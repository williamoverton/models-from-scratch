"""Remove numeric citation markers from packed Wikipedia token rows."""

from bisect import bisect_left, bisect_right
from itertools import accumulate
import re

from model_tokenizer import Tokenizer
import numpy as np

_CITATION = re.compile(rb"(?:\[[0-9]{1,4}\])+")


class WikipediaCitationFilter:
    """Strip complete markers without decoding text or re-tokenizing whole tokens."""

    def __init__(self, tokenizer: Tokenizer) -> None:
        # Control IDs follow the contiguous byte vocabulary. Give each one a
        # single nonmatching byte so a citation cannot span a control boundary.
        self._spellings = tuple(tokenizer.vocabulary[i] for i in range(len(tokenizer.vocabulary)))
        self._spellings += (b"\x00",) * len(tokenizer.control_token_ids)

    def clean(self, row: np.ndarray) -> list[int] | None:
        """Return cleaned IDs, or None if the row has no complete marker."""
        ids = row.tolist()
        pieces = list(map(self._spellings.__getitem__, ids))
        data = b"".join(pieces)
        match = _CITATION.search(data)
        if match is None:
            return None

        offsets = list(accumulate(map(len, pieces), initial=0))
        cleaned: list[int] = []

        def keep(start: int, end: int) -> None:
            if start == end:
                return
            first = bisect_left(offsets, start)
            last = bisect_right(offsets, end) - 1
            # Slice only partial tokens; the base token ID equals the byte value.
            if first > last:
                cleaned.extend(data[start:end])
            else:
                cleaned.extend(data[start:offsets[first]])
                cleaned.extend(ids[first:last])
                cleaned.extend(data[offsets[last]:end])

        start = 0
        while match is not None:
            keep(start, match.start())
            start = match.end()
            match = _CITATION.search(data, start)
        keep(start, len(data))
        return cleaned
