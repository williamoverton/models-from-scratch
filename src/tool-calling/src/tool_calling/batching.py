"""Validate one prepared bundle and batch complete assistant-masked interactions."""

from dataclasses import dataclass
from hashlib import file_digest, sha256
import json
from pathlib import Path
from threading import Event

from model_tokenizer import Tokenizer
import pyarrow as pa
import pyarrow.parquet as pq
import torch
from torch.nn.utils.rnn import pad_sequence

from .framing import CONTROL_TOKENS
from .prepare_data import ENCODED_SCHEMA, MANIFEST_FORMAT, MANIFEST_VERSION

IGNORE_TARGET = -100


@dataclass(frozen=True)
class Record:
    """Aligned token IDs and mask with the generating schema's ID."""

    tokens: torch.Tensor
    mask: torch.Tensor
    schema_id: str


@dataclass(frozen=True)
class Bundle:
    """Validated artifacts, with a manifest digest binding their identities."""

    tokenizer: Tokenizer
    manifest_digest: str
    train: list[Record]
    validation: list[Record]


def _object(data: bytes, path: Path) -> dict:
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def _assistant_mask_matches(tokens: list[int], mask: list[bool], supervision: dict[int, bool],
                            eod: int) -> bool:
    """Ordinary tokens and delimiters inherit the supervision of their framing segment."""
    expected = False
    for index, (token, active) in enumerate(zip(tokens, mask)):
        if token == eod and index != len(tokens) - 1:
            return False
        expected = supervision.get(token, expected)
        if active != expected:
            return False
    return True


def _file_hash(path: Path) -> str:
    with path.open("rb") as stream:
        return file_digest(stream, "sha256").hexdigest()


def _read_split(path, metadata, tokenizer, vocab_size, context_length, stop_event):
    """Read bounded Parquet batches from a manifest-bound split."""
    records = []
    controls = tokenizer.control_token_ids
    eod = controls["<END_OF_DOCUMENT>"]
    supervision = {
        controls[marker]: marker in {
            "<TOOL_CALL>", "<EXECUTE>", "<ASSISTANT>", "<END_OF_DOCUMENT>",
        }
        for marker in CONTROL_TOKENS if marker != "<DELIMETER>"
    }
    with path.open("rb") as stream:
        # Hash the same open file used by the Parquet reader, without buffering it.
        digest = sha256()
        while chunk := stream.read(1024 * 1024):
            if stop_event.is_set():
                return None
            digest.update(chunk)
        if digest.hexdigest() != metadata["sha256"]:
            raise ValueError(f"Encoded split digest does not match manifest: {path}.")
        stream.seek(0)
        try:
            with pq.ParquetFile(stream) as split:
                if not split.schema_arrow.equals(ENCODED_SCHEMA):
                    raise ValueError(f"Unexpected encoded split schema: {path}.")
                count = metadata["records"]
                if type(count) is not int or count < 1 or split.metadata.num_rows != count:
                    raise ValueError(f"Encoded split row count does not match manifest: {path}.")
                for batch in split.iter_batches(batch_size=2048):
                    for tokens, mask, schema_id in zip(*(column.to_pylist() for column in batch.columns)):
                        if stop_event.is_set():
                            return None
                        if not (
                            isinstance(tokens, list) and isinstance(mask, list)
                            and 2 <= len(tokens) <= context_length and len(tokens) == len(mask)
                            and all(type(token) is int and 0 <= token < vocab_size for token in tokens)
                            and all(type(value) is bool for value in mask)
                            and not mask[0] and mask[-1] and tokens[-1] == eod
                            and _assistant_mask_matches(tokens, mask, supervision, eod)
                            and isinstance(schema_id, str) and schema_id
                        ):
                            raise ValueError(
                                f"Invalid encoded record at {path}:{len(records) + 1}: "
                                f"invalid tokens, assistant mask, or schema ID (context limit {context_length})."
                            )
                        records.append(Record(torch.tensor(tokens, dtype=torch.long),
                                              torch.tensor(mask, dtype=torch.bool), schema_id))
        except pa.ArrowException as error:
            raise ValueError(f"Invalid Parquet split {path}: {error}") from error
    if len(records) != count:
        raise ValueError(f"Encoded split row count does not match manifest: {path}.")
    return records


def load_bundle(directory: Path, stop_event: Event) -> Bundle | None:
    """Load only the prepared format; cancellation returns no partial bundle."""
    if stop_event.is_set():
        return None
    manifest_path = directory / "manifest.json"
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = _object(manifest_bytes, manifest_path)
        if (manifest.get("format") != MANIFEST_FORMAT
                or type(manifest.get("version")) is not int
                or manifest["version"] != MANIFEST_VERSION):
            raise ValueError(f"Unsupported data format or version: {manifest_path}.")
        context = manifest["context_length"]
        if type(context) is not int or context <= 0:
            raise ValueError(f"Invalid context length: {manifest_path}.")

        tokenizer_path = directory / "tokenizer.json"
        tokenizer_hash = manifest["tokenizer_sha256"]
        if _file_hash(tokenizer_path) != tokenizer_hash:
            raise ValueError(f"Tokenizer digest does not match manifest: {tokenizer_path}.")
        try:
            tokenizer = Tokenizer.load(tokenizer_path)
        except ValueError as error:
            raise ValueError(f"Invalid tokenizer {tokenizer_path}: {error}") from error
        if _file_hash(tokenizer_path) != tokenizer_hash:
            raise ValueError(f"Tokenizer changed while loading: {tokenizer_path}.")
        control_ids = manifest["control_token_ids"]
        if (not isinstance(control_ids, dict) or any(type(i) is not int for i in control_ids.values())
                or control_ids != tokenizer.control_token_ids or set(control_ids) != set(CONTROL_TOKENS)):
            raise ValueError(f"Tokenizer control map does not match the prepared format: {tokenizer_path}.")

        splits = manifest["splits"]
        vocab_size = tokenizer.vocab_size
        train = _read_split(directory / "train.parquet", splits["train"],
                            tokenizer, vocab_size, context, stop_event)
        if train is None:
            return None
        validation = _read_split(directory / "validation.parquet", splits["validation"],
                                 tokenizer, vocab_size, context, stop_event)
        if validation is None or stop_event.is_set():
            return None
        return Bundle(tokenizer, sha256(manifest_bytes).hexdigest(), train, validation)
    except (KeyError, OSError, TypeError, ValueError) as error:
        raise ValueError(
            f"Cannot use prepared bundle {directory}: {error} "
            "Run prepare-data --output-dir <new-directory> if the artifacts are missing or invalid."
        ) from error


def pack_batch(records: list[Record], device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    """Shift the targets and their mask together, then right-pad this batch only."""
    inputs = pad_sequence([record.tokens[:-1] for record in records], batch_first=True)
    targets = pad_sequence(
        [record.tokens[1:].masked_fill(~record.mask[1:], IGNORE_TARGET) for record in records],
        batch_first=True, padding_value=IGNORE_TARGET,
    )
    return inputs.to(device), targets.to(device)


class TokenBatcher:
    """Sample training records with replacement using a checkpointable CPU RNG."""

    def __init__(self, records: list[Record], batch_size: int, seed: int):
        self.records = records
        self.batch_size = batch_size
        self.generator = torch.Generator().manual_seed(seed)

    def next_batch(self, device: torch.device) -> tuple[torch.Tensor, torch.Tensor]:
        indices = torch.randint(len(self.records), (self.batch_size,), generator=self.generator)
        return pack_batch([self.records[index] for index in indices.tolist()], device)
