import logging
import sys
import termios
from collections.abc import Callable
from pathlib import Path
from threading import Event

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.worker import WorkerCancelled, get_current_worker
from textual.widgets import Footer, Header, RichLog, Sparkline, Static

from model_training.preview import ImageGenerationPanel
from model_training.progress import ImageGenerationPreview, ProgressCallback, TrainingProgress


class TrainingApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Models From Scratch"
    BINDINGS = [
        ("s", "start_training", "Start"),
        ("x", "stop_training", "Stop"),
        ("g", "generate", "Generate"),
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        train: Callable[[ProgressCallback, Event], None],
        *,
        title: str,
        image_generation: bool = False,
        log_path: Path = Path("logs/training.log"),
        generate: Callable[[], ImageGenerationPreview] | None = None,
        generation_request: Event | None = None,
    ) -> None:
        super().__init__()
        self.train = train
        self.title = title
        self.image_generation = image_generation
        self.stop_event = Event()
        self.quit_requested = False
        self.generate = generate
        self.generation_request = generation_request
        self.generation_running = False

        # Append timestamped messages without sending logging output into the TUI.
        log_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_logger = logging.Logger("model_training", level=logging.INFO)
        self.log_handler = logging.FileHandler(log_path, encoding="utf-8")
        self.log_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        self.file_logger.addHandler(self.log_handler)
        self.file_logger.info("Dashboard opened: %s", title)

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
        """Close the file log when the dashboard exits."""
        self.file_logger.info("Dashboard closed.")
        self.log_handler.close()

    def compose(self) -> ComposeResult:
        """Build the dashboard without model-specific metric fields."""
        yield Header()
        if self.image_generation:
            yield ImageGenerationPanel(id="image-generation", classes="panel")
        with VerticalScroll(id="dashboard"):
            yield Static("Idle — press S to train.", id="status")
            with Vertical(id="metrics", classes="panel"):
                yield Static("Step: —", id="step")
                yield Static("No metrics yet.", id="metric-values", markup=False)
            with Vertical(id="loss-panel", classes="panel"):
                yield Static("No loss samples yet.", id="loss-caption")
                yield Sparkline([], id="loss-history")
            yield RichLog(id="training-log", wrap=True, markup=False, max_lines=1000)
        yield Footer()

    def on_mount(self) -> None:
        """Initialize display history and training controls."""
        self.training_running = False
        self.loss_history: list[float] = []
        self.query_one("#metrics").border_title = "Training progress"
        self.query_one("#loss-panel").border_title = "Loss history"
        self.query_one("#training-log").border_title = "Training log"
        self.write_log("Ready: S starts training; X stops; Q stops and quits.")

    def action_start_training(self) -> None:
        """Start training unless a previous run is still active or stopping."""
        if self.training_running or self.generation_running:
            return
        self.training_running = True
        self.stop_event = Event()
        self.quit_requested = False
        if self.generation_request is not None:
            self.generation_request.clear()
        self.loss_history = []
        self.query_one("#loss-history", Sparkline).data = []
        self.query_one("#loss-caption", Static).update("No loss samples yet.")
        self.query_one("#step", Static).update("Step: —")
        self.query_one("#metric-values", Static).update("No metrics yet.")
        if self.image_generation:
            self.query_one(ImageGenerationPanel).reset_preview()
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
        """Expose generation only for apps that supply generation callbacks."""
        if action == "generate":
            return self.generate is not None and self.generation_request is not None
        return True

    def action_generate(self) -> None:
        """Queue a training preview or generate from a checkpoint while idle."""
        if self.generate is None or self.generation_request is None:
            return
        if self.generation_running:
            return
        if self.training_running:
            if not self.stop_event.is_set():
                self.generation_request.set()
                self.write_log("Display-only generation requested.")
            return
        self.generation_running = True
        self.set_status("Generating from checkpoint…")
        self.run_generation()

    @work(thread=True, group="generation", exclusive=True)
    def run_generation(self) -> None:
        """Generate off the UI thread without changing the saved model."""
        try:
            preview = self.generate()
        except Exception as error:
            self.file_logger.exception("Generation failed")
            self.call_from_thread(self.finish_generation, None, str(error))
        else:
            self.call_from_thread(self.finish_generation, preview, None)

    def finish_generation(
        self, preview: ImageGenerationPreview | None, error: str | None
    ) -> None:
        """Publish the generated images and release idle generation controls."""
        self.generation_running = False
        if error is not None:
            self.quit_requested = False
            self.set_status("Generation failed — see log. Press G to retry.")
            self.write_log(f"Generation failed: {error}")
            return
        if preview is not None:
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

        def report(progress: TrainingProgress) -> None:
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

    def show_progress(self, progress: TrainingProgress) -> None:
        """Render named metrics and retain one loss sample per report."""
        step_text = f"Step: {progress.step:,}"
        if progress.total_steps is not None:
            step_text += f" / {progress.total_steps:,}"
        self.query_one("#step", Static).update(step_text)
        # Image-generation models supply display-ready images through progress.
        if self.image_generation and progress.preview is not None:
            self.query_one(ImageGenerationPanel).show_preview(progress.preview)
        self.query_one("#metric-values", Static).update(
            "\n".join(f"{name}: {value:.6g}" for name, value in progress.metrics.items())
        )
        if "loss" in progress.metrics:
            self.loss_history.append(progress.metrics["loss"])
            self.query_one("#loss-history", Sparkline).data = list(self.loss_history)
            self.query_one("#loss-caption", Static).update(
                "Loss per report — lower is better."
            )
        self.write_log(
            f"Step {progress.step}: "
            + ", ".join(f"{name}={value:.6g}" for name, value in progress.metrics.items())
        )

    def write_log(self, message: str) -> None:
        """Append a message to both the file and the scrollable dashboard log."""
        self.query_one("#training-log", RichLog).write(message)
        self.file_logger.info(message)
