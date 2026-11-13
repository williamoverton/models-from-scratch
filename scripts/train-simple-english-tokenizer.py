"""Train a tiny byte-BPE vocabulary and inspect explicit control-token handling.

Run from the repository root:
    uv run --package model-tokenizer python scripts/train-simple-english-tokenizer.py

Re-running replaces trained-models/tokenizers/simple-english.json.
This tiny sample illustrates the API; it is not a useful English vocabulary yet.
"""

from pathlib import Path

from model_tokenizer import Tokenizer, train_tokenizer


# Train on ordinary text; even a literal control spelling remains ordinary text.
text = "Hello café! Hello world! <END>"
tokenizer = train_tokenizer(
    [text], vocab_size=280, control_tokens=["<END>"],
)
ordinary_ids = tokenizer.encode(text)
end_id = tokenizer.control_token_ids["<END>"]

print(f"Vocabulary: {tokenizer.vocab_size} tokens (target: 280)")
print(f"Learned merges: {len(tokenizer.merges)}")
print(f"Control IDs: {dict(tokenizer.control_token_ids)}")
print(f"Ordinary text IDs: {ordinary_ids}")
print(f"Control ID present in ordinary text: {end_id in ordinary_ids}")
print(f"Decoded ordinary text: {tokenizer.decode(ordinary_ids)}")

# Insert a control ID explicitly; skipping controls preserves the literal spelling.
sequence = ordinary_ids + [end_id]
print(f"With control: {tokenizer.decode(sequence)}")
print(f"Skipping controls: {tokenizer.decode(sequence, skip_control_tokens=True)}")

# Keep an artifact that future runs can load without retraining.
path = Path("trained-models/tokenizers/simple-english.json")
tokenizer.save(path)
loaded = Tokenizer.load(path)
print(f"Saved tokenizer: {path}")
print(f"Reloaded vocabulary: {loaded.vocab_size} tokens")
print(f"Reloaded encoding matches: {loaded.encode(text) == ordinary_ids}")
print(f"Reloaded controls match: {loaded.control_token_ids == tokenizer.control_token_ids}")
print(f"Reloaded sequence: {loaded.decode(sequence)}")
