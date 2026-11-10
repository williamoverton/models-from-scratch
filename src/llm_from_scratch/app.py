from pathlib import Path

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.worker import WorkerCancelled, get_current_worker
from textual.widgets import Footer, Header, RichLog, Sparkline, Static
from textual_image.widget import Image

from llm_from_scratch.model import create_model
from llm_from_scratch.training import TrainingProgress, train


class TrainingApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Neural Network From Scratch"
    BINDINGS = [
        ("s", "start_training", "Start"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the dashboard without model-specific metric fields."""
        yield Header()
        with VerticalScroll(id="dashboard"):
            yield Image(Path.home() / "Documents" / "avatar.jpg", id="avatar")
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
        self.write_log("Ready: S starts a fresh CUDA model, 200 steps, learning rate 0.01.")

    def action_start_training(self) -> None:
        """Start a fresh experiment unless one is already running."""
        if self.training_running:
            return
        self.training_running = True
        self.loss_history = []
        self.query_one("#loss-history", Sparkline).data = []
        self.query_one("#loss-caption", Static).update("No loss samples yet.")
        self.query_one("#step", Static).update("Step: 0 / 200")
        self.query_one("#metric-values", Static).update("No metrics yet.")
        self.set_status("Training on CUDA…")
        self.write_log("Starting a fresh model; reporting every 20 steps.")
        self.run_training()

    @work(thread=True, exclusive=True)
    def run_training(self) -> None:
        """Run the experiment off the UI thread and hand results back safely."""
        worker = get_current_worker()

        def report(progress: TrainingProgress) -> None:
            if worker.is_cancelled:
                raise WorkerCancelled()
            self.call_from_thread(self.show_progress, progress)

        try:
            model = create_model()
            train(
                model,
                steps=200,
                learning_rate=0.01,
                report_every=20,
                on_progress=report,
            )
        except WorkerCancelled:
            return
        except Exception as error:
            if not worker.is_cancelled:
                self.call_from_thread(self.finish_training, str(error))
        else:
            if not worker.is_cancelled:
                self.call_from_thread(self.finish_training)

    def finish_training(self, error: str | None = None) -> None:
        """Display completion or failure and allow another run."""
        self.training_running = False
        if error is not None:
            self.set_status("Training failed — see log. Press S to retry.")
            self.write_log(f"Training failed: {error}")
        else:
            self.set_status("Completed — press S for a fresh run.")
            self.write_log("Completed 200 training steps.")

    def set_status(self, status: str) -> None:
        """Replace the current training status."""
        self.query_one("#status", Static).update(status)

    def show_progress(self, progress: TrainingProgress) -> None:
        """Render named metrics and retain one loss sample per report."""
        self.query_one("#step", Static).update(
            f"Step: {progress.step:,} / {progress.total_steps:,}"
        )
        self.query_one("#metric-values", Static).update(
            "\n".join(f"{name}: {value:.6g}" for name, value in progress.metrics.items())
        )
        if "loss" in progress.metrics:
            self.loss_history.append(progress.metrics["loss"])
            self.query_one("#loss-history", Sparkline).data = list(self.loss_history)
            self.query_one("#loss-caption", Static).update(
                "Loss per report (every 20 steps) — lower is better."
            )
        self.write_log(
            f"Step {progress.step}: "
            + ", ".join(f"{name}={value:.6g}" for name, value in progress.metrics.items())
        )

    def write_log(self, message: str) -> None:
        """Append a plain-text message to the scrollable log."""
        self.query_one("#training-log", RichLog).write(message)
