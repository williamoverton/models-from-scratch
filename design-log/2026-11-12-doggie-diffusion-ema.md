# Doggie Diffusion: EMA generation comparison

## Decision

Keep the current architecture, AdamW, FP16 gradient scaling, and compiled model
execution. Add an exponential moving average (EMA) of model parameters for
sampling, using PyTorch `AveragedModel` and `get_ema_multi_avg_fn(0.999)`.
This follows the [FP16 execution decision](2026-11-12-doggie-diffusion-fp16.md).

Seed the EMA from current learned weights when adopting it for an existing
checkpoint, or from the initial model for a fresh run. The initial copy counts
as the averaging seed, so the next successful update applies the decay rather
than replacing that seed. Update EMA only after successful optimizer updates:
a decreased gradient scale indicates an overflow-skipped update.

Save EMA parameters and its averaging counter alongside model, optimizer,
gradient scaler, and step. Resume that state when present. Checkpoints created
before EMA initialize it from their ordinary model weights; no training restart
or checkpoint deletion is required. Keep EMA stored in FP32 on CUDA.

## Preview comparison

Replace the fixed/random preview pair with current/EMA rows using the same
fixed seed (42), including identical initial noise and reverse-step random
noise. Both scheduled/manual training previews and idle generation show the
comparison. Save only the final EMA image at the existing scheduled sample path.
Existing saved images are not rewritten; older samples used ordinary weights.
Compile both model instances in place, preserving checkpoint parameter names.

This keeps two generation runs per preview, rather than adding a third run.
The tradeoff is losing the random-seed diversity row during this experiment.
The EMA adds a model-sized FP32 copy and parameter-update work, but no extra
training forward/backward pass. Throughput timing includes EMA update work.

## Rationale and verification

The immediate goal is more coherent samples. EMA may reduce short-term weight
fluctuations but is not an anatomy-specific improvement or a guarantee of
better coherence. Hold the architecture and optimizer fixed so same-seed rows
isolate the sampling-weight choice. At decay 0.999, the initial seed's influence
falls to about 37% after 1,000 successful updates and 5% after 3,000.

The user runs training and visual verification interactively. Check initially
matching rows, divergence after further training, throughput, and save/resume
of the comparison. No runtime verification was performed during implementation.
