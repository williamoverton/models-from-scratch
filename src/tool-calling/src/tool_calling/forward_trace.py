"""Locate the first non-finite tensor in a failed forward pass."""

from contextlib import ExitStack
from logging import Logger

import torch
from torch.utils._pytree import tree_leaves
from torch.utils._python_dispatch import TorchDispatchMode

from .model import LoopBlock


def _peak(tensor: torch.Tensor) -> float:
    """Return the largest finite magnitude, or NaN if none exists."""
    finite = tensor[torch.isfinite(tensor)]
    return finite.abs().amax().item() if finite.numel() else float("nan")


class _ForwardTrace(TorchDispatchMode):
    """Check computed outputs, including functional operations between modules."""

    def __init__(self):
        super().__init__()
        self.modules: list[str] = []
        self.passes: dict[str, int] = {}

    def enter(self, name: str) -> None:
        """Record module nesting and count invocations of each shared core."""
        self.modules.append(name)
        if name in self.passes:
            self.passes[name] += 1

    def leave(self) -> None:
        """Return to the enclosing module after a successful forward."""
        self.modules.pop()

    def __torch_dispatch__(self, func, types, args=(), kwargs=None):
        kwargs = {} if kwargs is None else kwargs
        result = func(*args, **kwargs)
        operation = str(func)
        if operation.startswith(("aten.empty", "aten.new_empty", "aten.resize_")):
            return result  # Allocation output has not been initialized yet.
        # Fused attention also returns auxiliary buffers, including padded log-sum-exp.
        if operation in ("flash_attn._flash_attn_forward.default",
                         "aten._scaled_dot_product_efficient_attention.default"):
            outputs = (result[0],)
        else:
            outputs = tree_leaves(result)
        for tensor in outputs:
            if (isinstance(tensor, torch.Tensor) and tensor.is_floating_point() and tensor.numel()
                    and not torch.isfinite(tensor).all().item()):
                location = self.modules[-1] if self.modules else "loss"
                for core, count in self.passes.items():
                    if core in self.modules:
                        location += f" (loop pass {count})"
                    elif core.removesuffix(".core") in self.modules:
                        location += f" (re-entry to loop pass {count + 1})"
                peaks = [f"{x.dtype}: {_peak(x):g}" for x in tree_leaves((args, kwargs))
                         if isinstance(x, torch.Tensor) and x.is_floating_point() and x.numel()]
                raise FloatingPointError(
                    f"{location}: {operation} returned {tensor.dtype} {tuple(tensor.shape)} "
                    f"with {torch.isnan(tensor).sum().item()} NaN and {torch.isinf(tensor).sum().item()} inf; "
                    f"input finite peaks {peaks}; output finite peak {_peak(tensor):g}"
                )
        return result


def log_forward_failure(model: torch.nn.Module, replay, log: Logger) -> None:
    """Replay the failed batch without an optimizer update and log the first bad output."""
    trace = _ForwardTrace()
    try:
        with ExitStack() as cleanup:
            for name, module in model.named_modules():
                if isinstance(module, LoopBlock):
                    trace.passes[f"{name}.core"] = 0
                cleanup.callback(module.register_forward_pre_hook(
                    lambda _module, _inputs, name=name: trace.enter(name or "model")
                ).remove)
                cleanup.callback(module.register_forward_hook(
                    lambda _module, _inputs, _output: trace.leave()
                ).remove)
            with trace:
                loss = replay()
            log.warning("Forward trace did not locate a non-finite operation; replay loss=%s.", loss.item())
    except FloatingPointError as error:
        log.error("First non-finite forward output: %s", error)
    except Exception:
        log.exception("Could not trace the non-finite forward pass.")
