# NumPy language-model inference overview

## Decision

Start the new text model with a very high-level, editable inference diagram in
`diagrams/numpy-llm-inference-overview.tldraw`. It describes the agreed architecture,
not an implemented model. Expand individual components and training flows as we
write and discuss their code, rather than designing all internals upfront.

Show prompt encoding, token context selection, the NumPy model, next-token
probabilities, sampling, and the autoregressive generation loop. The model
contains token embeddings plus position information, causal transformer blocks,
and an output projection from the final position to vocabulary scores. Keep
sampling outside the model boundary; learned weights are fixed during inference.

Append each sampled token ID to the sequence. Continue with the latest tokens
that fit the context window, or stop on `<END_OF_DOCUMENT>` and decode generated
IDs while skipping that control. The trained TinyStories tokenizer has 2,048
tokens and document-end ID 2047, following
[the corpus and vocabulary decision](2026-11-13-tinystories-tokenizer-training.md).

Do not specify context length, representation width, layer count, position
encoding method, or transformer internals in this overview. These remain future
decisions, as do loss calculation and manual backward calculations.

## Rationale

Separating the model's forward pass from tokenization and generation makes clear
what the model calculates versus how a prediction is used. One overview gives us
a shared map without preempting the developer-in-the-loop work on each component.
