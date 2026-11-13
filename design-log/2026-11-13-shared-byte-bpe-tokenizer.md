# Shared byte-level BPE tokenizer

## Decision

Add `libs/model-tokenizer/` as a dependency-free uv workspace package, following
[the shared-library layout](2026-11-10-models-monorepo-and-shared-training.md).
Reuse the byte-level BPE algorithm and pre-tokenization rules from the separate
`hello-ai/lessons/08b_tool_use_tokens/` lesson, without importing its tool-specific
dataset loading, formatting, or fixed control-token inventory.

Each model supplies ordinary-text training documents, a total vocabulary-size
target, and its own ordered list of unique, non-empty control-token spellings.
The target includes the 256 base bytes, learned merges, and controls. Training
may stop early if no eligible pairs remain. Control IDs follow the actual
ordinary vocabulary in registration order.

Ordinary encoding never recognizes control-token spellings. Models look up
registered IDs and insert them explicitly. Decoding includes registered spellings
by default and can skip controls. Literal spellings in ordinary text remain text
in either mode. Display text does not preserve the distinction between a control
ID and ordinary tokens spelling the same text.

A tokenizer's vocabulary, merges, and control IDs are fixed after training.
Versioned JSON artifacts preserve them and the pre-tokenization identity. Loading
validates the artifact and does not register additional tokens. Model layer sizes
must use the actual vocabulary size rather than the requested training target.

Keep `scripts/train-simple-english-tokenizer.py` as a small, runnable learning
example, consistent with the
[retained experiments decision](2026-11-10-retained-console-experiments.md).
It saves a tokenizer under the ignored `trained-models/tokenizers/` directory.

## Rationale and tradeoffs

Sharing the tokenizer avoids coupling text models to the tool-calling lesson.
Each model still owns its corpus, vocabulary artifact, and sequence formatting;
the library contains no model or tool-call semantics.

Explicit control insertion prevents literal text from becoming sequence
structure. A fixed vocabulary avoids silently invalidating a model's embedding
and output matrix dimensions. Adding controls later would require deliberate
model resizing and training, so there is no token-registration API after training.

Retain frequency-weighted unique chunks, indexed pair updates, and first-seen
tie-breaking from the existing implementation. The shared trainer returns the
trained tokenizer, not a duplicate tokenized corpus; callers encode documents
when needed. Keep the existing boundaries: words, whitespace and punctuation
runs are separate, and each numeric character is its own chunk.

The initial example corpus is deliberately tiny. It demonstrates training and
artifact reuse, not a vocabulary suitable for the planned NumPy language model.
No dataset or vocabulary size for that model has been selected yet.
