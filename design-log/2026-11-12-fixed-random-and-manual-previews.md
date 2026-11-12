# Fixed, random, and on-demand generation previews

## Decision

Extend the [image-generation dashboard mode](2026-11-11-image-generation-dashboard-mode.md)
with two rows of three snapshots: one fixed-seed generation and one fresh
random-seed generation. Each row shows 100, 500, and 1,000 denoising steps.
The model supplies row titles, images, and labels; shared UI code remains
independent of PyTorch and individual model projects.

Doggie Diffusion resets a dedicated CUDA generator to seed 42 for the fixed
row and seeds a separate generator nondeterministically for the random row.
Both initial and reverse-step noise use those generators, not training's
random stream. Display each seed in its row title.

Scheduled previews save only the fixed row's final image to
`trained-models/doggie-diffusion/samples/generation-sample-{step}.png`.
Keep one rolling checkpoint; sample history is not checkpoint history.

Add G to request display-only generation. During training, coalesce pending
requests and generate after a completed update. A scheduled preview satisfies
a coincident request and keeps its normal fixed-image save. While stopped,
load model weights and the step from the checkpoint without starting training
or saving samples. Missing checkpoints are reported rather than generating
from untrained weights. Stop does not generate a final sample.

## Tradeoffs

Keep generation synchronous in a single process. Two generations increase
preview pauses, but preserve fixed comparisons and varied examples without
parallel weight snapshots, CUDA-stream synchronization, or concurrent model
updates. Starting training is blocked during idle generation; Quit waits for
generation to finish. A stop request suppresses pending manual generation.

The user owns runtime verification; no tests or runtime checks were run.
