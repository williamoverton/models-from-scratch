import torch
from torch import nn

from .settings import ModelSettings


class Downsample(nn.Module):
    """Reduce spatial resolution while learning new feature channels."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        settings: ModelSettings,
    ) -> None:
        """Create a strided convolution using the configured kernel and padding."""
        super().__init__()

        self.convolution = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size=settings.downsample_kernel_size,
            stride=settings.downsample_stride,
            padding=settings.downsample_padding,
            device="cuda",
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Map [B, C_in, H, W] to [B, C_out, H/2, W/2] with default settings."""
        # Combine local features at fewer spatial positions.
        return self.convolution(features)


class Upsample(nn.Module):
    """Enlarge feature grids and refine them with a learned convolution."""

    def __init__(
        self,
        channels: int,
        settings: ModelSettings,
    ) -> None:
        """Create nearest-neighbor resizing followed by a spatial convolution."""
        super().__init__()

        kernel_size = settings.convolution_kernel_size
        if kernel_size < 1 or kernel_size % 2 == 0:
            raise ValueError("Processing kernel size must be positive and odd.")

        # Fixed nearest-neighbor resizing repeats feature values; it learns no weights.
        # At scale factor 2, each value becomes a 2×2 patch.
        self.resize = nn.Upsample(
            scale_factor=settings.upsample_scale_factor,
            mode="nearest",
        )
        self.convolution = nn.Conv2d(
            channels,
            channels,
            kernel_size=kernel_size,
            padding=kernel_size // 2,
            device="cuda",
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Map [B, C, H, W] to [B, C, 2H, 2W] with default settings."""
        # Repeat feature values onto a larger spatial grid.
        features = self.resize(features)

        # Learn local feature combinations without changing the enlarged shape.
        return self.convolution(features)
