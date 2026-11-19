# NumPy LLM Stories

## Scope

This model is a learning project focused on transformer math, using NumPy
instead of PyTorch. Implement the model's forward calculations and explicit
backward gradients; do not introduce an automatic-differentiation framework.
The root PyTorch/CUDA defaults do not apply to this explicitly NumPy-only model.

The Marimo lesson `notebooks/03-next-token-predictor.py` uses the reusable
`Transformer` in `src/numpy_llm_stories/transformer.py`, not an averaged-embedding
predictor. Keep one decoder block: notebook context length 32, width 32, one
causal scaled dot-product attention head, learned positions, and a width-128
feedforward layer with tanh activation.
Use pre-layernorm residual attention and feedforward sublayers, final layer
normalization, and a linear vocabulary output from the last position.
Keep manual NumPy gradients and Adam; do not add PyTorch or autodiff.

Preserve the module API: `Transformer(vocab_size, context_size=8, width=16,
seed=42)`, a `parameters` dictionary, `forward(ids)`,
`loss_and_gradients(ids, targets)`, and `step(gradients, learning_rate)`.
Forward returns `probabilities`, `logits`, `attention`, `token_embeddings`,
`positioned_embeddings`, and `hidden`. Accept padding-free contexts of length
1 through `context_size`; construct the notebook model with
`context_size=32, width=32` and train on every prefix length through 32. Adam owns its moments
and update count. Use a separate same-seed instance for the initial comparison
rather than retaining a second model implementation.

## Notebook-led learning

Keep concept-focused notebooks under `notebooks/`, starting with
`00-environment.ipynb`. Use the project's optional `notebooks` dependencies and
the shared uv environment; do not install packages into a global Python or
register a machine-specific kernel.

Use the optional `marimo` extra for the reactive next-token predictor lesson.
Keep the lesson's guided sequence: token chips, token plus position heatmaps,
causal attention heatmap, final-position hidden vector, and prediction bars,
then training experiments and the existing post-training next-token prediction.
Expose mathematical operations in expandable calculation panels; keep
implementation and presentation cells collapsed with `@app.cell(hide_code=True)`.
Token-only and token-plus-position heatmaps share a signed scale; label the
final hidden vector's separate scale. Attention must expose the causal mask,
and probability bars use a fixed 0–100% scale. UI changes must drive actual
NumPy calculations, not a JavaScript approximation. Make arrays scrollable with
clear position labels. Show the complete training stories in an accordion,
loss per epoch, processed example count, and optimizer update count.
Use epochs 0–200 (default 80), batch size 16, and Adam learning rates
0.001–0.01 (default 0.003). Training-control changes reset the model to a fixed
seed; prompt and generation-control changes must not retrain it.
Keep the live next-token prediction and a separate autoregressive greedy
continuation. Stop generation at EOD or a configurable token cap (default and
maximum 400); an empty prompt begins with EOD. Retain earlier Jupyter notebooks
as references. This is session-local educational memorization, not a promise of
generalization, checkpoints, or a full-corpus training pipeline.

Write notebooks to run top to bottom from a fresh kernel. Standard Jupyter
execution uses the notebook's directory as its working directory; make artifact
paths explicit and document that assumption. Do not rely on out-of-order cells,
hidden state, or absolute interpreter paths in notebook metadata.

Keep explanations and exploratory calculations in notebooks. Move understood,
reused components into `src/numpy_llm_stories/`; do not introduce model components
before discussing them with the developer. Long-running model training belongs
in scripts rather than depending on an interactive notebook session.

Keep notebook prose educational and descriptive: explain the concepts, notation,
calculations, and how to interpret the results. Do not include agent self-reminders,
process commentary, repeated kernel-selection instructions, disclaimers that an
example is not the final architecture, or callouts to unrelated future work.
Keep environment and operating instructions in the README or environment notebook,
not repeated throughout concept notebooks.

Keep mathematical logic visible. Put LaTeX formatting and display-only helpers
in separate code cells with `metadata.jupyter.source_hidden = true`, leaving
their rendered outputs visible.

Retain meaningful learning outputs when useful, but never commit credentials,
server tokens, massive array dumps, or generated model artifacts in notebooks.
Ignore Jupyter autosave checkpoints, not the notebooks themselves.

## Data and tokenizer

Use the existing TinyStories V2 training and validation splits under
`/mnt/StorageBox/datasets/TinyStories/`. Do not train on validation text.
The user explicitly agreed to the first three complete real training stories
for this educational notebook, while accepting that full-corpus training is
impractical here. This permission does not change the full-corpus tokenizer
training decision or authorize replacing the corpus for other training work.

Reuse `model-tokenizer`; do not copy its BPE implementation into this project.
The current artifact is `trained-models/tokenizers/simple-english.json`, relative
to the repository root. Its total vocabulary is 2,048, including one control,
`<END_OF_DOCUMENT>` (ID 2047). Read the actual artifact when constructing model
layers rather than independently recreating its vocabulary.

Keep standalone dataset delimiter lines (`<|endoftext|>`) out of ordinary
story text while preserving story whitespace. Use `stories.py` for
`load_stories(path, count=3)`, `encode_stories(stories, tokenizer)`, and
`training_batches(sequences, context_size, batch_size, rng)`; do not put model
construction or training orchestration in that module. Count an unterminated
nonempty final story at EOF; fail if fewer than the requested stories exist.

Encode each sequence as `[EOD] + encoded_story + [EOD]` using the registered
control ID, not its text spelling. The starting EOD marks a fresh story.
For target positions 1 through `len(sequence) - 1`, include every next-token
example exactly once per epoch, including short prefixes and the final EOD.
Use only the preceding `min(position, context_size)` tokens of that story.
Length-bucket padding-free minibatches yield contexts `(B, T)` and targets
`(B,)`; shuffle within buckets and batch order reproducibly with the supplied
random generator. Create a fresh batch iterator each epoch.

## Documentation and diagrams

Keep the model README current and link shared tokenizer usage rather than
repeating its API documentation. Record new agreed architecture decisions in
the root design log.

The editable inference source is
`diagrams/numpy-llm-inference-overview.tldraw`. Follow `diagrams/AGENTS.md` and the
`tldraw-offline` skill when editing it. `inference-overview.png` in this directory
is its GitHub-readable export; regenerate it when changing the overview.
Preserve the compact horizontal-row layout for readability in the README.

The notebook's implemented transformer overview is
`diagrams/numpy-llm-transformer-block.tldraw`, exported here as
`transformer-block.png`. Keep it near the top of the notebook and regenerate
the image through tldraw when the model architecture or notebook dimensions
change. Preserve both pre-norm residual paths and the last-position readout.

Expand subcomponent diagrams and training flows as their implementation is
discussed, rather than adding speculative design detail to the top-level view.
