"""Settings for the hybrid convolution/attention tool-calling model."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class PretrainConfig:
    """Launch settings for pretraining from the workspace root."""

    data_dir: Path = Path("/mnt/StorageBox/datasets/pretrain-wiki-qa-8k-ctx1024")
    run_dir: Path = Path("trained-models/tool-calling/runs/pretrain-wiki-qa-8k-2loops")
    init_from: Path | None = None
    sample_prompt: str = "Training an LLM is"
    verify_shards: bool = False
    headless: bool = False
    step_delay_seconds: float = 0.0


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
    """Shared model and training settings for pretraining and tool training."""

    context_length: int = 800
    batch_size: int = 6
    embedding_dim: int = 512
    feed_forward_dim: int = 512*2
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
    num_heads: int = 8
    attention_head_gating: bool = True
    learning_rate: float = 0.001
    pretrain_peak_lr: float = 3e-4
    pretrain_final_lr: float = 3e-5
    pretrain_warmup_tokens: int = 4_000_000
    pretrain_decay_end_tokens: int = 200_000_000
    eval_interval: int = 100
    eval_batches: int = 10
    checkpoint_interval: int = 200

    def __post_init__(self) -> None:
        """Require a positive number of input positions."""
        if type(self.context_length) is not int or self.context_length < 1:
            raise ValueError("Config.context_length must be a positive integer.")
