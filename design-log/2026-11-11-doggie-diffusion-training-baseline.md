# Doggie Diffusion: implementation baseline, diffusion, and loading

## Context

Continue [the network component decision](2026-11-11-doggie-diffusion-network-components.md)
and [the full-dataset decision](2026-11-11-doggie-diffusion-full-dataset.md).
The user authorized implementation through file-by-file review. These decisions
replace the corresponding provisional choices in the earlier records; preserve
those records as history.

## Model settings and structure

Use a frozen `ModelSettings` dataclass for explicit, immutable configuration.
The approved starting settings are:

- Feature channels `(32, 64, 128, 128)`, at resolutions 64 → 32 → 16 → 8.
- Two residual blocks per stage and at the bottleneck.
- 3×3 processing convolutions with stride 1 and spatially preserving padding.
- Eight group-normalization groups, configurable; this divides all starting
  channel widths. It is not a measured optimum.
- A 128-value fixed timestep encoding: 64 sine/cosine pairs with geometrically
  spaced frequencies. Learned Linear → SiLU → Linear layers produce a
  128-value conditioning vector; each residual block projects it to its own
  output channel count. Encoding and conditioning widths are separate settings.
- The input/output convolutions use the processing kernel setting and map
  RGB to features and features to unrestricted three-channel noise predictions.

Use `ResidualStage` alongside `ResidualBlock` to construct and run repeated
conditioned blocks. Only a stage's first block changes channels. Keep encoder
skip storage, downsampling, upsampling, and concatenation explicit in `UNet`;
do not hide these differences in a generic pipeline. PyTorch `ModuleList`
registers the component collections.

Call the spatial resizing module `resampling.py`, distinguishing it from
image generation. Nearest-neighbor resizing has no learned weights: at scale
factor two, each feature value becomes a 2×2 patch. The following convolution
learns how to refine those enlarged grids.

## Diffusion process

Use 1,000 noise levels with a cosine schedule and the conventional 0.008
offset. Cap per-step noise variance below one to avoid singular reverse
coefficients. Schedule tensors are fixed CUDA buffers.

Train with direct noisy-image construction at a randomly selected level:
`x_t = sqrt(alpha_bar_t) * x_0 + sqrt(1 - alpha_bar_t) * noise`.
The training loop owns timestep selection, random noise targets, and mean
squared error between predicted and actual noise. `Diffusion.add_noise` owns
only the schedule-based mixture.

Generate using stochastic DDPM (Denoising Diffusion Probabilistic Model)
reverse steps with fixed posterior variance, not a learned variance output.
Calculate the reverse mean from predicted noise and sample around it using
schedule-scaled Gaussian noise. Add no fresh noise at the final step.
This samples the modeled uncertainty; it is not a reset or a heuristic for
activating features. Deterministic DDIM sampling was discussed as an
alternative, but is not the chosen baseline.

Generation runs without gradient tracking, temporarily selects evaluation
mode, and restores the model's previous mode afterward. Capture raw tensor
snapshots after 100, 500, and 1,000 completed reverse steps from the same run;
display conversion belongs outside diffusion code. Fixed preview randomness
has not yet been agreed or implemented.

### Sampling correction after inspecting generated previews

A read-only diagnostic of the step-3,000 checkpoint found final image values
from approximately -196 to 737, with 99.3% outside the display range. Adopt
the conventional pixel-space DDPM update: reconstruct the predicted clean
image from the noise estimate, clip that estimate to `[-1, 1]`, then compute
the posterior mean as a weighted combination of it and the current noisy image.
This supersedes the direct, unbounded noise-based reverse mean above.
Do not clip intermediate noisy states; retain the existing posterior variance
and final step without added noise. Training and checkpoints are unchanged.
The user authorized this implementation change only; mathematical checks,
another generation diagnostic, and a fresh training run remain separate.

## Streaming data loading

Use all 126,841 prepared images from
`/mnt/StorageBox/datasets/SDIP_dog/64x64`, without full-dataset preload.
An `IterableDataset` streams embedded PNG bytes from Parquet shards.

- Start with four configurable DataLoader workers.
- Partition shards between workers before shuffling so images are not duplicated.
- Shuffle each worker's shard order and use a 1,024-image replacement buffer
  per worker, holding compressed PNG bytes rather than float tensors.
- Read at most 128 records per requested Parquet batch; underlying Parquet
  decoding, Python objects, and prefetching also contribute to memory use.
- Drain the shuffle buffer at the end so every assigned image is yielded.
- Decode on CPU into channel-first float32 tensors scaled to `[-1, 1]`.
  Transfer assembled batches to CUDA in the training process, not in workers.

This is approximate bounded shuffling, not a uniform permutation of the full
dataset. Four workers trade additional system RAM and storage contention for
parallel loading. Throughput and actual memory use have not been measured.

## Optimizer

Use AdamW with learning rate `0.0002` and explicit `weight_decay=0.0` as the
initial configurable baseline. Disabling decay avoids adding regularization
without evidence of a need, and is an established diffusion-training choice;
it is not a measured advantage for this dataset. With zero decay, AdamW uses
Adam-style updates without its distinguishing decoupled shrinkage.

Nonzero decay can help generalization but can also contribute to underfitting.
Do not treat PyTorch's AdamW default of 0.01 as evidence that it fits this model.

## Training duration and independent intervals

Start with a configurable batch size of 32; GPU memory use is not yet measured.
Train continuously until the user stops the interactive application, making
new passes through the dataset as needed. Do not impose a maximum step count.

Keep `preview_interval` and `checkpoint_interval` independent, both initially
1,000 optimizer steps. Neither action triggers the other. Adjust the intervals
separately after measuring training, generation, and saving speeds; frequent
previews should not require equally frequent checkpoint writes.

## Scope and remaining choices

The reviewed settings, timestep embedding, residual components, resampling,
U-Net, diffusion, and dataset files have been written, but have not been run or
tested. Worker settings and optimizer choices still need wiring into the
training process. This decision record does not imply a working training app.

Stop/save behavior, checkpoint policy details, preview reproducibility,
and dashboard integration still need review. Keep simple git-ignored
model-directory storage. Continue reviewing each file with the user before
writing it.
