# Complete-story NumPy transformer notebook

## Decision

Align the Marimo lesson with story generation by training on the first three
complete real stories in
`/mnt/StorageBox/datasets/TinyStories/TinyStoriesV2-GPT4-train.txt`.
The user explicitly permitted a small fixed subset of complete stories for this
educational notebook and accepted that full-corpus training is impractical here.
This supersedes the short editable-passage training, eight-token context,
width-16/FF64 dimensions, and update-count controls in the
[single-block decision](2026-11-15-single-block-transformer.md) and the earlier
[Marimo lesson decision](2026-11-15-marimo-next-token-predictor.md).
It does not change the full-corpus tokenizer decision or validation split.

Preserve one decoder block, learned positions, one causal scaled dot-product
attention head, pre-layernorm residual attention and feedforward sublayers,
tanh feedforward activation, final layer normalization, and the last-position
linear vocabulary projection. Use context 32, width 32, feedforward width 128,
manual NumPy gradients, and Adam. Keep the reusable Transformer API; the
notebook explicitly supplies its dimensions. No PyTorch or autodiff.

## Story boundaries and training

Keep whitespace in stories, excluding standalone `<|endoftext|>` separator
lines. Load three complete nonempty stories; an unterminated final story counts
at EOF, and insufficient stories is an error. Reuse the tokenizer trained on
all TinyStories training stories. Encode each story as
`[EOD] + encoded_story + [EOD]` using the registered control token, not its
spelling. The initial EOD represents a fresh story boundary.

Every target position from 1 through `len(sequence) - 1` appears exactly once
per epoch: all story tokens and final EOD, including short-prefix examples.
Each context contains the preceding `min(position, 32)` tokens from that story;
never concatenate stories into cross-boundary contexts. Bucket by context
length for padding-free minibatches of 16. Shuffle within buckets and shuffle
batch order deterministically from the supplied random generator, creating a
fresh iterator each epoch.

Keep data utilities in `src/numpy-llm-stories/src/numpy_llm_stories/stories.py`:
`load_stories(path, count=3)`, `encode_stories(stories, tokenizer)`, and
`training_batches(sequences, context_size, batch_size, rng)`. Batches contain
contexts `(B, T)` and targets `(B,)`. Model creation and training orchestration
remain outside this module.

## Reactive learning workflow

Use epochs 0–200 (default 80) and learning rates 0.001–0.01 (default 0.003).
Changing training controls resets the model from a fixed seed; changing the
prompt or generation controls must not retrain. Preserve a separate same-seed
untrained model for comparison. Show complete stories in an accordion, loss per
epoch, processed-example count, and optimizer-update count.

Keep the live next-token prediction and add a separate autoregressive greedy
continuation, feeding each predicted token back through the latest context.
Stop at EOD or a configurable token cap (default and maximum 400). An empty
prompt starts from EOD. Keep the token chips, token and position heatmaps,
causal attention, final hidden vector, probability bars, and expandable manual
calculations. Arrays must scroll with clear position labels; embedding heatmaps
share a signed scale, the hidden vector has its own labeled scale, and
probability bars retain a fixed 0–100% scale. Preserve the earlier Jupyter
notebooks and collapsed implementation cells.

## Scope and tradeoffs

Complete real stories connect boundary prediction and autoregressive decoding
to the project's purpose without pretending a short editable passage is story
training. More examples and larger arrays increase notebook runtime and demand
scrollable displays. This remains session-local educational memorization, not
evidence of generalization or a guarantee of coherent new stories. There is no
full-corpus training pipeline, saved model, or checkpoint promise.
