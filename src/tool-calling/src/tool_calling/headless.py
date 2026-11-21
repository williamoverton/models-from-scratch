"""Run a tool-calling training worker without a terminal UI."""

from contextlib import ExitStack, closing
import logging
from os import getpid
from pathlib import Path
import signal
from threading import Event

from model_training.history import MetricsHistory
from model_training.progress import TextGenerationPreview, TrainingProgress, TrainingStarted


def run_headless(train, log_path: Path, *, history_path: Path) -> int:
    """Persist and stream progress, stopping cooperatively on SIGINT or SIGTERM."""
    stop_event = Event()
    logger = logging.Logger("tool-calling", level=logging.INFO)
    history: MetricsHistory

    def stop(_signum, _frame) -> None:
        stop_event.set()

    def report(progress: TrainingStarted | TrainingProgress) -> None:
        nonlocal history
        if isinstance(progress, TrainingStarted):
            history = session.enter_context(closing(MetricsHistory(history_path)))
            history.resume(progress.step)
            return
        history.record(progress)
        if progress.metrics:
            metrics = ", ".join(f"{name}={value:.6g}" for name, value in progress.metrics.items())
            logger.info("Step %s: %s", progress.step, metrics)
        if isinstance(progress.preview, TextGenerationPreview):
            for example in progress.preview.examples:
                logger.info("Sample step %s (%s): %r + %r", progress.preview.step,
                            example.label, example.context, example.completion)

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    with ExitStack() as handlers:
        stream = handlers.enter_context(closing(logging.StreamHandler()))
        stream.setFormatter(formatter)
        logger.addHandler(stream)
        handlers.callback(logger.removeHandler, stream)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file = handlers.enter_context(closing(logging.FileHandler(log_path, encoding="utf-8")))
            file.setFormatter(formatter)
            logger.addHandler(file)
            handlers.callback(logger.removeHandler, file)
            with ExitStack() as session:
                for sig in (signal.SIGINT, signal.SIGTERM):
                    session.callback(signal.signal, sig, signal.signal(sig, stop))
                logger.info("Starting headless training (PID %s).", getpid())
                train(report, stop_event, log=logger)
            logger.info("Training stopped." if stop_event.is_set() else "Training completed.")
            return 0
        except Exception:
            logger.exception("Training failed")
            return 1
