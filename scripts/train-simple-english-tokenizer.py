"""Train a 2,048-token byte-BPE vocabulary on the full TinyStories V2 train split.

Run from the repository root:
    uv run --package model-tokenizer python scripts/train-simple-english-tokenizer.py

Re-running replaces trained-models/tokenizers/simple-english.json.
Validation text is not used for vocabulary training.
"""

from collections.abc import Iterator
from pathlib import Path
from time import perf_counter

from model_tokenizer import Tokenizer, train_tokenizer


TRAIN_PATH = Path("/mnt/StorageBox/datasets/TinyStories/TinyStoriesV2-GPT4-train.txt")
OUTPUT_PATH = Path("trained-models/tokenizers/simple-english.json")
VOCAB_SIZE = 2048
END_OF_DOCUMENT = "<END_OF_DOCUMENT>"


def read_stories(path: Path) -> Iterator[str]:
    """Stream complete stories, excluding the dataset's separator lines."""
    lines = []
    count = 0
    with path.open(encoding="utf-8") as source:
        for line in source:
            if line.rstrip("\r\n") == "<|endoftext|>":
                story = "".join(lines)
                lines.clear()
                if story.strip():
                    count += 1
                    yield story
                    if count % 100_000 == 0:
                        print(f"Read {count:,} training stories", flush=True)
            else:
                lines.append(line)

    # Keep the final story even if the file has no trailing separator.
    story = "".join(lines)
    if story.strip():
        count += 1
        yield story
    print(f"Read all {count:,} training stories; learning BPE merges.", flush=True)


print(f"Training on: {TRAIN_PATH}", flush=True)
print(f"Vocabulary target: {VOCAB_SIZE:,}, including {END_OF_DOCUMENT}", flush=True)
started = perf_counter()
tokenizer = train_tokenizer(
    read_stories(TRAIN_PATH),
    vocab_size=VOCAB_SIZE,
    control_tokens=[END_OF_DOCUMENT],
)
print(f"Training finished in {perf_counter() - started:.1f} seconds", flush=True)

# Save the fixed vocabulary for the future language model, then load it again.
tokenizer.save(OUTPUT_PATH)
loaded = Tokenizer.load(OUTPUT_PATH)
print(f"Saved tokenizer: {OUTPUT_PATH}")
print(f"Reloaded vocabulary: {loaded.vocab_size:,} tokens")
print(f"Learned merges: {len(loaded.merges):,}")
print(f"Control IDs: {dict(loaded.control_token_ids)}")

# Story boundaries are explicit IDs, never ordinary text passed to BPE.
text = "Once upon a time, there was a fluffy bunny."
ordinary_ids = loaded.encode(text)
sequence = ordinary_ids + [loaded.control_token_ids[END_OF_DOCUMENT]]
print(f"Example text: {text}")
print(f"Ordinary text IDs: {ordinary_ids}")
print(f"Token pieces: {[loaded.vocabulary[token_id] for token_id in ordinary_ids]}")
print(f"With document boundary: {loaded.decode(sequence)}")
print(f"Without control tokens: {loaded.decode(sequence, skip_control_tokens=True)}")
