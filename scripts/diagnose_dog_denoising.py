"""Inspect a saved EMA model without updating weights or training state.

Run from the repository root in the project's CUDA environment:
    uv run --package doggie-diffusion python scripts/diagnose_dog_denoising.py

Writes one reconstruction/rollout grid per input image, pure-noise generations,
metrics.csv, and run.json in a diagnostics/ directory beside the checkpoint.
Checkpoints must match the current architecture; old stage-level-skip weights
cannot be loaded. Use --help for checkpoint, dataset, timestep, seed, and output.

Timesteps are zero-based schedule indices: t=50 takes 51 reverse updates.
Images use fixed rows from the first sorted shard, not a shuffled training batch.
All displayed images are clipped to [-1, 1]; reported errors are NOT clipped.
High-noise recovery is ambiguous, so pixel error alone is not a quality score.
"""

import argparse
import csv
import json
from pathlib import Path

import pyarrow.parquet as pq
import torch
from PIL import Image, ImageDraw
from torch.optim.swa_utils import AveragedModel

from doggie_diffusion.data import DogImageDataset
from doggie_diffusion.diffusion import Diffusion
from doggie_diffusion.settings import ModelSettings, TrainingSettings
from doggie_diffusion.training import CHECKPOINT_PATH
from doggie_diffusion.unet import UNet


def load_images(directory: Path, count: int) -> tuple[torch.Tensor, Path]:
    """Decode fixed rows using the training dataset's RGB normalization."""
    dataset = DogImageDataset(directory)
    shard = dataset.shards[0]
    batch = next(pq.ParquetFile(shard).iter_batches(batch_size=count, columns=["image"]))
    records = batch.column(0).to_pylist()
    if len(records) != count:
        raise ValueError(f"Requested {count} images, found only {len(records)} in {shard}")
    images = torch.stack([dataset._decode_image(row["bytes"]) for row in records])
    return images.to("cuda"), shard


def predict_clean(
    model: torch.nn.Module,
    diffusion: Diffusion,
    images: torch.Tensor,
    timestep: int,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return predicted noise and unclipped clean images [B, 3, H, W]."""
    timesteps = torch.full((len(images),), timestep, dtype=torch.long, device="cuda")
    with torch.autocast(device_type="cuda", dtype=torch.float16):
        predicted_noise = model(images, timesteps)
    predicted_noise = predicted_noise.float()
    clean = (
        images - diffusion.noise_scale[timestep] * predicted_noise
    ) / diffusion.signal_scale[timestep]
    return predicted_noise, clean


def reverse_rollout(
    model: torch.nn.Module,
    diffusion: Diffusion,
    images: torch.Tensor,
    start: int,
    generator: torch.Generator,
) -> torch.Tensor:
    """Apply the application's clipped-clean DDPM equations from start to zero."""
    for timestep in reversed(range(start + 1)):
        _, clean = predict_clean(model, diffusion, images, timestep)
        mean = (
            diffusion.clean_mean_scale[timestep] * clean.clamp(-1, 1)
            + diffusion.noisy_mean_scale[timestep] * images
        )
        images = mean
        if timestep > 0:
            images = images + diffusion.posterior_std[timestep] * torch.randn(
                images.shape, device="cuda", generator=generator
            )
    return images


def save_grid(
    path: Path,
    rows: list[list[torch.Tensor]],
    headings: list[str],
    labels: list[str],
) -> None:
    """Save labeled RGB tensors with nearest-neighbor enlargement for inspection."""
    tile = 192
    label_width = 80
    row_height = tile + 8
    canvas = Image.new(
        "RGB", (label_width + tile * len(headings), 32 + row_height * len(rows)), "#202020"
    )
    draw = ImageDraw.Draw(canvas)
    for column, heading in enumerate(headings):
        draw.text((label_width + column * tile + 4, 10), heading, fill="white")
    for row_index, (row, label) in enumerate(zip(rows, labels, strict=True)):
        y = 32 + row_index * row_height
        draw.text((4, y + 8), label, fill="white")
        for column, tensor in enumerate(row):
            pixels = ((tensor.detach().float().clamp(-1, 1) + 1) * 127.5).round()
            pixels = pixels.to(torch.uint8).permute(1, 2, 0).contiguous().cpu().numpy()
            image = Image.fromarray(pixels).resize((tile, tile), Image.Resampling.NEAREST)
            canvas.paste(image, (label_width + column * tile, y))
    canvas.save(path)


@torch.inference_mode()
def main() -> None:
    """Load one checkpoint snapshot and write reproducible denoising diagnostics."""
    settings = TrainingSettings()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT_PATH)
    parser.add_argument("--dataset", type=Path, default=settings.dataset_directory)
    parser.add_argument("--images", type=int, default=4)
    parser.add_argument("--timesteps", type=int, nargs="+", default=[50, 250, 500, 750, 900])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, help="New directory; existing paths are refused")
    args = parser.parse_args()
    if args.images < 1:
        parser.error("--images must be positive")
    if any(t < 0 or t >= settings.noise_levels for t in args.timesteps):
        parser.error(f"--timesteps must be between 0 and {settings.noise_levels - 1}")
    if not torch.cuda.is_available():
        parser.error("CUDA is required; no CPU fallback")

    # Load EMA strictly: do not silently diagnose the current training weights.
    checkpoint = torch.load(args.checkpoint, map_location="cuda", weights_only=True)
    model = AveragedModel(UNet(ModelSettings()))
    model.load_state_dict(checkpoint["ema_model"])
    step = checkpoint["step"]
    del checkpoint
    model = model.module.eval()
    diffusion = Diffusion(settings.noise_levels)
    clean, shard = load_images(args.dataset, args.images)
    if clean.shape[1:] != (3, settings.image_size, settings.image_size):
        raise ValueError(f"Expected RGB {settings.image_size}x{settings.image_size} images")
    output = args.output or args.checkpoint.parent / "diagnostics" / f"step-{step}-seed-{args.seed}"
    output.mkdir(parents=True, exist_ok=False)

    # Reuse each image's noise across levels; rollout randomness is separate.
    noise_generator = torch.Generator(device="cuda").manual_seed(args.seed)
    noise = torch.randn(clean.shape, device="cuda", generator=noise_generator)
    image_rows = [[] for _ in range(args.images)]
    metrics = []
    for timestep in args.timesteps:
        print(f"Checkpoint {step:,}: reconstructing and rolling out t={timestep}", flush=True)
        timesteps = torch.full((args.images,), timestep, device="cuda", dtype=torch.long)
        noisy = diffusion.add_noise(clean, noise, timesteps)
        predicted_noise, reconstructed = predict_clean(model, diffusion, noisy, timestep)
        generator = torch.Generator(device="cuda").manual_seed(args.seed + 1)
        recovered = reverse_rollout(model, diffusion, noisy, timestep, generator)
        for index in range(args.images):
            image_rows[index].append([
                clean[index].cpu(), noisy[index].cpu(),
                reconstructed[index].cpu(), recovered[index].cpu(),
            ])
            metrics.append({
                "image_row": index,
                "timestep": timestep,
                "noise_mse": (predicted_noise[index] - noise[index]).square().mean().item(),
                "clean_mse_unclipped": (reconstructed[index] - clean[index]).square().mean().item(),
                "clean_outside_range_fraction": (reconstructed[index].abs() > 1).float().mean().item(),
                "rollout_mse_unclipped": (recovered[index] - clean[index]).square().mean().item(),
            })

    # Ordinary generations use the application's sampler as a comparison.
    print("Generating comparison images from pure noise", flush=True)
    generator = torch.Generator(device="cuda").manual_seed(args.seed + 2)
    generated = diffusion.sample(
        model, args.images, settings.image_size,
        snapshot_steps=(settings.noise_levels,), generator=generator,
    )[settings.noise_levels]
    for index, rows in enumerate(image_rows):
        save_grid(
            output / f"image-{index}.png", rows,
            ["Original", "Noisy (display clipped)", "One-step clean estimate", "Reverse rollout"],
            [f"t={t}" for t in args.timesteps],
        )
    save_grid(
        output / "generations.png", [[image] for image in generated],
        ["Pure-noise generation"], [f"Sample {i}" for i in range(args.images)],
    )
    with (output / "metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(metrics[0]))
        writer.writeheader()
        writer.writerows(metrics)
    metadata = {
        "checkpoint": str(args.checkpoint.resolve()), "checkpoint_step": step,
        "weights": "EMA", "dataset_shard": str(shard.resolve()),
        "image_rows": list(range(args.images)), "timesteps": args.timesteps,
        "seed": args.seed, "rollout_seed": args.seed + 1, "generation_seed": args.seed + 2,
        "noise_levels": settings.noise_levels, "model_settings": vars(ModelSettings()),
        "precision": "FP16 autocast predictions, FP32 diffusion arithmetic; no compilation",
        "metrics": "MSE in model [-1,1] units before clipping; not a perceptual quality score",
    }
    (output / "run.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Saved grids, metrics.csv and run.json to {output.resolve()}")


if __name__ == "__main__":
    main()
