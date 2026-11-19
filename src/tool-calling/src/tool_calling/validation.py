"""Measure held-out assistant loss and free-running greedy tool-name accuracy."""

from collections import defaultdict
from threading import Event

from model_tokenizer import Tokenizer
import torch
from torch.nn import functional as F
from torch.nn.utils.rnn import pad_sequence

from .batching import IGNORE_TARGET, Record, pack_batch
from .config import Config
from .precision import autocast


def token_losses(logits: torch.Tensor, targets: torch.Tensor, reduction: str) -> torch.Tensor:
    """Cross-entropy over shifted assistant targets, not context or padding."""
    return F.cross_entropy(logits.flatten(0, 1), targets.flatten(),
                           ignore_index=IGNORE_TARGET, reduction=reduction)


def stage_masks(targets: torch.Tensor, tokenizer: Tokenizer) -> dict[str, torch.Tensor]:
    """Partition supervised targets by call, name, arguments, and answer."""
    control = tokenizer.control_token_ids
    call_start = targets == control["<TOOL_CALL>"]
    call_end = targets == control["<EXECUTE>"]
    answer_start = targets == control["<ASSISTANT>"]
    answer_end = targets == control["<END_OF_DOCUMENT>"]
    call = (call_start.cumsum(1) - call_end.cumsum(1) + call_end) > 0
    answer = (answer_start.cumsum(1) - answer_end.cumsum(1) + answer_end) > 0
    supervised = targets != IGNORE_TARGET

    positions = torch.arange(1, targets.shape[1] + 1, device=targets.device)
    name_boundary = torch.where(call_start, positions, 0).cummax(1).values
    argument_boundary = torch.where(
        (targets == control["<DELIMETER>"]) | call_end, positions, 0
    ).cummax(1).values
    name = call & ~call_start & (name_boundary > argument_boundary)
    return {"call": call & supervised, "name": name & supervised,
            "arguments": call & ~call_start & ~name & supervised, "answer": answer & supervised}


def _evenly_spaced(records: list, count: int) -> list:
    """Select the midpoint of each equal-width interval of the original order."""
    return [records[(2 * i + 1) * len(records) // (2 * count)] for i in range(count)]


def _balanced_sample(groups: dict, budget: int) -> list[Record]:
    names = sorted(groups)
    budget = min(sum(map(len, groups.values())), max(budget, len(names)))
    counts = dict.fromkeys(names, 0)
    while budget:
        for name in names:
            if counts[name] < len(groups[name]):
                counts[name] += 1
                budget -= 1
                if not budget:
                    break
    return [record for name in names for record in _evenly_spaced(groups[name], counts[name])]


def _reference(record: Record, call: int, terminators: set[int], tokenizer: Tokenizer):
    """Find the first supervised call with a nonempty ordinary-byte tool name."""
    tokens = record.tokens.tolist()
    if call not in tokens:
        return None
    mask = record.mask.tolist()
    for start, token in enumerate(tokens):
        if token != call or start == 0 or not mask[start]:
            continue
        end = start + 1
        while end < len(tokens) and tokens[end] in tokenizer.vocabulary and mask[end]:
            end += 1
        if end > start + 1 and end < len(tokens) and mask[end] and tokens[end] in terminators:
            expected = b"".join(tokenizer.vocabulary[token] for token in tokens[start + 1:end])
            return tokens[:start], expected
    return None


class Validation:
    """Compute diagnostics on fixed sets from the bound validation split."""

    def __init__(self, records: list[Record], tokenizer: Tokenizer, config: Config, stop_event: Event):
        self.tokenizer = tokenizer
        self.config = config
        control = tokenizer.control_token_ids
        self.call_id = control["<TOOL_CALL>"]
        self.terminators = {control["<DELIMETER>"], control["<EXECUTE>"]}
        groups = defaultdict(list)
        references = defaultdict(list)
        for record in records:
            if stop_event.is_set():
                break
            groups[record.schema_id].append(record)
            reference = _reference(record, self.call_id, self.terminators, tokenizer)
            if reference is not None:
                references[record.schema_id].append(reference)
        self.records = _balanced_sample(groups, config.eval_batches * config.batch_size)
        self.references = [reference for schema in sorted(references)
                           for reference in _evenly_spaced(references[schema], min(5, len(references[schema])))]

    def _tool_name_accuracy(self, model, device, stop_event):
        correct = 0
        for offset in range(0, len(self.references), self.config.batch_size):
            active = [(prefix.copy(), expected, b"", False)
                      for prefix, expected in self.references[offset:offset + self.config.batch_size]]
            while active:
                if stop_event.is_set():
                    return None
                active = [item for item in active if len(item[0]) <= self.config.context_length]
                if not active:
                    break
                lengths = torch.tensor([len(item[0]) for item in active], device=device)
                # Right padding cannot affect the preceding, real causal positions.
                inputs = pad_sequence([torch.tensor(item[0], device=device) for item in active],
                                      batch_first=True)
                with autocast():
                    logits = model(inputs)[torch.arange(len(active), device=device), lengths - 1]
                if not torch.isfinite(logits).all().item():
                    raise FloatingPointError("Non-finite logits during greedy tool-name validation.")
                following = []
                for (prefix, expected, emitted, started), token in zip(active, logits.argmax(-1).tolist()):
                    if not started:
                        if token == self.call_id:
                            prefix.append(token)
                            following.append((prefix, expected, emitted, True))
                    elif token in self.terminators:
                        correct += emitted == expected
                    elif token in self.tokenizer.vocabulary:
                        emitted += self.tokenizer.vocabulary[token]
                        if expected.startswith(emitted):
                            prefix.append(token)
                            following.append((prefix, expected, emitted, True))
                active = following
        return correct, len(self.references)

    @torch.no_grad()
    def evaluate(self, model, device: torch.device, stop_event: Event):
        """Return token-weighted loss breakdowns and greedy counts, or no partial report."""
        was_training = model.training
        model.eval()
        try:
            stages = defaultdict(lambda: [0.0, 0])
            schemas = defaultdict(lambda: [0.0, 0, 0])
            for offset in range(0, len(self.records), self.config.batch_size):
                if stop_event.is_set():
                    return None
                records = self.records[offset:offset + self.config.batch_size]
                inputs, targets = pack_batch(records, device)
                with autocast():
                    losses = token_losses(model(inputs), targets, "none").reshape_as(targets)
                finite_rows = torch.isfinite(losses).all(dim=1)
                if not finite_rows.all().item():
                    invalid = sorted({record.schema_id for record, finite
                                      in zip(records, finite_rows.tolist()) if not finite})
                    raise FloatingPointError(f"Non-finite validation loss in schemas: {', '.join(invalid)}.")
                supervised = targets != IGNORE_TARGET
                for name, mask in {"overall": supervised, **stage_masks(targets, self.tokenizer)}.items():
                    stages[name][0] += losses.masked_fill(~mask, 0).sum().item()
                    stages[name][1] += mask.sum().item()
                for record, total, count in zip(records, losses.sum(1).tolist(), supervised.sum(1).tolist()):
                    stats = schemas[record.schema_id]
                    stats[0] += total
                    stats[1] += count
                    stats[2] += 1
            accuracy = self._tool_name_accuracy(model, device, stop_event)
            if accuracy is None or stop_event.is_set():
                return None
            return stages, schemas, accuracy
        finally:
            model.train(was_training)
