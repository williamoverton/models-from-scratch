"""Run a tool-calling training worker without a terminal UI."""

import logging
from os import getpid
from pathlib import Path
import signal
from threading import Event

from model_training.progress import TextGenerationPreview, TrainingProgress


def run_headless(train, log_path: Path) -> int:
    """Stream progress and request a checkpointed stop on SIGINT or SIGTERM."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    stop_event = Event()
    logger = logging.Logger("tool-calling", level=logging.INFO)

    def stop(_signum, _frame) -> None:
        stop_event.set()

    def report(progress: TrainingProgress) -> None:
        if progress.metrics:
            metrics = ", ".join(f"{name}={value:.6g}" for name, value in progress.metrics.items())
            logger.info("Step %s: %s", progress.step, metrics)
        if isinstance(progress.preview, TextGenerationPreview):
            for example in progress.preview.examples:
                logger.info("Sample step %s (%s): %r + %r", progress.preview.step,
                            example.label, example.context, example.completion)

    handlers = (logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8"))
    for handler in handlers:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    previous = {sig: signal.signal(sig, stop) for sig in (signal.SIGINT, signal.SIGTERM)}
    try:
        logger.info("Starting headless training (PID %s).", getpid())
        train(report, stop_event, log=logger)
        logger.info("Training stopped." if stop_event.is_set() else "Training completed.")
        return 0
    except Exception:
        logger.exception("Training failed")
        return 1
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)
        for handler in handlers:
            handler.close()
