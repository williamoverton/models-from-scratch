from pathlib import Path
from threading import Event

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader

from model_training.progress import (
    ImageGenerationPreview,
    ProgressCallback,
    TrainingProgress,
)

from .checkpoint import load_checkpoint, save_checkpoint
from .data import DogImageDataset
from .diffusion import Diffusion
from .settings import ModelSettings, TrainingSettings
from .unet import UNet


CHECKPOINT_PATH = Path("trained-models/doggie-diffusion/checkpoint.pt")
PREVIEW_STEPS = (100, 500, 1_000)


def create_preview(
    model: UNet,
    diffusion: Diffusion,
    image_size: int,
    step: int,
) -> ImageGenerationPreview:
    """Generate one example and convert its three snapshots to display images."""
    snapshots = diffusion.sample(
        model,
        batch_size=1,
        image_size=image_size,
        snapshot_steps=PREVIEW_STEPS,
    )

    # Convert model-range RGB tensors to CPU byte arrays for Pillow.
    images = []
    for sampling_step in PREVIEW_STEPS:
        pixels = snapshots[sampling_step][0].clamp(-1, 1)
        pixels = ((pixels + 1) * 127.5).round().to(torch.uint8)
        pixels = pixels.permute(1, 2, 0).contiguous().cpu()
        images.append(Image.fromarray(pixels.numpy()))

    return ImageGenerationPreview(
        step=step,
        images=(images[0], images[1], images[2]),
        labels=(
            "After 100 denoising steps",
            "After 500 denoising steps",
            "After 1,000 denoising steps",
        ),
    )


def train(
    on_progress: ProgressCallback,
    stop_event: Event,
    *,
    model_settings: ModelSettings,
    settings: TrainingSettings,
) -> None:
    """Train continuously, report progress, and save before a normal stop."""
    model = UNet(model_settings)
    diffusion = Diffusion(settings.noise_levels)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=settings.learning_rate,
        weight_decay=settings.weight_decay,
    )

    # Resume learned parameters and optimizer state when a save exists.
    step = load_checkpoint(CHECKPOINT_PATH, model, optimizer)
    model.train()

    # Read and decode images in CPU workers without forking CUDA state.
    dataset = DogImageDataset(
        settings.dataset_directory,
        shuffle_buffer_size=settings.shuffle_buffer_size,
        read_batch_size=settings.read_batch_size,
    )
    loader = DataLoader(
        dataset,
        batch_size=settings.batch_size,
        num_workers=settings.loading_workers,
        pin_memory=True,
        persistent_workers=settings.loading_workers > 0,
        multiprocessing_context=(
            "spawn" if settings.loading_workers > 0 else None
        ),
    )

    # Make new passes through the dataset until the dashboard requests a stop.
    while not stop_event.is_set():
        for clean_images in loader:
            if stop_event.is_set():
                break

            clean_images = clean_images.to("cuda", non_blocking=True)

            # Choose an independent noise level and noise target for each image.
            timesteps = torch.randint(
                settings.noise_levels,
                (clean_images.shape[0],),
                device="cuda",
            )
            noise = torch.randn_like(clean_images)
            noisy_images = diffusion.add_noise(
                clean_images, noise, timesteps
            )

            # Predict the added noise and update the learned parameters.
            optimizer.zero_grad()
            predicted_noise = model(noisy_images, timesteps)
            loss = nn.functional.mse_loss(predicted_noise, noise)
            loss.backward()
            optimizer.step()
            step += 1

            # Save on its own schedule, independently of preview generation.
            if step % settings.checkpoint_interval == 0:
                save_checkpoint(CHECKPOINT_PATH, model, optimizer, step)

            # Let a requested stop skip starting another expensive preview.
            preview = None
            if (
                not stop_event.is_set()
                and step % settings.preview_interval == 0
            ):
                preview = create_preview(
                    model, diffusion, settings.image_size, step
                )

            # Publish the completed update and any newly generated example.
            on_progress(
                TrainingProgress(
                    step=step,
                    total_steps=None,
                    metrics={"loss": loss.item()},
                    preview=preview,
                )
            )

    # Preserve the latest completed update before Stop or Quit returns.
    save_checkpoint(CHECKPOINT_PATH, model, optimizer, step)
