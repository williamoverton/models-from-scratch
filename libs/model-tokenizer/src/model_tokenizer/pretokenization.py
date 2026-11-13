"""Split ordinary text into lossless chunks for byte-level BPE."""

PRETOKENIZATION = "unicode-word-single-number-whitespace-punctuation-v2"


def split_chunks(text: str) -> list[bytes]:
    """Keep every character, splitting each numeric character into its own chunk.

    Numeric characters cannot merge with each other or with letters. Non-ASCII
    characters may still need multiple byte tokens within their own chunk.
    """
    chunks = []
    start = 0
    previous = None
    for position, character in enumerate(text):
        kind = ("number" if character.isnumeric() else
                "word" if character.isalnum() else
                "space" if character.isspace() else "punctuation")
        if previous is not None and (kind != previous or kind == "number"):
            chunks.append(text[start:position].encode("utf-8"))
            start = position
        previous = kind
    if previous is not None:
        chunks.append(text[start:].encode("utf-8"))
    return chunks
