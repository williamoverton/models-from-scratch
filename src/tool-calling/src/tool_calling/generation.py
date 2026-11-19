"""Sample two fixed, read-only continuations without executing a generated call."""

from threading import Event

from model_tokenizer import Tokenizer
from model_training.progress import TextGenerationExample, TextGenerationPreview
import torch

from .config import Config
from .framing import format_prefix, format_prompt
from .precision import autocast

SAMPLE_INTERVAL = 500
_SAMPLE_SEED = 42
_SAMPLE_TOKENS = 128
_SAMPLE_TEMPERATURE = 0.95
_SAMPLE = {
    "tools": [{
        "name": "lookup_api_endpoint",
        "description": "Look up a resource endpoint in the sample API registry.",
        "parameters": ["resource_name"],
    }],
    "messages": [
        {"role": "user", "content": "Look up the endpoint for the orders resource in the sample API."},
        {"role": "assistant", "tool_call": {"name": "lookup_api_endpoint", "arguments": ["orders"]}},
        {"role": "tool", "content": "orders: /v1/orders"},
    ],
}


def _sample_tokens(model, prefix: list[int], terminators: set[int], config: Config,
                   device: torch.device, stop_event: Event) -> list[int] | None:
    """Generate only within the remaining context and use a private, fixed RNG."""
    size = len(prefix)
    budget = min(_SAMPLE_TOKENS, config.context_length - size)
    if budget <= 0:
        return []
    ids = torch.empty((1, size + budget), dtype=torch.long, device=device)
    ids[0, :size] = torch.as_tensor(prefix, dtype=torch.long, device=device)
    generator = torch.Generator(device=device).manual_seed(_SAMPLE_SEED)
    generated = []
    for position in range(size, size + budget):
        if stop_event.is_set():
            return None
        with autocast():
            logits = model(ids[:, :position])[:, -1, :].float()
        if not torch.isfinite(logits).all().item():
            raise FloatingPointError("Non-finite logits while generating the fixed examples.")
        probabilities = torch.softmax(logits / _SAMPLE_TEMPERATURE, dim=-1)
        token = torch.multinomial(probabilities, 1, generator=generator)
        token_id = token.item()
        generated.append(token_id)
        if token_id in terminators:
            break
        ids[:, position:position + 1] = token
    return generated


@torch.no_grad()
def create_preview(model, tokenizer: Tokenizer, config: Config, device: torch.device,
                   step: int, stop_event: Event) -> TextGenerationPreview | None:
    """Publish both continuations together; the answer uses only the reference prefix."""
    if stop_event.is_set():
        return None
    prompt = format_prompt(tokenizer, _SAMPLE["messages"][0]["content"], _SAMPLE["tools"])
    reference = format_prefix(tokenizer, _SAMPLE)
    controls = tokenizer.control_token_ids
    terminators = {controls["<EXECUTE>"], controls["<END_OF_DOCUMENT>"]}
    was_training = model.training
    model.eval()
    try:
        examples = []
        for label, prefix in (
            ("Generated tool call", prompt),
            ("Generated answer from supplied reference result", reference),
        ):
            if stop_event.is_set():
                return None
            generated = _sample_tokens(model, prefix, terminators, config, device, stop_event)
            if generated is None or stop_event.is_set():
                return None
            context = tokenizer.decode(prefix)
            completion = (tokenizer.decode(generated) if generated
                          else "No room to generate within this bundle's context limit.")
            examples.append(TextGenerationExample(label, context, completion))
        if stop_event.is_set():
            return None
        return TextGenerationPreview(step, tuple(examples))
    finally:
        model.train(was_training)
