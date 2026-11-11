# Doggie Diffusion

A learning-first pixel-space diffusion model for generating random 64×64 RGB
dog images from scratch on a single RTX 2080. Training uses all 126,841 images
from the prepared dataset. The implementation is wired up but has not yet
been exercised end to end.

## Prepare the dataset

The complete [SDIP dog dataset](https://huggingface.co/datasets/rmokady/SDIP_dog)
is downloaded at `/mnt/StorageBox/datasets/SDIP_dog`.

Full conversion completed successfully: **126,841 images across 32 shards**.
Every converted shard's image count matched its source.

From the repository root, run:

```bash
uv run scripts/prepare_dog_images.py /mnt/StorageBox/datasets/SDIP_dog
```

The script declares its own Pillow and PyArrow dependencies for uv. It reads
original `data/train-*.parquet` shards in bounded batches and writes matching
shards under `64x64/`, containing 64×64 RGB images encoded as lossless PNGs.
Images are EXIF-orientation corrected and resized with Lanczos filtering.
Original files are unchanged. Each completed shard is published only after its
row count matches the source. The command reports the final image count when
conversion completes.

The output directory must be empty. After an interrupted conversion, remove
only the generated `64x64/` directory before rerunning.

## Run training

From the repository root, with an NVIDIA GPU and CUDA available to PyTorch:

```bash
uv run doggie-diffusion
```

Press **S** to start or resume, **X** to stop, and **Q** to stop and quit.
Training continues until stopped. A preview already in progress finishes
before shutdown; then the latest completed update is saved.
The shared dashboard restores the terminal's original input settings after
its run finishes, including when an exception unwinds the application.

Dashboard messages and full training-failure tracebacks are appended to
`logs/training.log`, relative to the working directory. Logs are git-ignored.

Model and training defaults live in
`src/doggie_diffusion/settings.py`. Preview and checkpoint intervals are
independent: previews every 100 optimizer updates and checkpoints every 1,000.
The U-Net uses feature channels `(64, 128, 256, 256)`, with batch size 32,
in-process data loading (`loading_workers=0`), and AdamW at
learning rate 0.0002 with zero weight decay. Add loading subprocesses only
if measurements show data loading is a bottleneck. GPU memory use and
throughput have not yet been measured.

The rolling checkpoint is `trained-models/doggie-diffusion/checkpoint.pt`,
relative to the working directory. Resume restores model weights, optimizer
state (including its saved learning rate), and completed step; data shuffling
starts anew. Deleting that model directory starts fresh.

## Agreed training behavior

- Begin with 64×64 images; reduce resolution if iteration is too slow.
- Measure progress and run length in training steps (optimizer updates), not
  epochs. Shuffle the training data.
- Load Parquet data in bounded portions and decode images as needed for
  batches; do not preload the complete dataset into RAM or GPU memory.
- Every 1,000 training steps, display snapshots after 100, 500, and 1,000
  denoising steps of the same generation in the dashboard's “Current model
  example” section, using textual-image.
- Keep save/resume simple, with git-ignored `trained-models/{model-name}/`
  storage. Deleting the model directory starts over.

The original discussion is recorded in
[the decision log](../../design-log/2026-11-10-doggy-diffusion.md), including
baseline architecture and checkpoint recommendations not yet agreed.
The project directory now uses the user's requested spelling `doggie-diffusion`;
the earlier decision log used `doggy-diffusion`.

The [full-dataset training decision](../../design-log/2026-11-11-doggie-diffusion-full-dataset.md)
supersedes the original 10,000-image subset plan and records step-based
training and dynamic loading requirements.

## Proposed network diagram

Open [the editable U-Net diagram](../../diagrams/doggie-diffusion-proposed-unet.tldraw)
in tldraw Offline. Page **01 · U-Net overview** aligns encoder and decoder
stages by resolution, with color-coded processing, skips, and timestep input.
Page **02 · Inside a residual block** expands the internal layers and routes
the residual shortcut around the processing path; a terminology guide follows.
The [network component decision](../../design-log/2026-11-11-doggie-diffusion-network-components.md)
records the agreed operations: SiLU, stride-2 convolutional downsampling,
nearest-neighbor resize followed by convolution for upsampling, and 1×1
shortcut projections when channel counts differ. Reusable component classes
use standard PyTorch layers and centralized settings. The
[implementation baseline](../../design-log/2026-11-11-doggie-diffusion-training-baseline.md)
records the subsequently approved defaults. The diagram remains a learning
aid rather than an automatically synchronized view of the code.
