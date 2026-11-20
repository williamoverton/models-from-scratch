"""Settings for the hybrid convolution/attention tool-calling model."""

from dataclasses import dataclass
from typing import Literal


type BlockSpec = Literal["convolution", "global"] | tuple[Literal["local"], int]


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
    embedding_dim: int = 512
    feed_forward_dim: int = 1024
    feed_forward_type: Literal["swiglu", "relu"] = "swiglu"
    seed: int = 42
    block_schedule: tuple[BlockSpec | Loop, ...] = (
        "global", "global",
        Loop(blocks=("convolution", ("local", 64), ("local", 128), "convolution", ("local", 64), "global"), passes=3),
        "global", "global",
    )
    conv_kernel_size: int = 7
    num_heads: int = 8
    attention_head_gating: bool = True
    learning_rate: float = 0.001
    eval_interval: int = 100
    eval_batches: int = 10
    checkpoint_interval: int = 500
