from collections import deque
from pathlib import Path
from threading import Event
from time import perf_counter

import torch
from PIL import Image
from torch import nn
from torch.utils.data import DataLoader

from model_training.progress import (
    ImageGenerationPreview,
    ImageGenerationRow,
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
PREVIEW_SEED = 42


def create_preview(
    model: UNet,
    diffusion: Diffusion,
    image_size: int,
    step: int,
    *,
    save_sample: bool,
) -> ImageGenerationPreview:
    """Generate fixed and random rows; optionally save only the fixed result."""
    rows = []
    for seed in (PREVIEW_SEED, None):
        # Keep both preview streams separate from training randomness.
        generator = torch.Generator(device="cuda")
        actual_seed = generator.seed() if seed is None else seed
        generator.manual_seed(actual_seed)
        snapshots = diffusion.sample(
            model,
            batch_size=1,
            image_size=image_size,
            snapshot_steps=PREVIEW_STEPS,
            generator=generator,
        )

        # Convert model-range RGB tensors to CPU byte arrays for Pillow.
        images = []
        for sampling_step in PREVIEW_STEPS:
            pixels = snapshots[sampling_step][0].clamp(-1, 1)
            pixels = ((pixels + 1) * 127.5).round().to(torch.uint8)
            pixels = pixels.permute(1, 2, 0).contiguous().cpu()
            images.append(Image.fromarray(pixels.numpy()))

        if save_sample and seed is not None:
            samples_directory = CHECKPOINT_PATH.parent / "samples"
            samples_directory.mkdir(parents=True, exist_ok=True)
            images[-1].save(samples_directory / f"generation-sample-{step}.png")

        rows.append(ImageGenerationRow(
            title=f"{'Fixed' if seed is not None else 'Random'} seed: {actual_seed}",
            images=(images[0], images[1], images[2]),
            labels=(
                "After 100 denoising steps",
                "After 500 denoising steps",
                "After 1,000 denoising steps",
            ),
        ))

    return ImageGenerationPreview(step=step, rows=(rows[0], rows[1]))


def train(
    on_progress: ProgressCallback,
    stop_event: Event,
    *,
    model_settings: ModelSettings,
    settings: TrainingSettings,
    generation_request: Event,
) -> None:
    """Train continuously, report progress, and save before a normal stop."""
    model = UNet(model_settings)
    diffusion = Diffusion(settings.noise_levels)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=settings.learning_rate,
        weight_decay=settings.weight_decay,
    )
    scaler = torch.amp.GradScaler("cuda")

    # Resume learned parameters and optimizer state when a save exists.
    step = load_checkpoint(CHECKPOINT_PATH, model, optimizer, scaler)
    model.train()
    # Compile execution in place so checkpoint parameter names stay unchanged.
    model.compile()

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

    step_durations: deque[float] = deque(maxlen=50)
    step_started = perf_counter()

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
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                predicted_noise = model(noisy_images, timesteps)
                loss = nn.functional.mse_loss(predicted_noise, noise)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            step += 1

            # Wait for GPU completion before measuring loading and training time.
            torch.cuda.synchronize()
            step_durations.append(perf_counter() - step_started)
            steps_per_second = len(step_durations) / sum(step_durations)

            # Save on its own schedule, independently of preview generation.
            if step % settings.checkpoint_interval == 0:
                save_checkpoint(CHECKPOINT_PATH, model, optimizer, step, scaler)

            # A scheduled preview also satisfies any pending manual request.
            preview = None
            scheduled = step % settings.preview_interval == 0
            if not stop_event.is_set() and (scheduled or generation_request.is_set()):
                generation_request.clear()
                preview = create_preview(
                    model, diffusion, settings.image_size, step,
                    save_sample=scheduled,
                )

            # Publish the completed update and any newly generated example.
            on_progress(
                TrainingProgress(
                    step=step,
                    total_steps=None,
                    metrics={
                        "loss": loss.item(),
                        "training steps/s": steps_per_second,
                    },
                    preview=preview,
                )
            )
            # Exclude saving, generation, and reporting from the next step.
            step_started = perf_counter()

    # Preserve the latest completed update before Stop or Quit returns.
    save_checkpoint(CHECKPOINT_PATH, model, optimizer, step, scaler)


def generate_from_checkpoint() -> ImageGenerationPreview:
    """Generate display-only rows from saved weights without starting training."""
    if not CHECKPOINT_PATH.exists():
        raise FileNotFoundError("No checkpoint yet; start training before generating.")
    model = UNet(ModelSettings())
    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cuda", weights_only=True)
    model.load_state_dict(checkpoint["model"])
    step = checkpoint["step"]
    del checkpoint
    model.compile()
    settings = TrainingSettings()
    diffusion = Diffusion(settings.noise_levels)
    return create_preview(
        model, diffusion, settings.image_size, step, save_sample=False
    )
