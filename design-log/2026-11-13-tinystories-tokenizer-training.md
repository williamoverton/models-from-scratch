# TinyStories tokenizer training

## Decision

Use the existing TinyStories V2 GPT-4 train/validation split under
`/mnt/StorageBox/datasets/TinyStories/` for the planned NumPy language model.
Train the shared byte-BPE tokenizer on the full `TinyStoriesV2-GPT4-train.txt`,
without using validation text or restricting training to a smaller subset.

Start with a total vocabulary target of 2,048 tokens, including the 256 base
bytes and one control token, `<END_OF_DOCUMENT>`. Revisit vocabulary size if
language-model training measurements warrant it. Unseen validation words remain
encodable through smaller byte-level tokens.

Adapt `scripts/train-simple-english-tokenizer.py` to this corpus, superseding the
tiny illustrative corpus described in
[the shared tokenizer decision](2026-11-13-shared-byte-bpe-tokenizer.md).
Stream complete stories and remove standalone `<|endoftext|>` delimiter lines
before BPE training. Preserve story text, including internal whitespace. Register
the document-end control separately; future model-data formatting inserts its ID
explicitly after each story.

Save the tokenizer to `trained-models/tokenizers/simple-english.json`. The script
reports corpus progress, saves and reloads the artifact, and displays a short
example's tokenization. Its corpus path and training settings remain simple
script constants rather than introducing a general dataset framework.

## Rationale and tradeoffs

Simple language and recurring story structures make learning progress motivating
to inspect. Using the full training corpus retains diversity; language-model
compute can instead be controlled through model size and training steps.

A 2,048-token vocabulary balances sequence length against the cost of the model's
output layer. It is an agreed starting choice, not a measured optimum. Vocabulary
training on the full corpus has its own upfront cost. Streaming stories avoids
holding the full text in memory, though the trainer retains unique chunks and
their pair statistics.
