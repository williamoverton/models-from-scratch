from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ModelSettings:
    feature_channels: tuple[int, ...] = (64, 128, 256, 256)
    residual_blocks_per_stage: int = 2
    convolution_kernel_size: int = 3
    downsample_kernel_size: int = 3
    downsample_stride: int = 2
    downsample_padding: int = 1
    upsample_scale_factor: int = 2
    normalization_groups: int = 8
    timestep_encoding_width: int = 128
    timestep_conditioning_width: int = 128
    attention_level: int = 2
    attention_heads: int = 4


@dataclass(frozen=True)
class TrainingSettings:
    """Configure data loading, optimization, diffusion, and reporting intervals."""

    dataset_directory: Path = Path(
        "/mnt/StorageBox/datasets/SDIP_dog/64x64"
    )
    image_size: int = 64
    batch_size: int = 32
    learning_rate: float = 0.0002
    weight_decay: float = 0.0
    noise_levels: int = 1_000
    loading_workers: int = 0
    shuffle_buffer_size: int = 1_024
    read_batch_size: int = 128
    preview_interval: int = 1000
    checkpoint_interval: int = 1_000
