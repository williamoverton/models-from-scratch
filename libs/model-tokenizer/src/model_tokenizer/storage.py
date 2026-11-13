"""Persist fixed tokenizer vocabularies with explicit format validation."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from .pretokenization import PRETOKENIZATION
from .tokenizer import Tokenizer

FORMAT = "model-tokenizer-byte-bpe"
VERSION = 1


def save_tokenizer(tokenizer: Tokenizer, path: str | Path) -> None:
    """Atomically replace an artifact only after its JSON is fully written."""
    data = {
        "format": FORMAT,
        "version": VERSION,
        "pretokenization": PRETOKENIZATION,
        "vocabulary": [tokenizer.vocabulary[i].hex() for i in range(len(tokenizer.vocabulary))],
        "merges": [[left, right, new_id] for (left, right), new_id in tokenizer.merges],
        "control_token_ids": dict(tokenizer.control_token_ids),
    }
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        # A unique sibling avoids collisions and keeps replacement on one filesystem.
        with NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                prefix=f".{path.name}.", suffix=".tmp", delete=False) as file:
            temporary_path = Path(file.name)
            file.write(json.dumps(data, indent=2) + "\n")
        temporary_path.replace(path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def load_tokenizer(path: str | Path) -> Tokenizer:
    """Reject incompatible formats and inconsistent vocabulary/control IDs."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("format") != FORMAT
            or type(data.get("version")) is not int or data["version"] != VERSION
            or data.get("pretokenization") != PRETOKENIZATION):
        raise ValueError("Unsupported tokenizer format, version, or pretokenization.")
    try:
        if (not isinstance(data["vocabulary"], list)
                or not isinstance(data["merges"], list)
                or not isinstance(data["control_token_ids"], dict)):
            raise ValueError("Invalid tokenizer artifact fields.")
        vocabulary = {i: bytes.fromhex(value) for i, value in enumerate(data["vocabulary"])}
        merges = [((left, right), new_id) for left, right, new_id in data["merges"]]
        return Tokenizer(vocabulary, merges, data["control_token_ids"])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Invalid tokenizer artifact.") from error
