# Doggie Diffusion: network components and sampling operations

## Decisions

Refine the U-Net proposal in [the initial scope](2026-11-10-doggy-diffusion.md)
with the following agreed component choices. This records the architecture
walkthrough, not authorization to implement the model.

### Modular components and settings

Use standard PyTorch layers directly, including `nn.Conv2d`, rather than
wrapping each individual layer in a custom class. Define custom classes for
meaningful reusable components: `ResidualBlock`, `Downsample`, `Upsample`,
and the connecting `UNet`.

Keep model settings centralized, exposing kernel sizes, channel counts, and
sampling settings. Preserve spatial size inside processing blocks; make
resolution changes explicit in downsampling and upsampling components.
Configuration must respect matching shapes at skip connections and residual
additions, not pretend arbitrary strides are interchangeable.

### Convolutions and residual processing

An input convolution maps three RGB channels to learned feature channels.
An output convolution maps the final features to three predicted-noise
channels. The output is not a finished RGB image: the diffusion sampler uses
it with the current noisy image and noise schedule to calculate a reverse
step. Do not restrict predicted noise to a display-pixel range.

Keep SiLU (Sigmoid Linear Unit) activations as the conventional diffusion
baseline. ReLU was considered; SiLU provides a smooth gate rather than a hard
zero cutoff. No image-quality advantage has been measured for this project.

The residual-block processing path is normalization → SiLU → convolution →
add timestep conditioning → normalization → SiLU → convolution. Each block
projects the timestep encoding to its output channel count and broadcasts
those values across spatial positions. This is an additive offset, not direct
feature multiplication.

Add the processing result to the shortcut: `output = shortcut + correction`.
The correction updates internal features, not the final image or noise
prediction, and is not constrained to be small. Use an identity shortcut
when channels match; otherwise a learned 1×1 convolution projects the input
channels to the output channel count without changing spatial size.

### Downsampling and upsampling

Downsample with a learned 3×3 convolution, stride 2, padding 1. Spatial
resolution halves; output channel count is a separate setting. This replaces
the previously unspecified downsampling operator.

Upsample using nearest-neighbor resizing by a factor of two followed by a
learned 3×3 stride-1 convolution with spatially preserving padding. This makes
expansion and refinement explicit instead of using a transposed convolution,
which can introduce checkerboard artifacts. Upsampling alone cannot restore
lost spatial detail.

Concatenate matching-resolution encoder features with the upsampled decoder
features along the channel dimension, then process them with residual blocks.
These long U-Net skips concatenate; shortcuts inside residual blocks add.

## Still provisional

The diagram retains the illustrative 32 → 64 → 128 → 128 channel widths,
64 → 32 → 16 → 8 resolution path, and two residual blocks per stage. Do not
interpret the walkthrough as approval of all architecture sizing or training
hyperparameters. Group normalization is illustrated, but its group count has
not been chosen; eight groups was only a teaching example. Exact timestep
encoding details and input/output convolution settings still need finalizing.

The earlier batch-size, optimizer, precision, checkpoint-policy, and fixed
preview-randomness recommendations remain proposals unless separately agreed.
Use the full prepared dataset and step-based progress as recorded in
[the dataset decision](2026-11-11-doggie-diffusion-full-dataset.md).

## Diagram

[The editable diagram](../diagrams/doggie-diffusion-proposed-unet.tldraw) shows
the agreed operations within the still-proposed network sizing. Preserve its
two-page layout: aligned U-Net overview and expanded residual-block detail.
