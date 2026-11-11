import math

import torch
from torch import nn


class Diffusion(nn.Module):
    """Add training noise and generate images with a cosine DDPM process."""

    def __init__(self, noise_levels: int = 1_000) -> None:
        """Calculate the cosine schedule and reverse-step coefficients on CUDA."""
        super().__init__()

        if noise_levels < 2:
            raise ValueError("Diffusion needs at least two noise levels.")

        self.noise_levels = noise_levels

        # Define how the clean-image signal fades across the forward process.
        boundaries = torch.linspace(
            0, 1, noise_levels + 1, device="cuda"
        )
        cosine_offset = 0.008
        signal_curve = torch.cos(
            (boundaries + cosine_offset)
            / (1 + cosine_offset)
            * math.pi
            / 2
        ).square()
        signal_curve = signal_curve / signal_curve[0]

        # Convert cumulative signal levels into per-step noise variances.
        betas = 1 - signal_curve[1:] / signal_curve[:-1]
        betas = betas.clamp(max=0.999)
        alphas = 1 - betas
        cumulative_alphas = torch.cumprod(alphas, dim=0)
        previous_cumulative_alphas = torch.cat((
            torch.ones(1, device="cuda"),
            cumulative_alphas[:-1],
        ))

        # Store the two coefficients used to construct noisy training images.
        self.register_buffer(
            "signal_scale", cumulative_alphas.sqrt()
        )
        self.register_buffer(
            "noise_scale", (1 - cumulative_alphas).sqrt()
        )

        # Store coefficients for the reverse mean calculated from predicted noise.
        self.register_buffer(
            "reverse_scale", alphas.rsqrt()
        )
        self.register_buffer(
            "prediction_scale", betas / (1 - cumulative_alphas).sqrt()
        )

        # Use the schedule's fixed posterior variance for reverse-step sampling.
        posterior_variance = (
            betas
            * (1 - previous_cumulative_alphas)
            / (1 - cumulative_alphas)
        )
        self.register_buffer(
            "posterior_std", posterior_variance.sqrt()
        )

    def add_noise(
        self,
        clean_images: torch.Tensor,
        noise: torch.Tensor,
        timesteps: torch.Tensor,
    ) -> torch.Tensor:
        """Mix CUDA images and noise [B, 3, H, W] at timesteps shaped [B]."""
        # Broadcast each image's schedule coefficients across channels and pixels.
        signal_scale = self.signal_scale[timesteps][:, None, None, None]
        noise_scale = self.noise_scale[timesteps][:, None, None, None]

        return signal_scale * clean_images + noise_scale * noise

    @torch.inference_mode()
    def sample(
        self,
        model: nn.Module,
        batch_size: int,
        image_size: int,
        snapshot_steps: tuple[int, ...] = (100, 500, 1_000),
    ) -> dict[int, torch.Tensor]:
        """Return CUDA image snapshots keyed by completed reverse-step counts."""
        if any(
            step < 1 or step > self.noise_levels
            for step in snapshot_steps
        ):
            raise ValueError("Snapshot steps must be within the sampling run.")

        # Begin with independent Gaussian noise for every image.
        images = torch.randn(
            batch_size, 3, image_size, image_size, device="cuda"
        )
        snapshots = {}

        # Temporarily use evaluation behavior while generating previews.
        was_training = model.training
        model.eval()

        try:
            for timestep in reversed(range(self.noise_levels)):
                timesteps = torch.full(
                    (batch_size,),
                    timestep,
                    dtype=torch.long,
                    device="cuda",
                )

                # Predict the noise and calculate the reverse distribution's mean.
                predicted_noise = model(images, timesteps)
                mean = self.reverse_scale[timestep] * (
                    images
                    - self.prediction_scale[timestep] * predicted_noise
                )

                # Sample a possible predecessor; the final step adds no noise.
                if timestep > 0:
                    images = (
                        mean
                        + self.posterior_std[timestep]
                        * torch.randn_like(images)
                    )
                else:
                    images = mean

                # Retain intermediate images from this single generation.
                completed_steps = self.noise_levels - timestep
                if completed_steps in snapshot_steps:
                    snapshots[completed_steps] = images

        finally:
            model.train(was_training)

        return snapshots
