"""Complete-story loading and boundary-aware, unpadded next-token batches."""

from collections.abc import Iterator, Sequence
from pathlib import Path

import numpy as np
from model_tokenizer import Tokenizer


END_OF_DOCUMENT = "<END_OF_DOCUMENT>"


def load_stories(path: str | Path, count: int = 3) -> list[str]:
    """Read the first ``count`` nonempty stories, preserving their whitespace.

    Only standalone ``<|endoftext|>`` lines are separators. A nonempty final
    story at EOF is complete even without a trailing separator.
    """
    if count < 1:
        raise ValueError("count must be positive")
    stories = []
    lines = []
    # Disable newline translation so story text retains its original whitespace.
    with Path(path).open(encoding="utf-8", newline="") as source:
        for line in source:
            if line.rstrip("\r\n") == "<|endoftext|>":
                story = "".join(lines)
                lines.clear()
                if story.strip():
                    stories.append(story)
                    if len(stories) == count:
                        return stories
            else:
                lines.append(line)
    story = "".join(lines)
    if story.strip():
        stories.append(story)
    if len(stories) < count:
        raise ValueError(f"Requested {count} complete nonempty stories, found {len(stories)} in {path}")
    return stories


def encode_stories(stories: Sequence[str], tokenizer: Tokenizer) -> list[np.ndarray]:
    """Encode each story separately as int64 ``[EOD, *story_tokens, EOD]``."""
    eod = tokenizer.control_token_ids[END_OF_DOCUMENT]
    return [np.asarray([eod, *tokenizer.encode(story), eod], dtype=np.int64) for story in stories]


def training_batches(
    sequences: Sequence[np.ndarray],
    context_size: int,
    batch_size: int,
    rng: np.random.Generator,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield one epoch of length-bucketed ``(contexts[B,T], targets[B])``.

    Every position after the initial boundary is a target exactly once,
    including the final EOD. Contexts stay inside their story and use at most
    ``context_size`` previous tokens. Short prefixes get their own length
    buckets, not padding. Both within-bucket examples and batch order are
    shuffled using only ``rng``; call again for a fresh epoch.
    """
    if context_size < 1 or batch_size < 1:
        raise ValueError("context_size and batch_size must be positive")
    buckets: dict[int, list[tuple[int, int]]] = {}
    for story_index, sequence in enumerate(sequences):
        for position in range(1, len(sequence)):
            length = min(position, context_size)
            buckets.setdefault(length, []).append((story_index, position))

    batches = []
    for length, examples in buckets.items():
        order = rng.permutation(len(examples))
        for start in range(0, len(order), batch_size):
            batches.append((length, examples, order[start : start + batch_size]))
    rng.shuffle(batches)
    for length, examples, indices in batches:
        contexts = np.empty((len(indices), length), dtype=np.int64)
        targets = np.empty(len(indices), dtype=np.int64)
        for row, index in enumerate(indices):
            story_index, position = examples[index]
            sequence = sequences[story_index]
            contexts[row] = sequence[position - length : position]
            targets[row] = sequence[position]
        yield contexts, targets
