"""Train the tool-calling architecture on packed next-token windows."""

from collections.abc import Callable
from dataclasses import asdict, dataclass
from hashlib import file_digest, sha256
import json
from logging import Logger
from math import cos, isfinite, pi
import os
from pathlib import Path
import stat
from tempfile import NamedTemporaryFile
from threading import Event
from time import perf_counter, sleep

from model_tokenizer import Tokenizer
from model_training.progress import ProgressCallback, TextGenerationPreview, TrainingProgress, TrainingStarted
import numpy as np
import torch
from torch.nn import functional as F

from .checkpoint import lock_run
from .config import Config
from .forward_trace import log_forward_failure
from .generation import SAMPLE_INTERVAL, create_pretraining_preview
from .model import LanguageModel
from .precision import autocast
from .pretrain_citations import WikipediaCitationFilter

_LATEST = "pretrain-latest.pt"
_BEST = "pretrain-best.pt"
_CHECKPOINT_FORMAT = "llm-from-scratch/tool-calling-pretrain"
_OPTIMIZER = "fused-adamw"
_SOURCES = ("wikipedia", "qa", "fineweb", "arxiv", "youtube")
_FINEWEB_MIX = ("wikipedia", "wikipedia", "wikipedia", "fineweb", "wikipedia",
                "wikipedia", "wikipedia", "fineweb", "wikipedia", "qa")
_ARXIV_MIX = (
    "wikipedia", "fineweb", "arxiv", "wikipedia", "fineweb",
    "qa", "wikipedia", "fineweb", "arxiv", "wikipedia",
    "fineweb", "arxiv", "wikipedia", "fineweb", "qa",
    "wikipedia", "fineweb", "arxiv", "wikipedia", "fineweb",
)
# One 1,000-update cycle, apportioned by packed training tokens.
_MIX_COUNTS = {"wikipedia": 364, "qa": 36, "fineweb": 289, "arxiv": 165, "youtube": 146}


def _make_mix() -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Space each source's updates across the cycle by largest scheduling deficit."""
    total = sum(_MIX_COUNTS.values())
    used = dict.fromkeys(_SOURCES, 0)
    mix, offsets = [], []
    for step in range(1, total + 1):
        source = max(_SOURCES, key=lambda name: step * _MIX_COUNTS[name] - total * used[name])
        mix.append(source)
        offsets.append(used[source])
        used[source] += 1
    return tuple(mix), tuple(offsets)


_MIX, _MIX_OFFSETS = _make_mix()
_TOKEN_DTYPE = np.dtype("<u2")
_IGNORE_TARGET = -100


class _Split:
    """Index model-sized windows within an ordered set of packed shards."""

    def __init__(self, shards: list[np.memmap], context_length: int):
        """Use only complete, non-overlapping windows from each stored row."""
        self.shards = shards
        self.ends = np.cumsum([len(shard) for shard in shards], dtype=np.int64)
        self.context_length = context_length
        stored_context = shards[0].shape[1] - 1
        self.windows_per_row, self.discarded_targets = divmod(stored_context, context_length)
        self.columns = np.arange(context_length + 1, dtype=np.int64)

    def __len__(self) -> int:
        return int(self.ends[-1]) * self.windows_per_row

    def batch(self, indices: np.ndarray, device: torch.device,
              citation_filter: WikipediaCitationFilter | None = None) -> tuple[torch.Tensor, torch.Tensor]:
        """Gather shuffled windows and return shifted inputs and targets."""
        rows = np.empty((len(indices), self.context_length + 1), dtype=np.int64)
        row_ids, slots = np.divmod(indices, self.windows_per_row) if self.windows_per_row > 1 else (indices, None)
        shard_ids = np.searchsorted(self.ends, row_ids, side="right")
        for shard_id in np.unique(shard_ids):
            positions = np.flatnonzero(shard_ids == shard_id)
            start = self.ends[shard_id - 1] if shard_id else 0
            local_rows = row_ids[positions] - start
            shard = self.shards[shard_id]
            if slots is None:
                rows[positions] = shard[local_rows, :self.context_length + 1]
            else:
                starts = slots[positions] * self.context_length
                rows[positions] = shard[local_rows[:, None], starts[:, None] + self.columns]
        padded = False
        if citation_filter is not None:
            target_count = len(rows) * self.context_length
            for row in rows:
                cleaned = citation_filter.clean(row)
                if cleaned is None:
                    continue
                kept = min(len(cleaned), len(row))
                row[:kept] = cleaned[:kept]
                row[kept:] = _IGNORE_TARGET
                padded |= kept < len(row)
                target_count -= self.context_length - max(kept - 1, 0)
            if not target_count:
                raise ValueError("Wikipedia citation filtering left the batch without next-token targets.")
        tokens = torch.from_numpy(rows).to(device)
        inputs = tokens[:, :-1]
        # Byte zero is a valid filler ID. Right padding cannot affect earlier causal predictions.
        if padded:
            inputs = inputs.clamp_min(0)
        return inputs, tokens[:, 1:]


@dataclass(frozen=True)
class _Bundle:
    tokenizer: Tokenizer
    manifest_sha256: str
    base_manifest_sha256: str
    fineweb_manifest_sha256: str
    arxiv_manifest_sha256: str
    tokenizer_sha256: str
    train: dict[str, _Split]
    validation: dict[str, _Split]


def _map_shard(path: Path, rows: int, width: int, digest: str, vocab_size: int,
               stop_event: Event, *, verify_shards: bool) -> np.memmap | None:
    """Check the shard size and optionally scan the same file before mapping it."""
    if not stat.S_ISREG(path.stat().st_mode):
        raise ValueError(f"Expected a regular shard file: {path}.")
    with path.open("rb") as stream:
        expected_bytes = rows * width * _TOKEN_DTYPE.itemsize
        if os.fstat(stream.fileno()).st_size != expected_bytes:
            raise ValueError(f"Shard byte length does not match the manifest: {path}.")
        if verify_shards:
            content_hash = sha256()
            while not stop_event.is_set() and (chunk := stream.read(1024 * 1024)):
                content_hash.update(chunk)
                if int(np.frombuffer(chunk, dtype=_TOKEN_DTYPE).max()) >= vocab_size:
                    raise ValueError(f"Shard contains token IDs outside the tokenizer vocabulary: {path}.")
            if stop_event.is_set():
                return None
            if content_hash.hexdigest() != digest:
                raise ValueError(f"Shard SHA-256 does not match the manifest: {path}.")
        return np.memmap(stream, dtype=_TOKEN_DTYPE, mode="r", shape=(rows, width))


def _load_bundle(data_dir: Path, fineweb_dir: Path, arxiv_dir: Path, youtube_dir: Path,
                 stop_event: Event, *, context_length: int, verify_shards: bool) -> _Bundle | None:
    """Combine matching Wikipedia/Q&A, FineWeb, arXiv and YouTube packs."""
    data_dir, fineweb_dir, arxiv_dir, youtube_dir = (
        path.resolve() for path in (data_dir, fineweb_dir, arxiv_dir, youtube_dir))
    manifest_path = data_dir / "manifest.json"
    try:
        manifest_bytes = manifest_path.read_bytes()
        manifest = json.loads(manifest_bytes)
        if (not isinstance(manifest, dict) or manifest.get("format") != "tool-calling-pretrain-data"
                or type(manifest.get("version")) is not int or manifest["version"] != 1):
            raise ValueError("Expected tool-calling pretraining data format version 1.")
        stored_context = manifest["context_length"]
        if type(stored_context) is not int or stored_context < 1:
            raise ValueError("Expected a positive stored context length.")
        if context_length > stored_context:
            raise ValueError(
                f"Config.context_length is {context_length}, but the bundle stores {stored_context}-token windows. "
                "Select a bundle prepared with windows at least as long as the model context."
            )
        tokenizer_path = data_dir / "tokenizer.json"
        tokenizer_hash = manifest["tokenizer_sha256"]
        with tokenizer_path.open("rb") as stream:
            if file_digest(stream, "sha256").hexdigest() != tokenizer_hash:
                raise ValueError("Tokenizer SHA-256 does not match the manifest.")
        tokenizer = Tokenizer.load(tokenizer_path)
        vocab_size = tokenizer.vocab_size
        with tokenizer_path.open("rb") as stream:
            if file_digest(stream, "sha256").hexdigest() != tokenizer_hash:
                raise ValueError("Tokenizer changed while loading.")
        if vocab_size > np.iinfo(_TOKEN_DTYPE).max + 1:
            raise ValueError("Tokenizer vocabulary does not fit in uint16 shards.")
        sources = manifest["sources"]
        if not isinstance(sources, dict) or set(sources) != {"wikipedia", "qa"}:
            raise ValueError("Expected exactly the wikipedia and qa sources in the base bundle.")
        roots = {"wikipedia": data_dir, "qa": data_dir, "fineweb": fineweb_dir,
                 "arxiv": arxiv_dir, "youtube": youtube_dir}
        base_digest = sha256(manifest_bytes)
        identity = base_digest.digest()
        identities = {}
        for source in ("fineweb", "arxiv", "youtube"):
            root = roots[source]
            extra_bytes = (root / "manifest.json").read_bytes()
            extra = json.loads(extra_bytes)
            for field in ("format", "version", "context_length", "tokenizer_sha256", "end_of_document_id"):
                if not isinstance(extra, dict) or extra.get(field) != manifest[field]:
                    raise ValueError(f"{source} manifest at {root} differs on {field}.")
            with (root / "tokenizer.json").open("rb") as stream:
                if file_digest(stream, "sha256").hexdigest() != tokenizer_hash:
                    raise ValueError(f"{source} tokenizer at {root} does not match the base bundle.")
            if not isinstance(extra["sources"], dict) or set(extra["sources"]) != {source}:
                raise ValueError(f"Expected exactly the {source} source in {root}.")
            sources[source] = extra["sources"][source]
            identity += sha256(extra_bytes).digest()
            identities[source] = sha256(identity).hexdigest()
        splits: dict[str, dict[str, _Split]] = {"train": {}, "validation": {}}
        seen: set[Path] = set()
        for source in _SOURCES:
            root = roots[source]
            for split, by_source in splits.items():
                entries = sources[source][split]
                if not isinstance(entries, list) or not entries:
                    raise ValueError(f"Expected nonempty shard entries for {source} {split}.")
                shards = []
                for entry in entries:
                    if stop_event.is_set():
                        return None
                    name, rows, digest = entry["file"], entry["rows"], entry["sha256"]
                    relative = Path(name)
                    path = (root / relative).resolve()
                    if (relative.is_absolute() or ".." in relative.parts or not path.is_relative_to(root)
                            or path in seen or path.name in ("manifest.json", "tokenizer.json")):
                        raise ValueError(f"Invalid or repeated shard path: {name}.")
                    if type(rows) is not int or rows < 1 or not isinstance(digest, str):
                        raise ValueError(f"Invalid shard metadata for {name}.")
                    shard = _map_shard(path, rows, stored_context + 1, digest, vocab_size, stop_event,
                                       verify_shards=verify_shards)
                    if shard is None:
                        return None
                    seen.add(path)
                    shards.append(shard)
                by_source[source] = _Split(shards, context_length)
        return _Bundle(tokenizer, identities["youtube"], base_digest.hexdigest(),
                       identities["fineweb"], identities["arxiv"], tokenizer_hash,
                       splits["train"], splits["validation"])
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError(f"Invalid pretraining data ({data_dir}, {fineweb_dir}, {arxiv_dir}, {youtube_dir}): {error}") from error


class _ShuffledRows:
    """Rebuild each source's independent epoch permutation from its seed and epoch."""

    def __init__(self, rows: int, seed: int, source_index: int):
        self.rows = rows
        self.seed = seed
        self.source_index = source_index
        self.epoch = -1
        self.permutation = np.empty(0, dtype=np.int64)

    def take(self, cursor: int, count: int) -> np.ndarray:
        """Take a complete batch even when it straddles one or more epoch boundaries."""
        indices = np.empty(count, dtype=np.int64)
        written = 0
        while written < count:
            epoch, offset = divmod(cursor + written, self.rows)
            if epoch != self.epoch:
                rng = np.random.Generator(np.random.PCG64([self.seed, self.source_index, epoch]))
                self.permutation = rng.permutation(self.rows)
                self.epoch = epoch
            size = min(count - written, self.rows - offset)
            indices[written:written + size] = self.permutation[offset:offset + size]
            written += size
        return indices


@dataclass
class _Progress:
    """Counters describe committed Adam updates; skipped attempts never consume rows."""

    step: int = 0
    overflow_skips: int = 0
    validated_step: int = 0
    best_step: int = 0
    best_loss: float | None = None
    last_loss: float = 0.0



def _atomic_save(path: Path, payload: dict) -> None:
    """Replace a checkpoint only after its complete payload has been written."""
    temp = None
    try:
        with NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as output:
            temp = Path(output.name)
            torch.save(payload, output)
        temp.replace(path)
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)


def _initialize_weights(path: Path, metadata: dict, model: LanguageModel, log: Logger) -> None:
    """Load only compatible weights from a latest or best pretraining checkpoint."""
    try:
        saved = torch.load(path, map_location="cpu", weights_only=True)
        source = saved["metadata"]
        if (saved["kind"] not in ("latest", "best")
                or (source["format"], source["version"]) != (metadata["format"], metadata["version"])):
            raise ValueError("Unsupported pretraining checkpoint format.")
        if source["tokenizer_sha256"] != metadata["tokenizer_sha256"]:
            raise ValueError("Checkpoint tokenizer differs from the prepared bundle.")
        model.load_state_dict(saved["model"], strict=True)
    except Exception as error:
        raise ValueError(f"Cannot initialize weights from {path}: {error}") from error
    log.info("Initialized model weights from %s. Starting at step 0 with fresh optimizer state.", path)


def _learning_rate(config: Config, update_tokens: int) -> float:
    """Compute the rate for an update ending at this many committed target tokens."""
    if update_tokens <= config.pretrain_warmup_tokens:
        return config.pretrain_peak_lr * update_tokens / config.pretrain_warmup_tokens
    if update_tokens >= config.pretrain_decay_end_tokens:
        return config.pretrain_final_lr
    fraction = (update_tokens - config.pretrain_warmup_tokens) / (
        config.pretrain_decay_end_tokens - config.pretrain_warmup_tokens
    )
    return config.pretrain_final_lr + (config.pretrain_peak_lr - config.pretrain_final_lr) * (
        1 + cos(pi * fraction)
    ) / 2


def _checkpoint_mix(metadata: dict, bundle: _Bundle) -> str:
    """Recognize only the current mix or exact known predecessor bundles."""
    identity, mix = metadata["manifest_sha256"], metadata.get("mix")
    if identity == bundle.manifest_sha256 and mix == _MIX:
        return "current"
    if identity == bundle.arxiv_manifest_sha256 and mix == _ARXIV_MIX:
        return "arxiv"
    if identity == bundle.fineweb_manifest_sha256 and mix == _FINEWEB_MIX:
        return "fineweb"
    if identity == bundle.base_manifest_sha256 and "mix" not in metadata:
        return "wiki-qa"
    raise ValueError("Cannot resume after changing the prepared bundles or source mix.")


def _mix_cursor(previous: dict, bundle: _Bundle, step: int) -> tuple[int, dict[str, int]]:
    """Recover batch offsets at the start of the current schedule."""
    mix = _checkpoint_mix(previous, bundle)
    if mix in ("current", "arxiv"):
        start, offsets = previous["mix_start_step"], previous["mix_offsets"]
        sources = _SOURCES if mix == "current" else _SOURCES[:-1]
        if (type(start) is not int or not 0 <= start <= step or not isinstance(offsets, dict)
                or set(offsets) != set(sources)
                or any(type(count) is not int or count < 0 for count in offsets.values())
                or sum(offsets.values()) != start):
            raise ValueError("Invalid pretraining mix cursor.")
        if mix == "current":
            return start, offsets
        offsets = {**offsets, "youtube": 0}
        previous_mix = _ARXIV_MIX
    else:
        start = previous["mix_start_step"] if mix == "fineweb" else step
        if type(start) is not int or not 0 <= start <= step:
            raise ValueError("Invalid pretraining mix start step.")
        qa = start // 10
        offsets = {"wikipedia": start - qa, "qa": qa, "fineweb": 0, "arxiv": 0, "youtube": 0}
        previous_mix = _FINEWEB_MIX
    cycles, tail = divmod(step - start, len(previous_mix))
    for source in offsets:
        offsets[source] += cycles * previous_mix.count(source) + previous_mix[:tail].count(source)
    return step, offsets


def _source_batch(step: int, mix_start_step: int, offsets: dict[str, int]) -> tuple[str, int]:
    """Return the source and its next batch index, including pre-cutover batches."""
    cycles, slot = divmod(step - mix_start_step, len(_MIX))
    source = _MIX[slot]
    return source, offsets[source] + cycles * _MIX_COUNTS[source] + _MIX_OFFSETS[slot]


def _restore(path: Path, metadata: dict, bundle: _Bundle, model: LanguageModel,
             optimizer: torch.optim.AdamW, scaler: torch.amp.GradScaler,
             device: torch.device) -> tuple[_Progress, dict] | None:
    """Restore training state and preserve cursors across known mix changes."""
    try:
        try:
            mode = path.lstat().st_mode
        except FileNotFoundError:
            return None
        if not stat.S_ISREG(mode):
            raise ValueError("Expected a regular checkpoint file.")
        saved = torch.load(path, map_location="cpu", weights_only=True)
        previous = saved["metadata"]
        if saved["kind"] != "latest" or any(
            previous[key] != metadata[key]
            for key in ("format", "version", "tokenizer_sha256", "vocab_size")
        ):
            raise ValueError("Checkpoint format or prepared bundle differs.")
        migrated = _checkpoint_mix(previous, bundle) != "current"
        if previous.get("optimizer") != _OPTIMIZER:
            raise ValueError("Checkpoint does not use fused AdamW; set PretrainConfig.init_from to load weights only.")
        if previous["settings"]["context_length"] != metadata["settings"]["context_length"]:
            raise ValueError("Cannot resume after changing Config.context_length.")
        if previous.get("discarded_targets_per_row") != metadata.get("discarded_targets_per_row"):
            raise ValueError("Cannot resume after changing the pretraining window layout.")
        # The sampler derives its row positions from the saved step and these settings.
        for name in ("batch_size", "seed"):
            if previous["settings"][name] != metadata["settings"][name]:
                raise ValueError(f"Cannot preserve the data cursor after changing {name}.")
        for name in ("pretrain_peak_lr", "pretrain_final_lr", "pretrain_warmup_tokens", "pretrain_token_budget"):
            if previous["settings"][name] != metadata["settings"][name]:
                raise ValueError(f"Cannot resume with a changed pretraining schedule ({name}).")
        progress = _Progress(**saved["progress"])
        if (any(type(value) is not int or value < 0 for value in
                (progress.step, progress.overflow_skips, progress.validated_step, progress.best_step))
                or not progress.best_step <= progress.validated_step <= progress.step
                or (progress.best_step == 0) != (progress.best_loss is None)
                or (progress.best_loss is not None and not isfinite(progress.best_loss))
                or not isfinite(progress.last_loss)):
            raise ValueError("Invalid checkpoint counters or loss.")
        metadata["mix_start_step"], metadata["mix_offsets"] = _mix_cursor(previous, bundle, progress.step)
        if migrated:
            # The old weighted validation loss is not comparable.
            progress.best_step = 0
            progress.best_loss = None
        model.load_state_dict(saved["model"], strict=True)
        optimizer.load_state_dict(saved["optimizer"])
        scaler.load_state_dict(saved["scaler"])
        torch.set_rng_state(saved["cpu_rng"])
        torch.cuda.set_rng_state(saved["cuda_rng"], device)
        return progress, previous
    except Exception as error:
        raise ValueError(f"Cannot resume {path}: {error} For a fresh start, change PretrainConfig.run_dir.") from error


def _loss(model: LanguageModel, batch: tuple[torch.Tensor, torch.Tensor],
          reduction: str) -> torch.Tensor:
    """Score shifted targets, excluding padding after removed citations."""
    inputs, targets = batch
    logits = model(inputs)
    return F.cross_entropy(logits.flatten(0, 1), targets.flatten(),
                           ignore_index=_IGNORE_TARGET, reduction=reduction)


def _pace(stop_event: Event, step_delay: Callable[[], float]) -> float:
    """Idle after a unit of GPU work; return the end time for throughput accounting."""
    completed_at = finished_at = perf_counter()
    remaining = step_delay()
    # Re-read live edits during short sleeps without taking the headless signal handler's event lock.
    while remaining > 0 and not stop_event.is_set():
        sleep(min(remaining, 0.1))
        finished_at = perf_counter()
        remaining = step_delay() - (finished_at - completed_at)
    return finished_at


@torch.no_grad()
def _validate(model: LanguageModel, validation: dict[str, _Split], config: Config,
              device: torch.device, stop_event: Event, step_delay: Callable[[], float]) -> dict[str, float] | None:
    """Evaluate fixed, independent held-out samples and weight them like the training mix."""
    model.eval()
    try:
        losses = {}
        for index, source in enumerate(_SOURCES):
            split = validation[source]
            sample_size = min(len(split), config.batch_size * config.eval_batches)
            rng = np.random.Generator(np.random.PCG64([config.seed, index, 0, 1]))
            indices = rng.choice(len(split), size=sample_size, replace=False)
            total = 0.0
            for start in range(0, sample_size, config.batch_size):
                if stop_event.is_set():
                    return None
                batch = split.batch(indices[start:start + config.batch_size], device)
                with autocast():
                    total += _loss(model, batch, "sum").item()
                del batch
                _pace(stop_event, step_delay)
            if not isfinite(total):
                raise FloatingPointError(f"Non-finite {source} validation loss.")
            losses[source] = total / (sample_size * config.context_length)
        return losses
    finally:
        model.train()


def _train(report: ProgressCallback, stop_event: Event, *, log: Logger, run_dir: Path,
           bundle: _Bundle, config: Config, device: torch.device, model: LanguageModel,
           optimizer: torch.optim.AdamW, scaler: torch.amp.GradScaler, sample_prompt: Callable[[], str],
           init_from: Path | None, generation_request: Event | None, step_delay: Callable[[], float]) -> None:
    """Keep the mix, data cursors, validation cadence, and best record stable across resumes."""
    settings = asdict(config)
    del settings["sample_temperature"]  # Preview-only; not part of the training state.
    # Keep the on-disk name for the LR endpoint so saved runs resume unchanged.
    settings["pretrain_token_budget"] = settings.pop("pretrain_decay_end_tokens")
    metadata = {
        "format": _CHECKPOINT_FORMAT,
        "version": 1,
        "optimizer": _OPTIMIZER,
        "settings": settings,
        "manifest_sha256": bundle.manifest_sha256,
        "mix": _MIX,
        "mix_start_step": 0,
        "mix_offsets": dict.fromkeys(_SOURCES, 0),
        "tokenizer_sha256": bundle.tokenizer_sha256,
        "vocab_size": bundle.tokenizer.vocab_size,
    }
    discarded_targets = bundle.train["wikipedia"].discarded_targets
    if discarded_targets:
        # Bind truncated layouts without changing resume identity for exact splits.
        metadata["discarded_targets_per_row"] = discarded_targets
    latest_path = run_dir / _LATEST
    best_path = run_dir / _BEST
    if init_from is not None and any(path.exists() or path.is_symlink() for path in (latest_path, best_path)):
        raise ValueError("PretrainConfig.init_from requires a run directory without checkpoints; set it to None to resume.")
    restored = _restore(latest_path, metadata, bundle, model, optimizer, scaler, device)

    def save_best(weights_metadata: dict) -> None:
        """Publish fine-tunable weights with their architecture and tokenizer identities."""
        _atomic_save(best_path, {
            "kind": "best", "metadata": weights_metadata, "step": progress.best_step,
            "validation_loss": progress.best_loss, "model": model.state_dict(),
        })
        log.info("Saved best weights at step %s (validation loss %.4f): %s",
                 progress.best_step, progress.best_loss, best_path)

    if restored is None:
        if best_path.exists():
            raise ValueError(f"Best weights exist but {latest_path} is missing; change PretrainConfig.run_dir.")
        progress = _Progress()
        if init_from is not None:
            _initialize_weights(init_from, metadata, model, log)
        else:
            log.info("Starting pretraining from scratch.")
    else:
        progress, previous_metadata = restored
        if _checkpoint_mix(previous_metadata, bundle) != "current":
            log.info("Changing the source mix after completed update %s; resetting the best validation loss.",
                     progress.step)
        # Latest is published first. If interrupted before publishing best, latest still
        # contains those exact weights until the run is able to continue.
        if progress.best_step and progress.best_step == progress.step:
            save_best(previous_metadata)
        log.info("Resuming pretraining at completed update %s.", progress.step)
    report(TrainingStarted(progress.step))
    mix_start_step = metadata["mix_start_step"]
    mix_offsets = metadata["mix_offsets"]

    saved = asdict(progress)

    def save_latest() -> None:
        """Commit model, optimizer, scaler, RNGs, and derived cursor inputs together."""
        nonlocal saved
        saved = asdict(progress)
        _atomic_save(latest_path, {
            "kind": "latest", "metadata": metadata, "progress": saved,
            "model": model.state_dict(), "optimizer": optimizer.state_dict(),
            "scaler": scaler.state_dict(), "cpu_rng": torch.get_rng_state(),
            "cuda_rng": torch.cuda.get_rng_state(device),
        })
        log.info("Saved latest checkpoint at step %s: %s", progress.step, latest_path)

    tokens_per_step = config.batch_size * config.context_length
    citation_filter = WikipediaCitationFilter(bundle.tokenizer)
    log.info("Training mix: %s.", ", ".join(
        f"{source} {100 * count / len(_MIX):.1f}%" for source, count in _MIX_COUNTS.items()))
    log.info("Filtering numeric citations from Wikipedia training windows; validation is unchanged.")
    log.info("Pretraining runs until stopped; warmup: %s tokens, peak LR %g, floor %g from %s tokens.",
             config.pretrain_warmup_tokens, config.pretrain_peak_lr, config.pretrain_final_lr,
             config.pretrain_decay_end_tokens)
    initial_delay = step_delay()
    if initial_delay:
        log.info("Pretraining slowdown: %g seconds of idle time after each update and validation batch.", initial_delay)

    def validate_if_due() -> dict[str, float]:
        """Retry a due validation on resume if Stop interrupted it before completion."""
        step = progress.step
        if (step <= max(progress.validated_step, mix_start_step)
                or (step != mix_start_step + 1 and step % config.eval_interval)
                or stop_event.is_set()):
            return {}
        losses = _validate(model, bundle.validation, config, device, stop_event, step_delay)
        if losses is None:
            return {}
        weighted = sum(losses[source] * count for source, count in _MIX_COUNTS.items()) / len(_MIX)
        progress.validated_step = step
        log.info("Step %s validation loss %.4f (%s)", step, weighted,
                 ", ".join(f"{source} {loss:.4f}" for source, loss in losses.items()))
        if progress.best_loss is None or weighted < progress.best_loss:
            progress.best_loss = weighted
            progress.best_step = step
            save_latest()
            save_best(metadata)
        return {"validation loss": weighted, **{f"validation {name} loss": loss for name, loss in losses.items()}}

    samplers = {source: _ShuffledRows(len(bundle.train[source]), config.seed, index)
                for index, source in enumerate(_SOURCES)}
    last_reported = progress.step
    first_step = progress.step + 1
    measured_steps = 0
    measured_seconds = 0.0
    scale = scaler.get_scale()
    model.train()
    resumed_validation = validate_if_due()
    if resumed_validation:
        report(TrainingProgress(progress.step, None, resumed_validation))
    validation_metrics = {}
    while not stop_event.is_set():
        started = perf_counter()
        source, source_batch = _source_batch(progress.step, mix_start_step, mix_offsets)
        cursor = source_batch * config.batch_size
        rows = samplers[source].take(cursor, config.batch_size)
        batch = bundle.train[source].batch(rows, device, citation_filter if source == "wikipedia" else None)
        learning_rate = _learning_rate(config, (progress.step + 1) * tokens_per_step)
        for group in optimizer.param_groups:
            group["lr"] = learning_rate
        # A skipped update retries the same rows and learning rate.
        while not stop_event.is_set():
            with autocast():
                loss = _loss(model, batch, "mean")
            loss_value = loss.item()
            if not isfinite(loss_value):
                del loss
                log.error("Tracing non-finite loss %s before update %s (%s, rows %s).",
                          loss_value, progress.step + 1, source, rows.tolist())
                with autocast():
                    log_forward_failure(model, lambda: _loss(model, batch, "mean"), log)
                raise FloatingPointError(f"Non-finite pretraining loss before update {progress.step + 1}.")
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad(set_to_none=True)
            del loss
            new_scale = scaler.get_scale()
            if new_scale <= 0 or not isfinite(new_scale):
                raise FloatingPointError(f"Invalid FP16 loss scale before update {progress.step + 1}.")
            skipped = new_scale < scale
            scale = new_scale
            if skipped:
                progress.overflow_skips += 1
                log.info("FP16 overflow before update %s; retrying %s batch.", progress.step + 1, source)
                continue
            progress.step += 1
            progress.last_loss = loss_value
            measured_steps += 1
            break
        else:
            break
        del batch
        measured_seconds += _pace(stop_event, step_delay) - started
        validation_metrics = validate_if_due()
        stopping = stop_event.is_set()
        if (stopping or progress.step % config.checkpoint_interval == 0) and progress.step != saved["step"]:
            save_latest()
        if progress.step == first_step or progress.step % config.eval_interval == 0 or stopping:
            _report_training(report, log, progress, tokens_per_step, learning_rate,
                             measured_steps, measured_seconds, validation_metrics)
            last_reported = progress.step
            measured_steps = 0
            measured_seconds = 0.0
        if stopping:
            continue
        requested = generation_request is not None and generation_request.is_set()
        if requested:
            generation_request.clear()
        if requested or progress.step == first_step or progress.step % SAMPLE_INTERVAL == 0:
            preview = create_pretraining_preview(
                model, bundle.tokenizer, sample_prompt(), config, device, progress.step, stop_event,
                fresh=requested,
            )
            if preview is not None and not stop_event.is_set():
                report(TrainingProgress(progress.step, None, {}, preview))

    if asdict(progress) != saved:
        save_latest()
    if progress.step > last_reported:
        _report_training(report, log, progress, tokens_per_step,
                         _learning_rate(config, progress.step * tokens_per_step),
                         measured_steps, measured_seconds, validation_metrics)


def _report_training(report: ProgressCallback, log: Logger, progress: _Progress, tokens_per_step: int,
                     learning_rate: float, measured_steps: int, seconds: float,
                     validation_metrics: dict[str, float]) -> None:
    """Report loss and recent successful-target throughput."""
    tokens_per_second = measured_steps * tokens_per_step / seconds
    log.info("Step %s loss %.4f, LR %g, %.0f tokens/s",
             progress.step, progress.last_loss, learning_rate, tokens_per_second)
    report(TrainingProgress(progress.step, None, {
        "loss": progress.last_loss, "tokens/s": tokens_per_second,
        "completed tokens": progress.step * tokens_per_step, "overflow skips": progress.overflow_skips,
        "learning rate": learning_rate,
        **validation_metrics,
    }))


def generate_pretraining_example(prompt: str, *, data_dir: Path, fineweb_dir: Path, arxiv_dir: Path,
                                 youtube_dir: Path, run_dir: Path) -> TextGenerationPreview:
    """Sample from the latest committed pretraining weights without changing the run."""
    path = run_dir / _LATEST
    if not path.is_file():
        raise ValueError(f"No pretraining checkpoint at {path}. Start training first.")
    if not torch.cuda.is_available():
        raise RuntimeError("Tool-calling generation requires CUDA.")
    device = torch.device("cuda", torch.cuda.current_device())
    stop = Event()
    config = Config()
    bundle = _load_bundle(data_dir, fineweb_dir, arxiv_dir, youtube_dir, stop, context_length=config.context_length,
                          verify_shards=False)
    assert bundle is not None  # This display-only operation has no stop request.
    saved = torch.load(path, map_location="cpu", weights_only=True, mmap=True)
    metadata = saved["metadata"]
    if (saved["kind"] != "latest" or metadata["format"] != _CHECKPOINT_FORMAT
            or metadata["version"] != 1 or metadata["tokenizer_sha256"] != bundle.tokenizer_sha256):
        raise ValueError(f"Checkpoint format or prepared bundle differs at {path}.")
    _checkpoint_mix(metadata, bundle)
    if metadata["settings"]["context_length"] != config.context_length:
        raise ValueError(f"Checkpoint context differs from Config.context_length at {path}.")
    model = LanguageModel(bundle.tokenizer.vocab_size, config).to(device)
    model.load_state_dict(saved["model"])
    step = saved["progress"]["step"]
    del saved
    preview = create_pretraining_preview(model, bundle.tokenizer, prompt, config, device, step, stop, fresh=True)
    assert preview is not None
    return preview


def run_pretraining(report: ProgressCallback, stop_event: Event, *, data_dir: Path, fineweb_dir: Path,
                    arxiv_dir: Path, youtube_dir: Path, run_dir: Path, log: Logger, sample_prompt: Callable[[], str],
                    step_delay: Callable[[], float],
                    verify_shards: bool = False, init_from: Path | None = None,
                    generation_request: Event | None = None) -> None:
    """Run resumable CUDA FP16/fused AdamW pretraining until stopped."""
    initial_delay = step_delay()
    if not isfinite(initial_delay) or initial_delay < 0:
        raise ValueError("PretrainConfig.step_delay_seconds must be finite and nonnegative.")
    if stop_event.is_set():
        return
    if not torch.cuda.is_available():
        raise RuntimeError("Tool-calling pretraining requires CUDA.")
    device = torch.device("cuda", torch.cuda.current_device())
    with lock_run(run_dir):
        log.info("Opening pretraining data: %s, %s, %s and %s (full shard verification %s)",
                 data_dir, fineweb_dir, arxiv_dir, youtube_dir, "on" if verify_shards else "off")
        config = Config()
        bundle = _load_bundle(data_dir, fineweb_dir, arxiv_dir, youtube_dir, stop_event, context_length=config.context_length,
                              verify_shards=verify_shards)
        if bundle is None or stop_event.is_set():
            return
        torch.manual_seed(config.seed)
        model = LanguageModel(bundle.tokenizer.vocab_size, config).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=config.pretrain_peak_lr, fused=True)
        scaler = torch.amp.GradScaler("cuda")
        log.info("%s, FP16 autocast, fused AdamW, %s parameters, context %s, batch size %s",
                 device, sum(parameter.numel() for parameter in model.parameters()), config.context_length,
                 config.batch_size)
        _train(report, stop_event, log=log, run_dir=run_dir, bundle=bundle, config=config,
               device=device, model=model, optimizer=optimizer, scaler=scaler, sample_prompt=sample_prompt,
               init_from=init_from, generation_request=generation_request, step_delay=step_delay)
