"""Count and merge adjacent byte-BPE token pairs."""

from collections import Counter


def count_pairs(tokens: list[int]) -> Counter[tuple[int, int]]:
    """Count neighboring tokens in one document (or excerpt).

    For the UTF-8 bytes of 'banana', (97, 110) occurs twice ('a', 'n').
    Pairs overlap: the middle token can belong to two neighboring pairs.
    """
    counts = Counter()
    for position in range(len(tokens) - 1):
        pair = (tokens[position], tokens[position + 1])
        counts[pair] += 1
    return counts


def merge_pair(
    tokens: list[int], pair: tuple[int, int], new_token_id: int
) -> list[int]:
    """Replace non-overlapping occurrences of a pair with one new token ID."""
    merged = []
    position = 0
    while position < len(tokens):
        if (
            position + 1 < len(tokens)
            and (tokens[position], tokens[position + 1]) == pair
        ):
            merged.append(new_token_id)
            position += 2  # Both tokens were consumed by this merge.
        else:
            merged.append(tokens[position])
            position += 1
    return merged


