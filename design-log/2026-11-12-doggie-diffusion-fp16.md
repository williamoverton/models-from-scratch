# Doggie Diffusion: FP16 mixed precision

## Decision

Replace the BF16 execution choice in the
[training baseline](2026-11-11-doggie-diffusion-training-baseline.md#bf16-and-compiled-execution-2026-11-12)
with CUDA FP16 autocast for training predictions/loss and generation predictions.
Keep compilation disabled while its environment prerequisites are repaired.

The RTX 2080 reports compute capability 7.5 and no native BF16 support.
The user observed approximately 5.95 steps/s with FP32 and 1.5 steps/s with
BF16. FP16 is supported by this GPU's Tensor Cores; actual throughput remains
to be measured by the user.

## Gradient scaling and persistence

Use `torch.amp.GradScaler("cuda")` to scale the loss before backward,
unscale/check gradients and conditionally step AdamW, then update the scale.
Stored parameters and optimizer state remain FP32. Reverse-diffusion arithmetic
stays FP32 through explicit conversion of model predictions. Generation does
not need a gradient scaler.

Save scaler state alongside the model, optimizer, and step. Existing checkpoints
without scaler state initialize a fresh scaler while retaining learned weights
and optimizer state. Subsequent saves preserve the scaler for resume.

The step counter continues counting training batches, including batches where
the scaler skips an optimizer update due to non-finite gradients. Throughput
therefore measures processed training steps, not guaranteed parameter updates.

## Verification

The user ran FP16 training and observed approximately 7.5 steps/s, compared
with the 5.95 steps/s FP32 baseline: about 26% higher training throughput,
or 21% less time for the same number of training steps. Generated images
appeared to retain the same quality in the user's visual comparison.
Checkpoint scaler-state resume has not been separately verified.

## Re-enable compilation in the Nix environment

After the user confirmed training runs in the project Nix development
environment, re-enable default-mode `model.compile()` after checkpoint loading
in training and standalone generation. This supersedes the temporary
compilation disablement above. Keep FP16 autocast, gradient scaling, checkpoint
format, and throughput measurement unchanged.

After setting `TRITON_LIBCUDA_PATH` to the host NVIDIA driver directory in the
Nix environment, the user observed compiled FP16 training at approximately
9.25 steps/s. This is about 23% higher throughput than FP16 alone (7.5 steps/s)
and 55% higher than the FP32 baseline (5.95 steps/s).
Initial compilation and preview overhead are excluded from this throughput
comparison. Compiled generation quality has not been separately reported.
