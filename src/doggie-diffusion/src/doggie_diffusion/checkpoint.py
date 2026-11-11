from pathlib import Path

import torch
from torch import nn
from torch.optim import Optimizer


def save_checkpoint(
    path: Path,
    model: nn.Module,
    optimizer: Optimizer,
    step: int,
) -> None:
    """Atomically save learned parameters, optimizer state, and completed step."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")

    try:
        # Finish writing the new checkpoint before replacing the previous save.
        torch.save(
            {
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "step": step,
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
) -> int:
    """Restore a saved run, or return step zero when no checkpoint exists."""
    if not path.exists():
        return 0

    # Restore the model and optimizer directly onto the training device.
    checkpoint = torch.load(path, map_location="cuda", weights_only=True)
    model.load_state_dict(checkpoint["model"])
    optimizer.load_state_dict(checkpoint["optimizer"])
    return checkpoint["step"]
