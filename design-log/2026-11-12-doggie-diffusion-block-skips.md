# Doggie Diffusion: block-level encoder–decoder skips

## Decision

Replace one encoder–decoder skip per resolution with one per encoder residual
block. This supersedes the stage-level skip layout in the
[implementation baseline](2026-11-11-doggie-diffusion-training-baseline.md)
and extends the [wider U-Net decision](2026-11-12-doggie-diffusion-larger-unet.md).
DDPM means Denoising Diffusion Probabilistic Model.

With the current two blocks at each encoder resolution (64×64, 32×32, 16×16),
retain six encoder outputs rather than three. Consume them in reverse order:
each decoder block concatenates one skip before processing. Encoder and decoder
stages expose their residual blocks as nested ModuleLists; the bottleneck keeps
its existing ResidualStage. The number of residual blocks is unchanged.

Keep stage widths `(96, 192, 384, 384)`, scale-and-offset timestep conditioning,
resampling, and attention placement unchanged. Encoder attention still follows
the final block at its selected resolution, and that attended output supplies
the final skip there. Decoder attention still follows its complete stage.
Do not add skips from the input convolution, downsampling operations, or
bottleneck: this adopts block-level DDPM-style skips, not a complete replica
of a particular reference DDPM U-Net.

## Rationale and tradeoffs

Expose multiple intermediate encoder representations to the decoder rather
than only each stage's final representation. This is a conventional diffusion
U-Net pattern, not a fix for a demonstrated correctness defect or a guarantee
of improved anatomy. Retaining extra feature maps and widening decoder inputs
increases activation memory and parameter count; training speed and image
quality must be compared at runtime. Leave optimization and diffusion unchanged
to keep the architecture change focused.

## Fresh-run storage

Use `trained-models/doggie-diffusion-dense-skips/checkpoint.pt` for training,
generation, and the diagnostic script's default. Samples and diagnostics remain
relative to that checkpoint directory. Leave the previous
`trained-models/doggie-diffusion/` directory and any running process untouched.
Quit and reopen the dashboard to load the new code and begin the new run.

The decoder weights are incompatible with the previous checkpoint. Keep strict
loading, with no partial loading or migration. Previous generated PNGs remain
viewable, but the diagnostic script now requires a checkpoint matching the new
architecture. A separate run directory avoids moving files while an old process
may still be saving them.

## Verification

A CUDA FP16 forward/backward pass and AdamW update succeeded with the default
architecture and a batch of one 64×64 RGB noisy image. Output shape was
`(1, 3, 64, 64)`; predictions and gradients were finite, and the output weights
changed after the update. The model has 31,837,731 parameters. Decoder block
input channel counts were `(768, 768)`, `(576, 384)`, and `(288, 192)` from
coarsest to finest, exercising all six concatenations.

The check ran in the project's Nix development environment; running outside it
initially failed to import PyTorch because `libstdc++.so.6` was unavailable.
Batch-size-32 memory fit, compiled execution, full training, and generation
quality have not been verified. No permanent tests were added, and existing
training/checkpoint files were not modified by the check.
