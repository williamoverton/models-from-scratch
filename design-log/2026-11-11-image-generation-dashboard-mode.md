# Reusable image-generation dashboard mode

## Decision

Extend the shared Textual dashboard with opt-in `image_generation=True`.
This follows [the shared training UI separation](2026-11-10-training-progress-and-ui.md)
and [the Doggie Diffusion preview decision](2026-11-10-doggy-diffusion.md).

Place a fixed `Current model example` panel below the application header and
above the scrollable metrics/log. It contains three equally sized image slots,
model-provided labels, and the training step that produced the example. Keep
the current example visible when later metric-only reports arrive. Clear it
when starting another run. Other model projects keep the existing dashboard
layout by leaving image-generation mode disabled.

Use `textual-image` widgets with their automatic terminal rendering selection.
Pillow is an explicit shared-package dependency because it is part of the
preview contract. The dashboard does not depend on PyTorch or import model
projects.

`TrainingProgress.preview` optionally carries an `ImageGenerationPreview`:

- `step`: completed training step that produced the example.
- `images`: exactly three display-ready Pillow images.
- `labels`: the three corresponding captions.

The producer must not mutate images after publishing them. Delivery uses the
existing progress callback and UI-thread handoff, not a separate timer or
worker. Preview construction and tensor-to-image conversion stay in the model
project. Shared code has no diffusion-step constants.

For Doggie Diffusion the labels will describe snapshots after 100, 500, and
1,000 reverse steps from the same generation. Training and checkpoint wiring
remain separate work under the ongoing file-by-file review.

## Consequences

The new mode is deliberately a three-image row, not a gallery framework.
Its height is bounded so metrics retain space on smaller terminals. Actual
image rendering depends on terminal graphics support; the image library can
select character-based rendering when graphics protocols are unavailable.
