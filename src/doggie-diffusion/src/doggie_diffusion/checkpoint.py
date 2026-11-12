from pathlib import Path

import torch
from torch import nn
from torch.optim import Optimizer
from torch.optim.swa_utils import AveragedModel


def save_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: Optimizer,
    step: int,
    scaler: torch.amp.GradScaler,
    ema_model: AveragedModel,
) -> None:
    """Atomically save training state and EMA weights for generation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")

    try:
        # Finish writing the new checkpoint before replacing the previous save.
        torch.save(
            {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
                "scaler": scaler.state_dict(),
                "ema_model": ema_model.state_dict(),
            },
            temporary,
        )
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def load_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: Optimizer,
    scaler: torch.amp.GradScaler,
    ema_model: AveragedModel,
) -> int:
    """Restore a saved run, or return step zero when no checkpoint exists."""
    if not path.exists():
        ema_model.update_parameters(model)
        return 0

    # Restore the model and optimizer directly onto the training device.
    checkpoint = torch.load(path, map_location="cuda", weights_only=True)
    model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    # Runs saved before FP16 training start with a fresh gradient scaler.
    if "scaler" in checkpoint:
        scaler.load_state_dict(checkpoint["scaler"])
    # Seed EMA from learned weights when adopting it for an existing run.
    if "ema_model" in checkpoint:
        ema_model.load_state_dict(checkpoint["ema_model"])
    else:
        ema_model.update_parameters(model)
    return checkpoint["step"]
