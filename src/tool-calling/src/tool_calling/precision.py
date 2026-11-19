"""Use CUDA FP16 autocast without converting the model weights."""

import torch


def autocast():
    """Run eligible CUDA operations in FP16 while keeping weights FP32."""
    return torch.autocast(device_type="cuda", dtype=torch.float16)
