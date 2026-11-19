# Tool-calling data preparation and training previews

## Decision

Port the custom tool-calling model and its synthetic data generator as a
workspace project. Train from scratch rather than converting old checkpoints
or requiring artifacts from the source checkout. Prepare a fresh byte-BPE
vocabulary from the training split using the shared tokenizer. The model
project owns protocol framing, assistant-only targets, and artifact identity.
The prepared manifest records the context limit used for training.

The Textual dashboard shows one fixed example after the first completed step,
every 500 steps, and at completion. It displays a proposed call and a separate
answer conditioned on a supplied reference call and simulated result. It does
not run the proposed call. The model project owns sampling; the shared
[training callback](2026-11-10-training-progress-and-ui.md) carries display text.

## Why

Regenerating the corpus makes the experiment self-contained and avoids the old
vocabulary's exposure to a now-held-out schema. A fixed example makes outputs
comparable across updates. Supplying a reference result isolates answer quality
from call quality and makes both inspectable without a tool runtime. Existing
image and metrics-only dashboard users retain their workflows.

## Tradeoffs

Preparation costs time and disk space, and the new vocabulary need not assign
historical token IDs. Sampling briefly pauses updates on the training worker;
it does not stream tokens into the UI. Held-out schemas may still share
operation patterns with training schemas, so the split does not prove
performance on entirely novel operations.
