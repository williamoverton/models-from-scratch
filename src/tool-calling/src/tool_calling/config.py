"""Settings for the hybrid convolution/attention tool-calling model."""

from dataclasses import dataclass
from typing import Literal


DEFAULT_STEPS = 100_000


@dataclass(frozen=True)
class Config:
    """Model context comes exclusively from the prepared data manifest."""

    context_length: int
    training_steps: int = DEFAULT_STEPS
    batch_size: int = 16
    embedding_dim: int = 512
    feed_forward_dim: int = 1024
    feed_forward_type: Literal["swiglu", "relu"] = "swiglu"
    seed: int = 42
    block_types: tuple[str, ...] = (
        "convolution",
        "convolution", "global", "convolution", "local",
        "convolution", "local", "convolution", "local",
        "convolution", "local", "convolution", "local",
        "convolution", "global", "convolution",
    )
    local_window: int = 32
    conv_kernel_size: int = 7
    num_heads: int = 8
    attention_head_gating: bool = True
    learning_rate: float = 0.001
    eval_interval: int = 100
    eval_batches: int = 10
    checkpoint_interval: int = 500
