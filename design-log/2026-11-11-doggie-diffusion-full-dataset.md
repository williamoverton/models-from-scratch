# Doggie Diffusion: full dataset and step-based training

## Decision

Train on all 126,841 prepared 64×64 dog images, with shuffled training data,
rather than an initial 10,000-image subset. This supersedes the subset decision
in [the initial model decision](2026-11-10-doggy-diffusion.md).

Measure progress and configure run length in training steps, not epochs. One
training step means one optimizer update. Keep the agreed preview interval of
1,000 training steps; denoising steps within a preview are a separate count.

Load data dynamically: read prepared Parquet data in bounded portions and
decode images as needed for training batches. Do not load or decode the full
dataset into RAM or GPU memory before training. Keep buffering bounded rather
than materializing the full dataset to shuffle it. The exact loader and
shuffling implementation remains to be decided.

## Rationale and tradeoffs

The complete prepared dataset now exists at
`/mnt/StorageBox/datasets/SDIP_dog/64x64/`. Restricting training to 10,000 images
no longer saves preparation work. At the same batch size and model settings,
a larger dataset does not inherently increase computation per training step;
it provides more variety before repeating examples and reduces overfitting
risk. Actual throughput still depends on data loading and must be measured.

An epoch becomes longer with more data, so epochs are not a consistent unit
for comparing development runs. Step-based limits preserve a predictable
amount of optimizer work and the existing preview cadence.

Dynamic loading keeps memory use bounded and avoids a full-dataset decoding
phase at startup. It introduces ongoing disk reads and decoding work, which
must be balanced against training throughput without building an unnecessary
data-loading framework.
