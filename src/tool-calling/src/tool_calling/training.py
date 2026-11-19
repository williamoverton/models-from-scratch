"""Train, validate, checkpoint, and publish fixed previews from the Textual worker."""

from logging import Logger
from math import isfinite
from pathlib import Path
from threading import Event
from time import perf_counter

from model_training.progress import ProgressCallback, TrainingProgress
import torch

from .batching import TokenBatcher, load_bundle
from .checkpoint import CHECKPOINT_NAME, lock_run, read_checkpoint, restore_checkpoint, save_checkpoint
from .config import Config
from .generation import SAMPLE_INTERVAL, create_preview
from .model import LanguageModel
from .precision import autocast
from .validation import Validation, stage_masks, token_losses


def _stage_metrics(losses, masks, split: str) -> dict[str, float]:
    metrics = {}
    for name, mask in masks.items():
        count = mask.sum().item()
        if count:
            metrics[f"{split} {name} loss"] = losses.masked_fill(~mask, 0).sum().item() / count
    return metrics


def _add_validation_metrics(result, metrics: dict[str, float], log: Logger, step: int) -> None:
    stages, schemas, (correct, evaluated) = result
    for stage, (total, count) in stages.items():
        name = "validation loss" if stage == "overall" else f"validation {stage} loss"
        if count:
            metrics[name] = total / count
        log.info("Step %s validation %s: %s (%s targets)", step, stage,
                 f"{total / count:.4f}" if count else "absent", count)
    metrics["greedy tool names correct"] = correct
    metrics["greedy tool names evaluated"] = evaluated
    if evaluated:
        metrics["greedy tool-name accuracy"] = correct / evaluated
    for schema, (total, count, samples) in sorted(schemas.items()):
        log.info("Step %s validation schema %s: %.4f (%s targets, %s samples)",
                 step, schema, total / count, count, samples)


def run_training(report: ProgressCallback, stop_event: Event, *, data_dir: Path, run_dir: Path,
                 steps: int, log: Logger) -> None:
    """Bind a run to one verified bundle and stop between completed optimizer updates."""
    if stop_event.is_set():
        return
    if not torch.cuda.is_available():
        raise RuntimeError("Tool-calling training requires CUDA.")
    device = torch.device("cuda", torch.cuda.current_device())
    with lock_run(run_dir):
        log.info("Checking prepared data bundle: %s", data_dir)
        bundle = load_bundle(data_dir, stop_event)
        if bundle is None:
            return
        config = Config(context_length=bundle.context_length, training_steps=steps)
        path = run_dir / CHECKPOINT_NAME
        state = read_checkpoint(path, config, bundle.manifest_digest)
        if stop_event.is_set():
            return
        torch.manual_seed(config.seed)
        model = LanguageModel(bundle.tokenizer.vocab_size, config).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=config.learning_rate)
        scaler = torch.amp.GradScaler("cuda")
        batcher = TokenBatcher(bundle.train, config.batch_size, config.seed)
        step = 0
        if state is not None:
            restore_checkpoint(path, state, model, optimizer, scaler, batcher, device)
            step = state["step"]
            del state
        log.info("%s at step %s: %s, FP16 mixed precision, Adam, %s parameters, context %s, %s train / %s validation rows",
                 "Fresh run" if step == 0 else "Resuming", step, device,
                 sum(parameter.numel() for parameter in model.parameters()), config.context_length,
                 len(bundle.train), len(bundle.validation))
        tokenizer, manifest_digest = bundle.tokenizer, bundle.manifest_digest
        validation = Validation(bundle.validation, tokenizer, config, stop_event)
        del bundle  # Validation retains only the selected records and tool-name prefixes.
        _train(report, stop_event, log, path, manifest_digest, config, device,
               model, batcher, tokenizer, optimizer, scaler, validation, step)


def _train(report, stop_event, log, path, manifest_digest, config, device, model,
           batcher, tokenizer, optimizer, scaler, validation, start_step):
    model.train()
    step = saved_step = reported_step = start_step
    previous_scale = scaler.get_scale()
    overflow_skips = 0
    last_loss = 0.0
    measured_seconds = 0.0
    measured_steps = 0

    def save_latest() -> None:
        nonlocal saved_step
        save_checkpoint(path, model, optimizer, scaler, batcher, config, step, manifest_digest, device)
        saved_step = step
        log.info("Saved checkpoint at step %s: %s", step, path)

    while step < config.training_steps and not stop_event.is_set():
        started = perf_counter()
        inputs, targets = batcher.next_batch(device)
        with autocast():
            logits = model(inputs)
            loss = token_losses(logits, targets, "mean")
        loss_value = loss.item()
        if not isfinite(loss_value):
            raise FloatingPointError(f"Non-finite training loss before update {step + 1}.")
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad(set_to_none=True)
        # GradScaler lowers its scale when it skips the Adam update.
        scale = scaler.get_scale()
        if scale <= 0:
            raise FloatingPointError(f"FP16 loss scale underflow before update {step + 1}.")
        skipped = scale < previous_scale
        previous_scale = scale
        del loss, inputs
        if skipped:
            overflow_skips += 1
            log.info("FP16 overflow before update %s; skipped the Adam update.", step + 1)
            del logits, targets
            continue

        step += 1
        last_loss = loss_value
        first = step == start_step + 1
        final = step == config.training_steps
        diagnostics_due = first or final or step % config.eval_interval == 0
        preview_due = first or final or step % SAMPLE_INTERVAL == 0
        checkpoint_due = final or step % config.checkpoint_interval == 0
        if diagnostics_due or preview_due or checkpoint_due or stop_event.is_set():
            torch.cuda.synchronize(device)
        measured_seconds += perf_counter() - started
        measured_steps += 1

        metrics = None
        if diagnostics_due or stop_event.is_set():
            metrics = {"loss": last_loss, "average update ms": 1000 * measured_seconds / measured_steps}
            metrics["overflow skips (this start)"] = overflow_skips
            measured_seconds = 0.0
            measured_steps = 0
            if diagnostics_due and not stop_event.is_set():
                with torch.no_grad(), autocast():
                    losses = token_losses(logits, targets, "none").reshape_as(targets)
                    masks = stage_masks(targets, tokenizer)
                    metrics.update(_stage_metrics(losses, {name: masks[name] for name in ("call", "answer")},
                                                  "training"))
                del losses, masks
        del logits, targets

        if diagnostics_due and not stop_event.is_set():
            result = validation.evaluate(model, device, stop_event)
            if result is not None:
                _add_validation_metrics(result, metrics, log, step)
        if checkpoint_due or stop_event.is_set():
            save_latest()
        if metrics is not None:
            report(TrainingProgress(step, config.training_steps, metrics))
            reported_step = step
        if preview_due and not stop_event.is_set():
            preview = create_preview(model, tokenizer, config, device, step, stop_event)
            if preview is not None and not stop_event.is_set():
                report(TrainingProgress(step, config.training_steps, {}, preview))

    # An early Stop/Quit may land after an update but outside any checkpoint boundary.
    if step > saved_step:
        save_latest()
    if step > reported_step:
        report(TrainingProgress(step, config.training_steps, {"loss": last_loss}))
