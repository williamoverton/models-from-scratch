import torch
from torch import nn

from .settings import ModelSettings


class ResidualBlock(nn.Module):
    """Learn a timestep-conditioned feature correction and add a shortcut."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        settings: ModelSettings,
    ) -> None:
        """Build shape-preserving processing and a channel-matching shortcut."""
        super().__init__()

        # Preserve spatial dimensions through the processing convolutions.
        kernel_size = settings.convolution_kernel_size
        if kernel_size < 1 or kernel_size % 2 == 0:
            raise ValueError("Processing kernel size must be positive and odd.")

        padding = kernel_size // 2

        # Normalize and transform the input into output-channel features.
        self.input_layers = nn.Sequential(
            nn.GroupNorm(
                settings.normalization_groups, in_channels, device="cuda"
            ),
            nn.SiLU(),
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size,
                padding=padding,
                device="cuda",
            ),
        )

        # Convert the shared timestep embedding into one offset per output channel.
        self.timestep_projection = nn.Sequential(
            nn.SiLU(),
            nn.Linear(
                settings.timestep_conditioning_width,
                out_channels,
                device="cuda",
            ),
        )

        # Process the conditioned features into a learned correction.
        self.output_layers = nn.Sequential(
            nn.GroupNorm(
                settings.normalization_groups, out_channels, device="cuda"
            ),
            nn.SiLU(),
            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size,
                padding=padding,
                device="cuda",
            ),
        )

        # Match shortcut channels when the input and output widths differ.
        self.shortcut = (
            nn.Identity()
            if in_channels == out_channels
            else nn.Conv2d(
                in_channels, out_channels, kernel_size=1, device="cuda"
            )
        )

    def forward(
        self,
        features: torch.Tensor,
        timestep_embedding: torch.Tensor,
    ) -> torch.Tensor:
        """Map [B, C_in, H, W] and [B, conditioning_width] to [B, C_out, H, W]."""
        # Extract features before adding noise-level information.
        correction = self.input_layers(features)

        # Broadcast each timestep-derived channel offset across its spatial grid.
        conditioning = self.timestep_projection(timestep_embedding)
        correction = correction + conditioning[:, :, None, None]

        # Turn the conditioned features into the residual correction.
        correction = self.output_layers(correction)

        # Add the correction to the channel-matched input.
        return self.shortcut(features) + correction


class ResidualStage(nn.Module):
    """Run residual blocks with shared timestep conditioning."""

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        settings: ModelSettings,
    ) -> None:
        """Change channels in the first block, then refine at the same width."""
        super().__init__()

        if settings.residual_blocks_per_stage < 1:
            raise ValueError("Each stage needs at least one residual block.")

        # Only the first block needs to handle a change in channel count.
        self.blocks = nn.ModuleList([
            ResidualBlock(
                in_channels if index == 0 else out_channels,
                out_channels,
                settings,
            )
            for index in range(settings.residual_blocks_per_stage)
        ])

    def forward(
        self,
        features: torch.Tensor,
        timestep_embedding: torch.Tensor,
    ) -> torch.Tensor:
        """Transform [B, C_in, H, W] into [B, C_out, H, W]."""
        # Apply each block using the same noise-level conditioning.
        for block in self.blocks:
            features = block(features, timestep_embedding)
        return features
