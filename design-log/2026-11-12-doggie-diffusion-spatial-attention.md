# Doggie Diffusion: spatial attention at 16×16

## Decision

Extend the [training baseline](2026-11-11-doggie-diffusion-training-baseline.md)
with separate spatial self-attention blocks after the encoder and decoder
residual stages at 16×16. Encoder skip features include the attention output.
Leave the 8×8 bottleneck unchanged.

Use PyTorch `nn.MultiheadAttention`, four heads, group normalization before
attention, and a residual addition afterward. With 256 channels, each head
uses 64 features. Flatten the spatial grid into a sequence of positions and
restore its original shape after attention.

Expose `attention_level=2` (zero-based resolution level, 16×16 for the current
64×64 input and stride-two downsampling) and `attention_heads=4` in model
settings. Keep the doubled channel widths, batch size 32, and other training
settings unchanged.

## Rationale and alternatives

Attention lets distant spatial positions exchange information directly.
16×16 retains more spatial detail than 8×8 and has fewer position pairs than
full-resolution attention. Attention at 8×8 or multiple resolutions remains
an experiment for later, not part of this change. More attention is not assumed
to improve quality without comparison.

## Checkpoints and verification

Move `trained-models/doggie-diffusion/` to
`trained-models/doggie-diffusion-no-attention/` to preserve the trained baseline.
The attention model starts fresh at the usual checkpoint path; do not add a
partial-loading compatibility path for the old weights.

The user will run and verify the new model. No runtime checks were performed
as part of this implementation.
