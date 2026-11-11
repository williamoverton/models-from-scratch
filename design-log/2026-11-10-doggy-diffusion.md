# Doggy Diffusion: initial scope and training previews

## Decisions

Build `doggy-diffusion`, a learning-first image generation project trained from
scratch on a single RTX 2080. Generate random dogs, without text prompts or
breed selection. Start at 64×64 RGB; reduce resolution if iteration is too slow.

Use pixel-space diffusion with a U-Net predicting the synthetic noise added to
training images. Diffusion was chosen for its relevance to real-world systems,
despite more machinery and slower generation than a variational autoencoder.
A GAN was considered but introduces competing-network training complexity.

Follow the existing [model project and shared dashboard separation](2026-11-10-models-monorepo-and-shared-training.md):
the project belongs under `src/doggy-diffusion/` and owns its data, model,
diffusion process, and training settings. Shared UI code must remain
model-independent.

### Dataset

Use [rmokady/SDIP_dog](https://huggingface.co/datasets/rmokady/SDIP_dog), a curated
dataset with 126,841 dog images. The complete repository was downloaded to
`/mnt/StorageBox/datasets/SDIP_dog` successfully on 2026-11-10.

Initially train on 10,000 images to keep development manageable. Expand the
subset for longer training runs. A smaller subset reduces preparation work,
not computation per training step at a fixed batch size. It also increases
overfitting risk.

### Training previews

Every 1,000 training steps, generate one image trajectory and display snapshots
after 100, 500, and 1,000 denoising steps. These are intermediate noisy states
of the same generation, not three completed generations with different sampling
budgets.

Render the three images across the top of the Textual dashboard in a
“Current model example” section using
[textual-image](https://github.com/lnqs/textual-image).

### Save and resume

Provide simple save/resume functionality using the git-ignored directory
`trained-models/{model-name}/`, specifically `trained-models/doggy-diffusion/`.
Deleting the model directory is how the user starts again. Do not add an
experiment-management framework.

## Proposed details — not yet agreed

The following recommendations were discussed but have not been approved as
implementation decisions:

- Small convolutional U-Net without attention, with channels 32 → 64 → 128 → 128
  at spatial resolutions 64 → 32 → 16 → 8, and two residual blocks per level.
  The suggested parameter count was an estimate, not measured.
- Batch size 32, AdamW with learning rate 0.0002, and full-precision training
  initially. Memory use and speed have not been measured.
- Standard DDPM (Denoising Diffusion Probabilistic Model) formulation with
  1,000 noise levels and a noise-prediction objective.
- A fixed 10,000-image subset and fixed preview randomness for comparisons
  between training stages.
- Pause training during preview sampling while keeping the UI responsive.
- One rolling `checkpoint.pt`, automatically resumed, containing model weights,
  optimizer state, training step, and settings. Save every 1,000 steps and on a
  clean stop; replace atomically and report incompatible settings rather than
  silently restarting.

## Next discussion

Confirm the proposed baseline and checkpoint behavior, then inspect the existing
dashboard to agree on preview integration before implementing. No model or UI
implementation has been authorized by this decision-log request.
