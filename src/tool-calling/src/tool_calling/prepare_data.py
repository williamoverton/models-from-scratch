"""Prepare a complete offline tool-calling data bundle in a new directory."""

from collections.abc import Iterator
from functools import lru_cache
from hashlib import file_digest
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from model_tokenizer import Tokenizer, train_tokenizer
from model_tokenizer.pretokenization import split_chunks
import pyarrow as pa
import pyarrow.parquet as pq

from .data_generation import DEFAULT_SEED, SPLITS, write_structured_splits
from .framing import CONTROL_TOKENS, format_record, iter_text_fields

DEFAULT_CONTEXT_LENGTH = 350
MANIFEST_FORMAT = "tool-calling-data"
MANIFEST_VERSION = 2
ENCODED_SCHEMA = pa.schema([
    pa.field("tokens", pa.list_(pa.field("element", pa.int32(), nullable=False)), nullable=False),
    pa.field("loss_mask", pa.list_(pa.field("element", pa.bool_(), nullable=False)), nullable=False),
    pa.field("schema_id", pa.string(), nullable=False),
])
_ROW_GROUP_SIZE = 2048
_VOCAB_SIZE = 2048


def _sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _records(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as source:
        for line in source:
            yield json.loads(line)


def _train_text(path: Path) -> Iterator[str]:
    for record in _records(path):
        yield from iter_text_fields(record)


def _write_json(path: Path, data: dict) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as output:
        json.dump(data, output, ensure_ascii=False, indent=2)
        output.write("\n")


def _encode_splits(directory: Path, tokenizer: Tokenizer) -> dict:
    """Write typed Parquet splits without buffering the full encoded corpus."""
    @lru_cache(maxsize=32768)
    def encode_chunk(chunk: bytes) -> tuple[int, ...]:
        return tuple(tokenizer.encode(chunk.decode("utf-8")))

    def encode_text(text: str) -> list[int]:
        return [token for chunk in split_chunks(text) for token in encode_chunk(chunk)]

    splits = {}
    for split in SPLITS:
        structured_path = directory / "structured" / f"{split}.jsonl"
        encoded_path = directory / f"{split}.parquet"
        records = total_tokens = max_tokens = 0
        min_tokens = None
        rows = []
        with pq.ParquetWriter(encoded_path, ENCODED_SCHEMA) as destination:
            for line_number, record in enumerate(_records(structured_path), 1):
                try:
                    formatted = format_record(tokenizer, record, encode_text=encode_text)
                    schema_id = record["execution"]["schema_id"]
                    if not isinstance(schema_id, str) or not schema_id:
                        raise ValueError("expected a nonempty schema ID")
                    formatted["schema_id"] = schema_id
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError(f"structured/{structured_path.name}:{line_number}: {exc}") from exc
                length = len(formatted["tokens"])
                records += 1
                total_tokens += length
                max_tokens = max(max_tokens, length)
                min_tokens = length if min_tokens is None else min(min_tokens, length)
                rows.append(formatted)
                if len(rows) == _ROW_GROUP_SIZE:
                    destination.write_table(pa.Table.from_pylist(rows, schema=ENCODED_SCHEMA))
                    rows.clear()
            if rows:
                destination.write_table(pa.Table.from_pylist(rows, schema=ENCODED_SCHEMA))
        if records == 0:
            raise ValueError(f"No records were generated for {split}.")
        splits[split] = {
            "sha256": _sha256(encoded_path),
            "structured_sha256": _sha256(structured_path),
            "records": records,
            "total_tokens": total_tokens,
            "min_tokens": min_tokens,
            "max_tokens": max_tokens,
        }
    return splits


def prepare_data(
    output_dir: str | Path, *, context_length: int = DEFAULT_CONTEXT_LENGTH, seed: int = DEFAULT_SEED
) -> dict:
    """Generate, train a fresh tokenizer, and publish a hash-bound data bundle.

    Only structured training text enters BPE training. Both encoded splits must
    fit the chosen context length before the destination can be published.
    """
    if type(context_length) is not int or context_length <= 0:
        raise ValueError("context_length must be a positive integer.")
    if type(seed) is not int:
        raise ValueError("seed must be an integer.")
    output_dir = Path(output_dir)
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Output directory already exists: {output_dir}")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output_dir.parent, prefix=".tool-calling-prepare-") as temporary:
        staging = Path(temporary)
        structured = staging / "structured"
        write_structured_splits(structured, seed=seed)
        tokenizer = train_tokenizer(_train_text(structured / "train.jsonl"), _VOCAB_SIZE, CONTROL_TOKENS)
        tokenizer_path = staging / "tokenizer.json"
        tokenizer.save(tokenizer_path)
        splits = _encode_splits(staging, tokenizer)
        measured_max = max(stats["max_tokens"] for stats in splits.values())
        if measured_max > context_length:
            raise ValueError(
                f"Maximum encoded row is {measured_max} tokens, exceeding context length "
                f"{context_length}. No bundle was published. Retry prepare-data with "
                f"--context-length {measured_max} (or higher) and --output-dir <new-directory>."
            )

        manifest = {
            "format": MANIFEST_FORMAT,
            "version": MANIFEST_VERSION,
            "seed": seed,
            "context_length": context_length,
            "tokenizer_sha256": _sha256(tokenizer_path),
            "control_token_ids": dict(tokenizer.control_token_ids),
            "splits": splits,
        }
        manifest_path = staging / "manifest.json"
        _write_json(manifest_path, manifest)

        # Claim the destination exclusively and put the manifest in place last.
        # If moving any earlier artifact fails, there is no usable manifest.
        output_dir.mkdir(exist_ok=False)
        for artifact in staging.iterdir():
            if artifact != manifest_path:
                artifact.rename(output_dir / artifact.name)
        manifest_path.rename(output_dir / manifest_path.name)
    return manifest
