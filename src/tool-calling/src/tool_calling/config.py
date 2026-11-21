"""Settings for the hybrid convolution/attention tool-calling model."""

from dataclasses import dataclass
from typing import Literal


type BlockSpec = Literal["convolution", "global", "l2-norm"] | tuple[Literal["local"], int]


@dataclass(frozen=True)
class Loop:
    """Run one shared sequence of ordinary blocks for the given number of passes."""

    blocks: tuple[BlockSpec, ...]
    passes: int

    def __post_init__(self) -> None:
        """Reject empty cores and invalid pass counts."""
        if not self.blocks or type(self.passes) is not int or self.passes < 1:
            raise ValueError("A loop needs at least one block and a positive integer pass count.")


@dataclass(frozen=True)
class Config:
    """Shared settings for pretraining and tool training; context comes from the manifest."""

    context_length: int
    batch_size: int = 32
    embedding_dim: int = 768
    feed_forward_dim: int = 1536
    feed_forward_type: Literal["swiglu", "relu"] = "swiglu"
    swiglu_product_limit: float | None = 2048.0
    seed: int = 42
    block_schedule: tuple[BlockSpec | Loop, ...] = (
        "convolution", "global",
        Loop(
            blocks=(
                "convolution", ("local", 64), "convolution", "global",
                "convolution", ("local", 128), "convolution", "global",
            ),
            passes=2,
        ),
        "convolution", "global",
    )
    conv_kernel_size: int = 7
    num_heads: int = 12
    attention_head_gating: bool = True
    learning_rate: float = 0.001
    eval_interval: int = 100
    pretrain_peak_lr: float = 3e-4
    pretrain_final_lr: float = 3e-5
    pretrain_warmup_tokens: int = 4_000_000
    pretrain_token_budget: int = 200_000_000
    eval_batches: int = 10
    checkpoint_interval: int = 500
