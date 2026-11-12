# Doggie Diffusion: wider U-Net and scale-and-offset conditioning

## Decision

Start a fresh model with feature channels `(96, 192, 384, 384)` at resolutions
64×64 → 32×32 → 16×16 → 8×8. Keep two residual blocks per stage, including the
bottleneck. Keep the independent encoder/decoder attention blocks at 16×16,
and add one spatial attention block after the bottleneck residual stage at
8×8. All attention blocks use the existing normalized residual
`nn.MultiheadAttention` implementation with four heads (96 features per head
at the 384-channel attention levels).

This extends the
[16×16 attention decision](2026-11-12-doggie-diffusion-spatial-attention.md)
and supersedes the additive conditioning from the
[network component decision](2026-11-11-doggie-diffusion-network-components.md).

## Residual conditioning

Each residual block projects the timestep embedding to twice its output-channel
count and splits the result into scale and offset. Apply these after the
second group normalization, before SiLU and the second convolution:

`conditioned = normalized * (1 + scale) + offset`

Broadcast scale and offset over height and width. Keep the first
normalization → SiLU → convolution and the channel-matching residual shortcut
unchanged. Keep timestep encoding and conditioning widths at 128. The old
additive offset before the second normalization is removed, not retained as
an alternative mode.

## Rationale and tradeoffs

The goal is better global coherence: wider features provide capacity,
bottleneck attention lets coarse regions interact directly, and scale-and-offset
conditioning gives noise levels more control over feature processing. None
of these guarantees coherent anatomy. Changing these together prioritizes a
stronger model experiment over isolating each contribution.

Keep 64×64 output, batch size 32, learning rate, AdamW, dataset, diffusion
schedule, FP16 gradient scaling, compiled execution, and EMA unchanged. Do not
add gradient clipping. Higher memory use and lower training throughput are
expected; whether batch size 32 fits has not yet been verified. Compare both
training steps and elapsed training time with the smaller model.

## Fresh-run checkpoint policy

The previous model was archived at
`trained-models/doggie-diffusion-12866947-params/`, including its samples and
step-93,481 checkpoint with EMA. Leave that archive untouched. The current
architecture starts at the existing default `trained-models/doggie-diffusion/`
path, which was empty after archiving. No weight or optimizer migration is
part of this change; strict loading is retained. This fresh-run choice is
specific to this experiment, not a blanket prohibition on future migrations.

## Verification

The user runs training and preview verification interactively. No tests or
runtime smoke checks were performed during implementation. GPU memory fit,
compiled forward/backward execution, throughput, and generated quality remain
to be checked by the user. Initial compilation and early noisy samples should
not be compared directly with the mature archived model.
