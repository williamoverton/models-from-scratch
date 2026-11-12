import torch
from torch import nn


class SpatialAttention(nn.Module):
    """Let each spatial position gather features from the whole image."""

    def __init__(
        self,
        channels: int,
        *,
        heads: int,
        normalization_groups: int,
    ) -> None:
        """Build shape-preserving attention; channels must divide into heads."""
        super().__init__()

        self.normalization = nn.GroupNorm(
            normalization_groups, channels, device="cuda"
        )
        self.attention = nn.MultiheadAttention(
            embed_dim=channels,
            num_heads=heads,
            batch_first=True,
            device="cuda",
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        """Transform CUDA features [B, C, H, W] without changing their shape."""
        batch, channels, height, width = features.shape

        # Normalize features before calculating attention.
        normalized = self.normalization(features)

        # Treat each spatial position as one item in a sequence.
        positions = normalized.flatten(2).transpose(1, 2)

        # Learn queries, keys, and values from the same feature sequence.
        attended, _ = self.attention(
            positions, positions, positions, need_weights=False
        )

        # Restore the image grid and add the learned global correction.
        correction = attended.transpose(1, 2).reshape(
            batch, channels, height, width
        )
        return features + correction
