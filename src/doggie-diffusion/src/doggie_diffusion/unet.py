import torch
from torch import nn

from .attention import SpatialAttention
from .resampling import Downsample, Upsample
from .residual import ResidualBlock, ResidualStage
from .settings import ModelSettings
from .timestep import TimestepEmbedding


class UNet(nn.Module):
    """Predict RGB-channel noise using timestep-conditioned image features."""

    def __init__(self, settings: ModelSettings) -> None:
        """Build the encoder, bottleneck, and decoder from model settings."""
        super().__init__()

        channels = settings.feature_channels
        kernel_size = settings.convolution_kernel_size

        if len(channels) < 2:
            raise ValueError("The U-Net needs at least two channel levels.")
        if kernel_size < 1 or kernel_size % 2 == 0:
            raise ValueError("Processing kernel size must be positive and odd.")
        if not 0 <= settings.attention_level < len(channels) - 1:
            raise ValueError("Attention must select an encoder/decoder level.")
        if settings.residual_blocks_per_stage < 1:
            raise ValueError("Each stage needs at least one residual block.")

        padding = kernel_size // 2
        self.attention_level = settings.attention_level

        # Use independent attention weights at the matching encoder/decoder level.
        attention_channels = channels[self.attention_level]
        self.encoder_attention = SpatialAttention(
            attention_channels,
            heads=settings.attention_heads,
            normalization_groups=settings.normalization_groups,
        )
        self.decoder_attention = SpatialAttention(
            attention_channels,
            heads=settings.attention_heads,
            normalization_groups=settings.normalization_groups,
        )

        # Encode noise levels and convert RGB inputs into feature channels.
        self.timestep_embedding = TimestepEmbedding(settings)
        self.input_convolution = nn.Conv2d(
            3,
            channels[0],
            kernel_size=kernel_size,
            padding=padding,
            device="cuda",
        )

        # Keep encoder blocks explicit so each output can supply a skip.
        self.encoder_stages = nn.ModuleList()
        self.downsamples = nn.ModuleList()

        for level in range(len(channels) - 1):
            width = channels[level]
            self.encoder_stages.append(
                nn.ModuleList([
                    ResidualBlock(width, width, settings)
                    for _ in range(settings.residual_blocks_per_stage)
                ])
            )
            self.downsamples.append(
                Downsample(width, channels[level + 1], settings)
            )

        # Process features at the smallest spatial resolution.
        self.bottleneck = ResidualStage(
            channels[-1], channels[-1], settings
        )
        self.bottleneck_attention = SpatialAttention(
            channels[-1],
            heads=settings.attention_heads,
            normalization_groups=settings.normalization_groups,
        )

        # Build decoder stages from the deepest resolution to the shallowest.
        self.upsamples = nn.ModuleList()
        self.decoder_stages = nn.ModuleList()
        current_channels = channels[-1]

        for width in reversed(channels[:-1]):
            self.upsamples.append(Upsample(current_channels, settings))

            # Each decoder block consumes one same-resolution encoder skip.
            blocks = nn.ModuleList()
            for _ in range(settings.residual_blocks_per_stage):
                blocks.append(
                    ResidualBlock(current_channels + width, width, settings)
                )
                current_channels = width
            self.decoder_stages.append(blocks)

        # Predict three noise channels without restricting their value range.
        self.output_convolution = nn.Conv2d(
            channels[0],
            3,
            kernel_size=kernel_size,
            padding=padding,
            device="cuda",
        )

    def forward(
        self,
        noisy_images: torch.Tensor,
        timesteps: torch.Tensor,
    ) -> torch.Tensor:
        """Map CUDA images [B, 3, H, W] and timesteps [B] to predicted noise."""
        # Encode noise levels once and extract the initial image features.
        timestep_embedding = self.timestep_embedding(timesteps)
        features = self.input_convolution(noisy_images)

        # Save every encoder block output, including attention on the final block.
        encoder_features = []
        for level, (stage, downsample) in enumerate(zip(
            self.encoder_stages,
            self.downsamples,
            strict=True,
        )):
            for index, block in enumerate(stage):
                features = block(features, timestep_embedding)
                if level == self.attention_level and index == len(stage) - 1:
                    features = self.encoder_attention(features)
                encoder_features.append(features)
            features = downsample(features)

        # Process the smallest feature grids.
        features = self.bottleneck(features, timestep_embedding)
        features = self.bottleneck_attention(features)

        # Consume skips in reverse block order at each restored resolution.
        for index, (upsample, stage) in enumerate(zip(
            self.upsamples,
            self.decoder_stages,
            strict=True,
        )):
            features = upsample(features)
            for block in stage:
                skip = encoder_features.pop()
                features = torch.cat((features, skip), dim=1)
                features = block(features, timestep_embedding)
            level = len(self.decoder_stages) - 1 - index
            if level == self.attention_level:
                features = self.decoder_attention(features)

        # Convert the final features into RGB-channel noise estimates.
        return self.output_convolution(features)
