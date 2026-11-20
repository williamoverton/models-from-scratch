"""Causal convolution and attention blocks for next-token prediction."""

import torch
from torch import nn
from torch.nn import functional as F
from flash_attn import flash_attn_func

from .config import BlockSpec, Config, Loop


class InputEmbeddings(nn.Module):
    """Add learned token and absolute position vectors."""

    def __init__(self, vocab_size: int, config: Config):
        super().__init__()
        self.context_length = config.context_length
        self.token_embedding = nn.Embedding(vocab_size, config.embedding_dim)
        self.position_embedding = nn.Embedding(config.context_length, config.embedding_dim)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        if token_ids.ndim != 2 or not 0 < token_ids.shape[1] <= self.context_length:
            raise ValueError("Expected [batch, time] token IDs within the context length.")
        positions = torch.arange(token_ids.shape[1], device=token_ids.device)
        return self.token_embedding(token_ids) + self.position_embedding(positions)


class CausalAttentionHead(nn.Module):
    """Project the full embedding into independent query, key, and value vectors."""

    def __init__(self, config: Config):
        super().__init__()
        dim = config.embedding_dim
        head_dim = dim // config.num_heads
        self.query = nn.Linear(dim, head_dim, bias=False)
        self.key = nn.Linear(dim, head_dim, bias=False)
        self.value = nn.Linear(dim, head_dim, bias=False)

    def forward(self, vectors: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.query(vectors), self.key(vectors), self.value(vectors)


class MultiHeadAttention(nn.Module):
    """Mix causal attention heads, with optional local windows and token-wise gates."""

    def __init__(self, config: Config, window: int | None = None):
        super().__init__()
        self.window = window
        self.heads = nn.ModuleList(CausalAttentionHead(config) for _ in range(config.num_heads))
        self.head_gate = (
            nn.Linear(config.embedding_dim, config.num_heads, bias=False)
            if config.attention_head_gating else None
        )
        self.output = nn.Linear(config.embedding_dim, config.embedding_dim)

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        # Stack directly in FlashAttention's [batch, time, heads, head_dim] layout.
        projected = [head(vectors) for head in self.heads]
        queries, keys, values = (torch.stack(items, dim=2) for items in zip(*projected))
        if self.window is not None:
            # The fork counts tokens to the left, excluding the current token.
            outputs = flash_attn_func(
                queries, keys, values, causal=True, window_size=(self.window - 1, 0)
            )
        else:
            outputs = F.scaled_dot_product_attention(
                queries.transpose(1, 2), keys.transpose(1, 2), values.transpose(1, 2),
                is_causal=True,
            ).transpose(1, 2)
        if self.head_gate is not None:
            outputs = outputs * torch.sigmoid(self.head_gate(vectors)).unsqueeze(-1)
        combined = outputs.flatten(2)
        return self.output(combined)


class GatedShortConvolution(nn.Module):
    """Mix recent tokens with a depthwise convolution and two learned gates."""

    def __init__(self, config: Config):
        super().__init__()
        dim = config.embedding_dim
        self.kernel_size = config.conv_kernel_size
        self.input_projection = nn.Linear(dim, 3 * dim)
        self.convolution = nn.Conv1d(dim, dim, self.kernel_size, groups=dim)
        self.output_projection = nn.Linear(dim, dim)

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        input_gate, values, output_gate = self.input_projection(vectors).chunk(3, dim=-1)
        gated_values = (input_gate * values).transpose(1, 2)
        # Only pad on the left: future tokens never enter the convolution.
        padded = F.pad(gated_values, (self.kernel_size - 1, 0))
        mixed = self.convolution(padded).transpose(1, 2)
        return self.output_projection(output_gate * mixed)


class SwiGLUFeedForward(nn.Module):
    """Gate features with a separate SiLU projection at each position."""

    def __init__(self, config: Config):
        super().__init__()
        self.gate_projection = nn.Linear(config.embedding_dim, config.feed_forward_dim)
        self.value_projection = nn.Linear(config.embedding_dim, config.feed_forward_dim)
        self.output_projection = nn.Linear(config.feed_forward_dim, config.embedding_dim)

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        gate = F.silu(self.gate_projection(vectors))
        return self.output_projection(gate * self.value_projection(vectors))


class TransformerBlock(nn.Module):
    """Apply separately normalized token mixing and feed-forward residual branches."""

    def __init__(self, config: Config, spec: BlockSpec):
        super().__init__()
        self.attention_norm = nn.LayerNorm(config.embedding_dim)
        match spec:
            case "convolution":
                self.mixer = GatedShortConvolution(config)
            case "global":
                self.mixer = MultiHeadAttention(config)
            case ("local", int(window)) if window > 0:
                self.mixer = MultiHeadAttention(config, window=window)
            case _:
                raise ValueError(f"Invalid block specification: {spec!r}")
        self.feed_forward_norm = nn.LayerNorm(config.embedding_dim)
        self.feed_forward = (
            SwiGLUFeedForward(config) if config.feed_forward_type == "swiglu"
            else nn.Sequential(
                nn.Linear(config.embedding_dim, config.feed_forward_dim),
                nn.ReLU(),
                nn.Linear(config.feed_forward_dim, config.embedding_dim),
            )
        )

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        vectors = vectors + self.mixer(self.attention_norm(vectors))
        return vectors + self.feed_forward(self.feed_forward_norm(vectors))


class LoopBlock(nn.Module):
    """Refine a fixed input with repeated passes through one learned core."""

    def __init__(self, config: Config, spec: Loop):
        super().__init__()
        self.core = nn.Sequential(*(TransformerBlock(config, block) for block in spec.blocks))
        self.passes = spec.passes
        self.reentry_norm = nn.LayerNorm(config.embedding_dim) if self.passes > 1 else None

    def forward(self, vectors: torch.Tensor) -> torch.Tensor:
        """Reinject the original [batch, time, width] state after the first pass."""
        state = self.core(vectors)
        if self.reentry_norm is not None:
            for _ in range(self.passes - 1):
                state = self.core(self.reentry_norm(state + vectors))
        return state


class LanguageModel(nn.Module):
    """Turn [batch, time] token IDs into [batch, time, vocabulary] logits."""

    def __init__(self, vocab_size: int, config: Config):
        super().__init__()
        if not config.num_heads or config.embedding_dim % config.num_heads != 0:
            raise ValueError("Embedding width must be divisible by the head count.")
        self.embeddings = InputEmbeddings(vocab_size, config)
        self.blocks = nn.ModuleList(
            LoopBlock(config, spec) if isinstance(spec, Loop) else TransformerBlock(config, spec)
            for spec in config.block_schedule
        )
        self.final_norm = nn.LayerNorm(config.embedding_dim)
        self.prediction = nn.Linear(config.embedding_dim, vocab_size)

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        vectors = self.embeddings(token_ids)
        for block in self.blocks:
            vectors = block(vectors)
        return self.prediction(self.final_norm(vectors))
