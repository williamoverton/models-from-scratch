# Doggie Diffusion

A learning-first pixel-space diffusion model for generating random 64×64 RGB
dog images from scratch on a single RTX 2080. Model implementation is not yet
present. Training will use all 126,841 images from the prepared dataset.

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
