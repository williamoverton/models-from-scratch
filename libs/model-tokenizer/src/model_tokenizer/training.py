"""Train byte-level BPE using frequency-weighted unique chunks."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence

from .pairs import count_pairs, merge_pair
from .pretokenization import split_chunks
from .tokenizer import Tokenizer


def count_weighted_pairs(chunk_tokens, frequencies):
    """Count pairs across unique chunks, weighted by occurrence frequency."""
    counts = Counter()
    for chunk, tokens in chunk_tokens.items():
        for pair, count in count_pairs(tokens).items():
            counts[pair] += count * frequencies[chunk]
    return counts


def build_pair_index(chunk_tokens):
    """Map each pair to the unique chunks that currently contain it."""
    index = defaultdict(set)
    for chunk, tokens in chunk_tokens.items():
        for pair in count_pairs(tokens):
            index[pair].add(chunk)
    return index


def merge_indexed_pair(chunk_tokens, pair_index, pair_counts, frequencies, pair, new_id):
    """Update counts and index entries only for chunks containing the pair."""
    # Copy the set: updating index entries may change the winning pair's set.
    affected_chunks = list(pair_index[pair])
    changed_pairs = set()
    for chunk in affected_chunks:
        old_tokens = chunk_tokens[chunk]
        old_counts = count_pairs(old_tokens)
        new_tokens = merge_pair(old_tokens, pair, new_id)
        new_counts = count_pairs(new_tokens)
        chunk_tokens[chunk] = new_tokens

        # Replace this chunk's old contribution with its new contribution.
        for changed_pair in old_counts.keys() | new_counts.keys():
            changed_pairs.add(changed_pair)
            difference = new_counts[changed_pair] - old_counts[changed_pair]
            pair_counts[changed_pair] += difference * frequencies[chunk]

        for removed_pair in old_counts.keys() - new_counts.keys():
            pair_index[removed_pair].remove(chunk)
            if not pair_index[removed_pair]:
                del pair_index[removed_pair]
        for added_pair in new_counts.keys() - old_counts.keys():
            pair_index[added_pair].add(chunk)

    # No pairs with zero occurrences should be considered in the next round.
    for changed_pair in changed_pairs:
        if pair_counts[changed_pair] == 0:
            del pair_counts[changed_pair]
    return len(affected_chunks)


def most_common_pair(pair_counts, pair_index, chunk_tokens, chunk_order):
    """Break ties as a fresh left-to-right recount would: first seen wins."""
    highest_count = max(pair_counts.values())
    candidates = [pair for pair, count in pair_counts.items() if count == highest_count]
    if len(candidates) == 1:
        return candidates[0], highest_count

    def first_position(pair):
        chunk = min(pair_index[pair], key=chunk_order.__getitem__)
        tokens = chunk_tokens[chunk]
        position = next(i for i in range(len(tokens) - 1)
                        if (tokens[i], tokens[i + 1]) == pair)
        return chunk_order[chunk], position

    return min(candidates, key=first_position), highest_count


def train_tokenizer(
    documents: Iterable[str],
    vocab_size: int,
    control_tokens: Sequence[str] = (),
) -> Tokenizer:
    """Learn within-chunk merges; the size target includes bytes and controls.

    Documents are ordinary text, not formatted control-token sequences.
    Training stops early if no eligible pairs remain. Ties follow first
    occurrence in the input, so document order affects the learned merges.
    """
    controls = validate_control_tokens(control_tokens)
    if type(vocab_size) is not int or vocab_size < 256 + len(controls):
        raise ValueError("vocab_size must include 256 bytes and all control tokens.")
    if isinstance(documents, (str, bytes)):
        raise TypeError("documents must be an iterable of text documents.")

    frequencies = Counter()
    for document in documents:
        if not isinstance(document, str):
            raise TypeError("Each document must be a string.")
        frequencies.update(split_chunks(document))

    # Evolve each unique chunk once, preserving its frequency and first position.
    chunk_tokens = {chunk: list(chunk) for chunk in frequencies}
    chunk_order = {chunk: i for i, chunk in enumerate(chunk_tokens)}
    pair_index = build_pair_index(chunk_tokens)
    pair_counts = count_weighted_pairs(chunk_tokens, frequencies)
    vocabulary = {i: bytes([i]) for i in range(256)}
    merges = []

    while len(vocabulary) + len(controls) < vocab_size and pair_counts:
        pair, _ = most_common_pair(pair_counts, pair_index, chunk_tokens, chunk_order)
        new_id = len(vocabulary)
        vocabulary[new_id] = vocabulary[pair[0]] + vocabulary[pair[1]]
        merges.append((pair, new_id))
        merge_indexed_pair(
            chunk_tokens, pair_index, pair_counts, frequencies, pair, new_id
        )

    # Controls follow the actual learned vocabulary, including early stopping.
    control_ids = {text: len(vocabulary) + i for i, text in enumerate(controls)}
    return Tokenizer(vocabulary, merges, control_ids)


def validate_control_tokens(control_tokens: Sequence[str]) -> tuple[str, ...]:
    """Reject ambiguous or duplicate control spellings before training."""
    if isinstance(control_tokens, (str, bytes)):
        raise TypeError("control_tokens must be a sequence of strings.")
    controls = tuple(control_tokens)
    if any(not isinstance(text, str) or not text for text in controls):
        raise ValueError("Control tokens must be non-empty strings.")
    if len(set(controls)) != len(controls):
        raise ValueError("Control-token spellings must be unique.")
    return controls
