import logging
import sys
import termios
from collections.abc import Callable
from math import isfinite
from pathlib import Path
from threading import Event
from typing import Literal

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.worker import WorkerCancelled, get_current_worker
from textual.widgets import Footer, Header, Input, RichLog, Static, TabbedContent, TabPane
from textual_plotext import PlotextPlot

from model_training.history import MetricsHistory
from model_training.logs import SegmentLogHandler
from model_training.preview import ImageGenerationPanel, TextGenerationPanel
from model_training.progress import (
    ImageGenerationPreview,
    ProgressCallback,
    TextGenerationPreview,
    TrainingProgress,
    TrainingStarted,
)


_LOSS_CHARTS = (
    ("loss", "training-loss", "Training loss"),
    ("validation loss", "validation-loss", "Validation loss"),
)


class _PromptEditor(ModalScreen[str | None]):
    """Submit a nonblank preview prompt or cancel with Escape."""

    BINDINGS = [("escape", "dismiss", "Cancel")]
    AUTO_FOCUS = "Input"
    DEFAULT_CSS = """
    _PromptEditor { align: center middle; }
    _PromptEditor Vertical { width: 80%; height: auto; }
    """

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def compose(self) -> ComposeResult:
        """Show the current prompt in a focused editor."""
        with Vertical(classes="panel"):
            yield Static("Generation prompt · Enter to generate · Esc to cancel")
            yield Input(self.prompt, placeholder="Enter a prompt")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Apply the edit only when there is text to generate from."""
        if event.value.strip():
            self.dismiss(event.value)


class TrainingApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Models From Scratch"
    BINDINGS = [
        ("s", "start_training", "Start"),
        ("x", "stop_training", "Stop"),
        ("g", "generate", "Generate"),
        ("e", "edit_prompt", "Edit prompt"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        train: Callable[[ProgressCallback, Event], None],
        *,
        title: str,
        preview_mode: Literal["none", "image", "text"],
        log_path: Path = Path("logs/training.log"),
        history_path: Path | None = None,
        generate: Callable[[], ImageGenerationPreview] | None = None,
        generation_request: Event | None = None,
        generate_text: Callable[[str], TextGenerationPreview] | None = None,
        generation_prompt: str = "",
    ) -> None:
        super().__init__()
        self.train = train
        self.title = title
        self.preview_mode = preview_mode
        self.stop_event = Event()
        self.quit_requested = False
        self.generate = generate
        self.generation_request = generation_request
        self.generate_text = generate_text
        self.generation_prompt = generation_prompt
        self.generation_running = False
        self.history_path = history_path
        self.metrics_history: MetricsHistory | None = None

        # Leave the previous segment untouched until training starts.
        self.file_logger = logging.Logger("model_training", level=logging.INFO)
        self.file_logger.addHandler(logging.NullHandler())
        self.log_handler = SegmentLogHandler(log_path)

    def run(self, **kwargs) -> None:
        """Run the dashboard and restore the terminal's original input modes."""
        terminal = sys.__stdin__
        terminal_fd = (
            terminal.fileno()
            if terminal is not None and terminal.isatty()
            else None
        )
        original_mode = (
            termios.tcgetattr(terminal_fd) if terminal_fd is not None else None
        )

        try:
            super().run(**kwargs)
        finally:
            # Restore echo, line buffering, and Enter handling after UI cleanup.
            if terminal_fd is not None:
                termios.tcsetattr(terminal_fd, termios.TCSANOW, original_mode)

    def on_unmount(self) -> None:
        """Close the metric database and file log when the dashboard exits."""
        if self.metrics_history is not None:
            self.metrics_history.close()
        self.file_logger.info("Dashboard closed.")
        self.log_handler.close()

    def compose(self) -> ComposeResult:
        """Build the dashboard without model-specific metric fields."""
        yield Header()
        if self.preview_mode == "image":
            yield ImageGenerationPanel(id="image-generation", classes="panel")
        with VerticalScroll(id="dashboard"):
            yield Static("Idle — press S to train.", id="status")
            with TabbedContent():
                with TabPane("Loss"):
                    with Horizontal(id="loss-charts"):
                        for _, chart_id, _ in _LOSS_CHARTS:
                            yield PlotextPlot(id=chart_id)
            if self.preview_mode == "text":
                yield TextGenerationPanel(
                    id="text-generation", classes="panel", markup=False
                )
            yield RichLog(id="training-log", wrap=True, markup=False, max_lines=1000)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize display history and training controls."""
        self.training_running = False
        if self.history_path is not None:
            self.metrics_history = MetricsHistory(self.history_path)
        for _, chart_id, title in _LOSS_CHARTS:
            plot = self.query_one(f"#{chart_id}", PlotextPlot).plt
            plot.title(title)
            plot.xlabel("Update")
        self._reload_loss_history()
        self.query_one("#training-log").border_title = "Training log"
        self.write_log("Ready: S starts training; X stops; Q stops and quits.")

    def action_start_training(self) -> None:
        """Start training unless a previous run is still active or stopping."""
        if self.training_running or self.generation_running:
            return
        try:
            self.log_handler.start_segment()
        except OSError as error:
            self.set_status("Could not rotate the training log — press S to retry.")
            self.query_one("#training-log", RichLog).write(f"Log rotation failed: {error}")
            return
        self.file_logger.addHandler(self.log_handler)
        self.training_running = True
        self.stop_event = Event()
        self.quit_requested = False
        if self.generation_request is not None:
            self.generation_request.clear()
        if self.metrics_history is None:
            self._reload_loss_history()
        if self.preview_mode == "image":
            self.query_one(ImageGenerationPanel).reset_preview()
        elif self.preview_mode == "text":
            self.query_one(TextGenerationPanel).reset_preview()
        self.set_status("Training…")
        self.write_log("Starting training.")
        self.run_training()

    def action_stop_training(self) -> None:
        """Request cooperative shutdown without interrupting an update or save."""
        if not self.training_running or self.stop_event.is_set():
            return
        self.stop_event.set()
        self.set_status("Stopping…")
        self.write_log("Stop requested; waiting for training to finish.")

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Expose generation controls only for launchers that supply the hooks."""
        if action == "edit_prompt":
            return self.generate_text is not None and not self.generation_running
        if action == "generate":
            return self.generation_request is not None and (
                (self.preview_mode == "image" and self.generate is not None)
                or (self.preview_mode == "text" and self.generate_text is not None)
            )
        return True

    def action_edit_prompt(self) -> None:
        """Edit this session's text prompt, then request generation on submit."""
        if self.generate_text is not None and not self.generation_running:
            self.push_screen(_PromptEditor(self.generation_prompt), self._apply_prompt)

    def _apply_prompt(self, prompt: str | None) -> None:
        """Store a submitted prompt and route it through the G action."""
        if prompt is not None:
            self.generation_prompt = prompt
            self.action_generate()

    def action_generate(self) -> None:
        """Queue a training preview or generate from a checkpoint while idle."""
        if self.generation_request is None or (self.generate is None and self.generate_text is None):
            return
        if self.generation_running:
            return
        if self.training_running:
            if not self.stop_event.is_set():
                self.generation_request.set()
                self.write_log("Display-only generation requested.")
            return
        self.generation_running = True
        self.refresh_bindings()
        self.set_status("Generating from checkpoint…")
        self.run_generation()

    @work(thread=True, group="generation", exclusive=True)
    def run_generation(self) -> None:
        """Generate off the UI thread without changing the saved model."""
        try:
            if self.generate_text is not None:
                preview = self.generate_text(self.generation_prompt)
            else:
                preview = self.generate()
        except Exception as error:
            self.file_logger.exception("Generation failed")
            self.call_from_thread(self.finish_generation, None, str(error))
        else:
            self.call_from_thread(self.finish_generation, preview, None)

    def finish_generation(
        self, preview: ImageGenerationPreview | TextGenerationPreview | None, error: str | None
    ) -> None:
        """Publish the generated preview and release idle generation controls."""
        self.generation_running = False
        self.refresh_bindings()
        if error is not None:
            self.quit_requested = False
            self.set_status("Generation failed — see log. Press G to retry.")
            self.write_log(f"Generation failed: {error}")
            return
        if isinstance(preview, TextGenerationPreview):
            self.query_one(TextGenerationPanel).show_preview(preview)
            self.write_log(f"Generated a text preview at step {preview.step}.")
        elif isinstance(preview, ImageGenerationPreview):
            self.query_one(ImageGenerationPanel).show_preview(preview)
            self.write_log(f"Generated display-only samples at step {preview.step}.")
        self.set_status("Stopped — press S to train or G to generate.")
        if self.quit_requested:
            self.exit()

    def action_quit(self) -> None:
        """Wait for active training to finish its shutdown before exiting."""
        if self.generation_running:
            self.quit_requested = True
            self.set_status("Waiting for generation before quitting…")
            return
        if not self.training_running:
            self.exit()
            return
        self.quit_requested = True
        self.action_stop_training()

    @work(thread=True, exclusive=True)
    def run_training(self) -> None:
        """Run the experiment off the UI thread and hand results back safely."""
        worker = get_current_worker()

        def report(progress: TrainingStarted | TrainingProgress) -> None:
            if worker.is_cancelled:
                raise WorkerCancelled()
            self.call_from_thread(self.show_progress, progress)

        try:
            self.train(report, self.stop_event)
        except WorkerCancelled:
            return
        except Exception as error:
            self.file_logger.exception("Training failed")
            if not worker.is_cancelled:
                self.call_from_thread(self.finish_training, str(error))
        else:
            if not worker.is_cancelled:
                self.call_from_thread(self.finish_training)

    def finish_training(self, error: str | None = None) -> None:
        """Display completion or failure and allow another run."""
        self.training_running = False
        quit_requested = self.quit_requested
        self.quit_requested = False
        if error is not None:
            self.set_status("Training failed — see log. Press S to retry.")
            self.write_log(f"Training failed: {error}")
        elif self.stop_event.is_set():
            self.set_status("Stopped — press S to train.")
            self.write_log("Training stopped.")
        else:
            self.set_status("Completed — press S to train.")
            self.write_log("Training completed.")

        # A training failure stays visible rather than disappearing on quit.
        if quit_requested and error is None:
            self.exit()

    def set_status(self, status: str) -> None:
        """Replace the current training status."""
        self.query_one("#status", Static).update(status)

    def show_progress(self, progress: TrainingStarted | TrainingProgress) -> None:
        """Reconcile resumed history or display a training report."""
        if isinstance(progress, TrainingStarted):
            if self.metrics_history is not None:
                self.metrics_history.resume(progress.step)
                self._reload_loss_history()
            return
        if self.metrics_history is not None:
            self.metrics_history.record(progress)
        preview = progress.preview
        if self.preview_mode == "image" and isinstance(preview, ImageGenerationPreview):
            self.query_one(ImageGenerationPanel).show_preview(preview)
        elif self.preview_mode == "text" and isinstance(preview, TextGenerationPreview):
            self.query_one(TextGenerationPanel).show_preview(preview)
        if preview is not None and not progress.metrics:
            return

        for metric, chart_id, _ in _LOSS_CHARTS:
            value = progress.metrics.get(metric)
            if value is not None and isfinite(value):
                self.loss_history[metric][progress.step] = value
                self._draw_loss_chart(metric, chart_id)
        self.write_log(
            f"Step {progress.step}: "
            + ", ".join(f"{name}={value:.6g}" for name, value in progress.metrics.items())
        )

    def _reload_loss_history(self) -> None:
        """Rebuild both charts from the saved history, or clear transient charts."""
        self.loss_history: dict[str, dict[int, float]] = {}
        for metric, chart_id, _ in _LOSS_CHARTS:
            self.loss_history[metric] = (
                self.metrics_history.series(metric) if self.metrics_history is not None else {}
            )
            self._draw_loss_chart(metric, chart_id)

    def _draw_loss_chart(self, metric: str, chart_id: str) -> None:
        """Redraw one loss series against actual completed updates."""
        chart = self.query_one(f"#{chart_id}", PlotextPlot)
        plot = chart.plt
        plot.clear_data()
        history = self.loss_history[metric]
        if history:
            draw = plot.scatter if len(history) == 1 else plot.plot
            draw(list(history), list(history.values()))
        chart.refresh()

    def write_log(self, message: str) -> None:
        """Append a message to both the file and the scrollable dashboard log."""
        self.query_one("#training-log", RichLog).write(message)
        self.file_logger.info(message)
