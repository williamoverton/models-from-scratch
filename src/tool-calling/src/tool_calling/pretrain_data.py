"""Prepare hash-bound, packed next-token data from local Wikipedia and Q&A."""

from array import array
from collections import deque
from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from contextlib import ExitStack, closing
from functools import lru_cache
import gzip
from hashlib import file_digest, sha256
from heapq import heapify, heappop, heappush
from html.parser import HTMLParser
from itertools import islice
import json
from multiprocessing import get_context
from pathlib import Path
from shutil import copyfile
from sys import byteorder
from tempfile import TemporaryDirectory
from time import monotonic
from typing import BinaryIO

from model_tokenizer import Tokenizer
from model_tokenizer.pretokenization import split_chunks
import numpy as np
import pyarrow.parquet as pq

from .framing import _Control

_MANIFEST_FORMAT = "tool-calling-pretrain-data"
_MANIFEST_VERSION = 1
_ROWS_PER_SHARD = 65_536
_VALIDATION_WINDOWS = 1024
_VALIDATION_MODULUS = 100
_QA_OPEN_SHARDS = 32
_QA_RECORDS_PER_TURN = 8
_TASK_BYTES = 512 * 1024
_TASK_RECORDS = 256
_IGNORED_HTML = frozenset({"aside", "footer", "head", "nav", "script", "style", "template"})
_BLOCK_HTML = frozenset({
    "article", "blockquote", "br", "caption", "dd", "div", "dl", "dt", "figcaption",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "li", "main", "ol", "p", "pre",
    "section", "table", "td", "th", "tr", "ul",
})


class _ArticleText(HTMLParser):
    """Extract readable article text while retaining paragraph breaks."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _IGNORED_HTML:
            self._ignored.append(tag)
        elif not self._ignored and tag in _BLOCK_HTML:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._ignored:
            if tag == self._ignored[-1]:
                self._ignored.pop()
        elif tag in _BLOCK_HTML:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._ignored:
            self.parts.append(data)

    def text(self) -> str:
        lines = (" ".join(line.split()) for line in "".join(self.parts).splitlines())
        return "\n".join(line for line in lines if line)


def _zim_records(path: Path) -> Iterator[tuple[str, str, bytes]]:
    """Read article HTML in physical order, leaving parsing to workers."""
    # https://python-libzim.readthedocs.io/en/latest/api_reference/libzim.reader/
    try:
        from libzim.reader import Archive
    except ImportError as exc:
        raise RuntimeError("Reading a .zim archive requires libzim (uv run --with libzim).") from exc

    if not hasattr(Archive, "iter_efficient"):
        raise RuntimeError("Upgrade libzim for ZIM iteration (uv run --with 'libzim>=4.1').")
    archive = Archive(path)
    # Physical read order avoids repeatedly decompressing clusters when titles
    # are scattered through the archive. The article path, not order, splits it.
    for entry in archive.iter_efficient():
        if entry.is_redirect:
            continue
        item = entry.get_item()
        if item.mimetype.split(";", 1)[0] != "text/html":
            continue
        yield entry.path, entry.title, bytes(item.content)


def _parquet_records(path: Path) -> Iterator[tuple[str, str]]:
    with pq.ParquetFile(path) as parquet:
        columns = ["id", "title", "text"]
        if not set(columns).issubset(parquet.schema_arrow.names):
            raise ValueError(f"{path}: Wikipedia Parquet requires id, title, and text columns.")
        row_number = 0
        for batch in parquet.iter_batches(batch_size=1024, columns=columns):
            for record in batch.to_pylist():
                row_number += 1
                document_id, title, text = record["id"], record["title"], record["text"]
                if (type(document_id) not in (str, int) or document_id == ""
                        or not isinstance(title, str) or not isinstance(text, str)):
                    raise ValueError(f"{path}: row {row_number} requires an ID and string title/text.")
                title, text = title.strip(), text.strip()
                if text:
                    yield str(document_id), f"{title}\n\n{text}" if title else text


def _qa_file_records(path: Path) -> Iterator[tuple[str, str]]:
    open_text = gzip.open if path.suffix.lower() == ".gz" else open
    with open_text(path, "rt", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: {exc.msg}") from exc
            if isinstance(record, dict):
                question, answer = record.get("title_body"), record.get("upvoted_answer")
            elif isinstance(record, list) and len(record) == 2:
                question, answer = record
            else:
                raise ValueError(f"{path}:{line_number}: expected a Q&A object or pair.")
            if not isinstance(question, str) or not isinstance(answer, str):
                raise ValueError(f"{path}:{line_number}: expected two Q&A strings.")
            question, answer = question.strip(), answer.strip()
            if question and answer:
                # Raw shards have no ID. Group the same question even if
                # duplicated across files with different top answers.
                yield " ".join(question.split()).casefold(), f"Question: {question}\n\nAnswer: {answer}"


def _qa_records(files: list[Path]) -> Iterator[tuple[str, str]]:
    # Spread each group across sorted filenames and interleave short runs so a
    # capped corpus spans many communities without unbounded open descriptors.
    groups = (len(files) + _QA_OPEN_SHARDS - 1) // _QA_OPEN_SHARDS
    for group in range(groups):
        with ExitStack() as stack:
            active = [
                stack.enter_context(closing(_qa_file_records(path)))
                for path in files[group::groups]
            ]
            while active:
                remaining = []
                for records in active:
                    count = 0
                    for count, record in enumerate(islice(records, _QA_RECORDS_PER_TURN), 1):
                        yield record
                    if count == _QA_RECORDS_PER_TURN:
                        remaining.append(records)
                active = remaining


def _chunk_encoder(tokenizer: Tokenizer) -> Callable[[bytes], tuple[int, ...]]:
    """Encode repeated byte chunks without scanning every merge rule."""
    ranks = dict(tokenizer.merges)

    def merge_chunk(chunk: bytes) -> tuple[int, ...]:
        if len(chunk) <= 1:
            return tuple(chunk)
        if len(chunk) == 2:
            rank = ranks.get((chunk[0], chunk[1]))
            return tuple(chunk) if rank is None else (rank,)
        queue = [(rank, index) for index, pair in enumerate(zip(chunk, chunk[1:]))
                 if (rank := ranks.get(pair)) is not None]
        if not queue:
            return tuple(chunk)

        # New token IDs are merge ranks: each rule can introduce only pairs with
        # higher ranks. Equal-ranked overlaps merge left-to-right, just as in the
        # tokenizer's full rule scan. Update only the two neighboring pairs.
        heapify(queue)
        size = len(chunk)
        tokens = list(chunk)
        after = list(range(1, size + 1))
        before = list(range(-1, size - 1))
        while queue:
            rank, left = heappop(queue)
            right = after[left]
            if right == size or ranks.get((tokens[left], tokens[right])) != rank:
                continue
            previous, following = before[left], after[right]
            tokens[left] = rank
            after[left] = following
            after[right] = size
            if previous >= 0:
                if (neighbor := ranks.get((tokens[previous], rank))) is not None:
                    heappush(queue, (neighbor, previous))
            if following != size:
                before[following] = left
                if (neighbor := ranks.get((rank, tokens[following]))) is not None:
                    heappush(queue, (neighbor, left))

        result = []
        index = 0
        while index != size:
            result.append(tokens[index])
            index = after[index]
        return tuple(result)

    cached = lru_cache(maxsize=131_072)(merge_chunk)

    def encode(chunk: bytes) -> tuple[int, ...]:
        return cached(chunk) if len(chunk) <= 128 else merge_chunk(chunk)

    return encode


class _WindowWriter:
    """Write fixed-width token windows with a shared boundary token."""

    def __init__(self, directory: Path, name: str, width: int, limit: int | None) -> None:
        self._directory = directory
        self._name = name
        self._width = width
        self._limit = limit
        self._pending = b""
        self._stream: BinaryIO | None = None
        self._digest = sha256()
        self._file = ""
        self._rows = 0
        self.total = 0
        self.shards: list[dict] = []

    @property
    def full(self) -> bool:
        return self._limit is not None and self.total == self._limit

    def append(self, encoded: bytes) -> None:
        """Append a stream segment, retaining the token shared by adjacent windows."""
        if not encoded or self.full:
            return
        tokens = np.frombuffer(self._pending + encoded, dtype="<u2")
        if len(tokens) < self._width:
            self._pending = tokens.tobytes()
            return
        stride = self._width - 1
        windows = np.lib.stride_tricks.sliding_window_view(tokens, self._width)[::stride]
        if self._limit is not None:
            windows = windows[:self._limit - self.total]
        self._pending = b""
        if self._limit != self.total + len(windows):
            self._pending = tokens[len(windows) * stride:].tobytes()
        while len(windows):
            if self._stream is None:
                self._file = f"{self._name}-{len(self.shards):06}.bin"
                self._stream = (self._directory / self._file).open("xb", buffering=1024 * 1024)
            count = min(len(windows), _ROWS_PER_SHARD - self._rows)
            contents = windows[:count].tobytes()
            self._stream.write(contents)
            self._digest.update(contents)
            self._rows += count
            self.total += count
            windows = windows[count:]
            if self._rows == _ROWS_PER_SHARD:
                self.close()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
            self.shards.append({"file": self._file, "rows": self._rows, "sha256": self._digest.hexdigest()})
            self._rows = 0
            self._digest = sha256()


type _Record = tuple[str, str] | tuple[str, str, bytes]
_encoder: Callable[[bytes], tuple[int, ...]]
_eod: int


def _init_worker(tokenizer_path: Path, eod: int) -> None:
    """Build a private bounded encode cache in each process."""
    global _encoder, _eod
    _encoder = _chunk_encoder(Tokenizer.load(tokenizer_path))
    _eod = eod


def _encode_records(source: str, records: list[_Record],
                    include_train: bool, include_validation: bool) -> tuple[bytes, bytes]:
    """Split by document and encode each stream in input order."""
    train, validation = array("H"), array("H")
    prefix = source.encode("ascii") + b"\0"
    for document_id, text, *html in records:
        bucket = int.from_bytes(sha256(prefix + document_id.encode("utf-8")).digest()[:8], "big")
        held_out = bucket % _VALIDATION_MODULUS == 0
        if not (include_validation if held_out else include_train):
            continue
        if html:
            parser = _ArticleText()
            parser.feed(html[0].decode("utf-8", errors="replace"))
            parser.close()
            title, text = text.strip(), parser.text()
            if not text:
                continue
            if title:
                text = f"{title}\n\n{text}"
        tokens = validation if held_out else train
        for chunk in split_chunks(text):
            tokens.extend(_encoder(chunk))
        tokens.append(_eod)
    if byteorder != "little":
        train.byteswap()
        validation.byteswap()
    return train.tobytes(), validation.tobytes()


def _record_batches(records: Iterator[_Record]) -> Iterator[list[_Record]]:
    """Bound in-flight data by input size as well as document count."""
    batch: list[_Record] = []
    size = 0
    for record in records:
        batch.append(record)
        size += sum(map(len, record))
        if size >= _TASK_BYTES or len(batch) >= _TASK_RECORDS:
            yield batch
            batch, size = [], 0
    if batch:
        yield batch


def _pack_source(
    directory: Path,
    source: str,
    records: Iterator[_Record],
    pool: ProcessPoolExecutor,
    workers: int,
    width: int,
    limits: dict[str, int | None],
) -> dict:
    """Feed workers concurrently and write their results in source order."""
    train = _WindowWriter(directory, f"{source}-train", width, limits["train"])
    validation = _WindowWriter(directory, f"{source}-validation", width, limits["validation"])
    batches = _record_batches(records)
    pending = deque()
    last_report = monotonic()
    print(f"Preparing {source} with {workers} workers.", flush=True)
    with closing(train), closing(validation):
        try:
            while not (train.full and validation.full):
                while len(pending) < 2 * workers and (batch := next(batches, None)) is not None:
                    pending.append(pool.submit(_encode_records, source, batch, not train.full, not validation.full))
                if not pending:
                    break
                train_ids, validation_ids = pending.popleft().result()
                train.append(train_ids)
                validation.append(validation_ids)
                if monotonic() - last_report >= 30:
                    print(f"{source}: {train.total:,} train / {validation.total:,} validation windows", flush=True)
                    last_report = monotonic()
        finally:
            for job in pending:
                job.cancel()
    for split, writer in (("train", train), ("validation", validation)):
        if not writer.total:
            raise ValueError(f"{source}: no complete {split} windows of {width} tokens were found.")
    print(f"Finished {source}: {train.total:,} train / {validation.total:,} validation windows", flush=True)
    return {"train": train.shards, "validation": validation.shards}


def _provenance(path: Path, adapter: str, files: list[Path]) -> dict:
    inputs = []
    for file in files:
        stat = file.stat()
        inputs.append({"file": file.name, "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns})
    return {"adapter": adapter, "path": str(path), "files": inputs}


def prepare_pretraining(
    output_dir: Path,
    *,
    tokenizer_path: Path,
    wikipedia: Path,
    qa: Path,
    context_length: int,
    windows_per_source: int | None,
    workers: int,
) -> dict:
    """Publish a new corpus directory with the original tokenizer and bin shards."""
    if type(context_length) is not int or context_length <= 0:
        raise ValueError("context_length must be a positive integer.")
    if type(workers) is not int or workers <= 0:
        raise ValueError("workers must be a positive integer.")
    if windows_per_source is not None and (
        type(windows_per_source) is not int or windows_per_source <= 0
    ):
        raise ValueError("windows_per_source must be a positive integer or None.")
    if output_dir.exists() or output_dir.is_symlink():
        raise FileExistsError(f"Output directory already exists: {output_dir}")

    # Choose adapters from the supplied paths before resolving any symlinks.
    wikipedia_suffix = wikipedia.suffix.lower()
    if not wikipedia.is_file() or wikipedia_suffix not in {".zim", ".parquet"}:
        raise ValueError(f"Wikipedia input must be a .zim or .parquet file: {wikipedia}")
    if qa.is_dir():
        qa_files = sorted(path for path in qa.glob("*.jsonl.gz") if path.is_file())
        if not qa_files:
            raise ValueError(f"No .jsonl.gz input files found in {qa}.")
    elif qa.is_file() and qa.name.lower().endswith((".jsonl", ".jsonl.gz")):
        qa_files = [qa]
    else:
        raise ValueError(f"Q&A input must be a JSONL file or directory of .jsonl.gz files: {qa}")

    limits = {
        "train": windows_per_source,
        "validation": min(_VALIDATION_WINDOWS, windows_per_source)
        if windows_per_source is not None else _VALIDATION_WINDOWS,
    }
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=output_dir.parent, prefix=".tool-calling-pretrain-") as temporary:
        staging = Path(temporary) / "bundle"
        staging.mkdir()
        frozen_tokenizer = staging / "tokenizer.json"
        copyfile(tokenizer_path, frozen_tokenizer)
        tokenizer = Tokenizer.load(frozen_tokenizer)
        if tokenizer.vocab_size > 2**16:
            raise ValueError("The tokenizer vocabulary is too large for uint16 pretraining data.")
        eod = tokenizer.control_token_ids.get(_Control.END_OF_DOCUMENT)
        if eod is None:
            raise ValueError("The pretraining tokenizer must register <END_OF_DOCUMENT>.")
        with frozen_tokenizer.open("rb") as stream:
            tokenizer_sha256 = file_digest(stream, "sha256").hexdigest()
        wikipedia_records = _zim_records if wikipedia_suffix == ".zim" else _parquet_records
        sources = {}
        with ProcessPoolExecutor(max_workers=workers, mp_context=get_context("spawn"),
                                 initializer=_init_worker, initargs=(frozen_tokenizer, eod)) as pool:
            for source, path, adapter, files, records in (
                ("wikipedia", wikipedia, wikipedia_suffix[1:], [wikipedia], wikipedia_records(wikipedia)),
                ("qa", qa, "jsonl", qa_files, _qa_records(qa_files)),
            ):
                provenance = _provenance(path.resolve(), adapter, files)
                with closing(records):
                    splits = _pack_source(staging, source, records, pool, workers, context_length + 1, limits)
                sources[source] = {**splits, "provenance": provenance}

        manifest = {
            "format": _MANIFEST_FORMAT,
            "version": _MANIFEST_VERSION,
            "context_length": context_length,
            "tokenizer_sha256": tokenizer_sha256,
            "end_of_document_id": eod,
            "window_limits": limits,
            "split": {"algorithm": "sha256-source-nul-id-first-8-be", "validation_modulus": _VALIDATION_MODULUS},
            "sources": sources,
        }
        with (staging / "manifest.json").open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        if output_dir.exists() or output_dir.is_symlink():
            raise FileExistsError(f"Output directory already exists: {output_dir}")
        staging.rename(output_dir)
    return manifest
