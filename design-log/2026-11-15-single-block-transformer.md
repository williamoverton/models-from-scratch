# Single-block NumPy transformer lesson

## Decision

Replace the averaged-embedding predictor from
[the Marimo next-token lesson decision](2026-11-15-marimo-next-token-predictor.md)
with a genuine single decoder transformer block. Preserve that decision's
reactive Marimo workflow and earlier Jupyter references, but supersede its
averaging architecture rather than maintain two implementations.

Use an eight-token context, width 16, one causal scaled dot-product attention
head, learned position embeddings, and a width-64 feedforward layer with tanh
activation.
Pre-layernorm attention and feedforward sublayers each have a residual path;
a final layer normalization and linear vocabulary projection read the last
position. Compute forward operations and all backward gradients manually in
NumPy, and update parameters with Adam. No PyTorch or automatic differentiation.

Keep the reusable model in `src/numpy-llm-stories/src/numpy_llm_stories/transformer.py`.
`Transformer(vocab_size, context_size=8, width=16, seed=42)` exposes `parameters`,
`forward(ids)`, `loss_and_gradients(ids, targets)`, and
`step(gradients, learning_rate)`. Forward exposes probabilities, logits,
attention, token embeddings, positioned embeddings, and hidden states.
Padding-free inference contexts may contain one through eight tokens; teaching
updates use eight-token contexts. Use a separate same-seed model for the
before-training comparison.

The walkthrough is token chips → token plus position heatmaps → causal attention
heatmap → final-position hidden vector → prediction bars. Retain expandable
calculations and the existing post-training next-token prediction. Training
controls use 0–600 updates (default 300) and Adam learning rates from 0.001–0.03
(default 0.01).

## Why and tradeoffs

Averaging discards order and assigns every context token equal weight. Learned
positions and causal attention make order-sensitive contextual representations
part of the actual predictor, rather than an isolated attention demonstration.
One small block keeps the forward path and manual derivatives inspectable,
while adding the normalization, residual, and feedforward operations that make
this a transformer rather than a renamed embedding average.

The editable passage demonstrates fitting teaching text, not full TinyStories
training or generalization to unseen stories. Weights remain session-local;
full-corpus training and whole-story generation are not delivered by this
lesson. The additional math and optimizer state are a deliberate increase in
complexity to teach the real architecture.
