import math

import torch
from torch import nn

from .settings import ModelSettings


class TimestepEmbedding(nn.Module):
    """Encode noise timesteps and learn conditioning vectors for residual blocks."""

    def __init__(self, settings: ModelSettings) -> None:
        """Create fixed frequency buffers and learned projection layers on CUDA."""
        super().__init__()

        encoding_width = settings.timestep_encoding_width
        conditioning_width = settings.timestep_conditioning_width

        if encoding_width < 4 or encoding_width % 2 != 0:
            raise ValueError("Timestep encoding width must be even and at least 4.")

        half_width = encoding_width // 2
        frequencies = torch.exp(
            -math.log(10_000)
            * torch.arange(half_width, dtype=torch.float32, device="cuda")
            / (half_width - 1)
        )
        self.register_buffer("frequencies", frequencies)

        self.projection = nn.Sequential(
            nn.Linear(encoding_width, conditioning_width, device="cuda"),
            nn.SiLU(),
            nn.Linear(conditioning_width, conditioning_width, device="cuda"),
        )

    def forward(self, timesteps: torch.Tensor) -> torch.Tensor:
        """Map CUDA timesteps shaped [batch] to [batch, conditioning_width]."""
        angles = timesteps.to(dtype=self.frequencies.dtype)[:, None] * (
            self.frequencies[None, :]
        )
        encoding = torch.cat((angles.sin(), angles.cos()), dim=-1)
        return self.projection(encoding)
