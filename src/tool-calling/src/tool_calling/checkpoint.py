"""Load only current-project checkpoints and replace them atomically."""

from contextlib import contextmanager
from dataclasses import asdict
import fcntl
import os
from pathlib import Path
import stat
from tempfile import NamedTemporaryFile

import torch

from .batching import TokenBatcher
from .config import Config

CHECKPOINT_NAME = "checkpoint.pt"
_FORMAT = "llm-from-scratch/tool-calling-checkpoint"
_VERSION = 2


@contextmanager
def lock_run(directory: Path):
    """Prevent cooperating dashboard processes from training into the same directory."""
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError(f"Another training worker is using run directory {directory}.") from error
        yield
    finally:
        os.close(fd)


def resume_settings(settings: dict) -> dict:
    """Keep tool-training settings that affect optimizer updates."""
    return {
        name: value for name, value in settings.items()
        if name not in ("eval_interval", "eval_batches", "checkpoint_interval")
        and not name.startswith("pretrain_")
    }


def _floating_tensors(value, path):
    if isinstance(value, torch.Tensor) and (value.is_floating_point() or value.is_complex()):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from _floating_tensors(child, f"{path}.{key}")
    elif isinstance(value, (tuple, list)):
        for index, child in enumerate(value):
            yield from _floating_tensors(child, f"{path}[{index}]")


def _check_finite(state: dict) -> None:
    checks = {}
    for section in ("model", "optimizer"):
        for name, tensor in _floating_tensors(state[section], section):
            checks.setdefault(tensor.device, []).append((name, torch.isfinite(tensor).all()))
    for values in checks.values():
        if not torch.stack([finite for _, finite in values]).all().item():
            bad = [name for name, finite in values if not finite.item()]
            raise FloatingPointError(f"Non-finite checkpoint state: {', '.join(bad)}.")


def read_checkpoint(path: Path, config: Config, manifest_digest: str) -> dict | None:
    """Treat a missing file as fresh, never a present but unusable one."""
    try:
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(mode):
            raise ValueError("Expected a regular checkpoint file, not a directory or symlink.")
        state = torch.load(path, map_location="cpu", weights_only=True)
        if (not isinstance(state, dict) or state.get("format") != _FORMAT
                or type(state.get("version")) is not int or state["version"] != _VERSION):
            raise ValueError("Unsupported checkpoint format; expected a CUDA FP16/Adam checkpoint.")
        if state["manifest_sha256"] != manifest_digest:
            raise ValueError("Prepared bundle differs from the one used by this checkpoint.")
        expected = resume_settings(asdict(config))
        saved = state["settings"]
        if saved != expected:
            changed = sorted(key for key in saved.keys() | expected.keys()
                             if saved.get(key) != expected.get(key))
            raise ValueError(f"Checkpoint settings differ: {', '.join(changed)}.")
        step = state["step"]
        if type(step) is not int or step < 1:
            raise ValueError("Invalid completed step in checkpoint.")
        _check_finite(state)
        return state
    except Exception as error:
        raise ValueError(f"Cannot resume {path}: {error} For a fresh start, use another --run-dir.") from error


def restore_checkpoint(path: Path, state: dict, model: torch.nn.Module, optimizer: torch.optim.Adam,
                       scaler: torch.amp.GradScaler, batcher: TokenBatcher, device: torch.device) -> None:
    """Restore update and RNG state before training can replace the checkpoint."""
    try:
        model.load_state_dict(state["model"])
        optimizer.load_state_dict(state["optimizer"])
        scaler.load_state_dict(state["scaler"])
        batcher.generator.set_state(state["batch_rng"])
        torch.set_rng_state(state["cpu_rng"])
        torch.cuda.set_rng_state(state["cuda_rng"], device)
    except Exception as error:
        raise ValueError(f"Cannot restore training state from {path}: {error}") from error


def save_checkpoint(path: Path, model: torch.nn.Module, optimizer: torch.optim.Adam,
                    scaler: torch.amp.GradScaler, batcher: TokenBatcher, config: Config,
                    step: int, manifest_digest: str, device: torch.device) -> None:
    """Publish the latest completed state only after validation and a full write."""
    state = {
        "format": _FORMAT,
        "version": _VERSION,
        "step": step,
        "settings": resume_settings(asdict(config)),
        "manifest_sha256": manifest_digest,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "scaler": scaler.state_dict(),
        "batch_rng": batcher.generator.get_state(),
        "cpu_rng": torch.get_rng_state(),
        "cuda_rng": torch.cuda.get_rng_state(device),
    }
    _check_finite(state)
    temp_path = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as output:
            temp_path = Path(output.name)
            torch.save(state, output)
        temp_path.replace(path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
