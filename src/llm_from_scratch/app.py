from collections.abc import Sequence

from textual.app import App, ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.widgets import Footer, Header, RichLog, Sparkline, Static


class TrainingApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "Neural Network From Scratch"
    BINDINGS = [
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="dashboard"):
            yield Static("Idle — no training started.", id="status")
            with Vertical(id="metrics", classes="panel"):
                yield Static("Step: —", id="step")
                yield Static("Loss: —", id="loss")
                yield Static("Weight: —", id="weight")
                yield Static("Bias: —", id="bias")
            with Vertical(id="loss-panel", classes="panel"):
                yield Static("No loss samples yet.", id="loss-caption")
                yield Sparkline([], id="loss-history")
            yield RichLog(id="training-log", wrap=True, markup=False, max_lines=1000)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#metrics").border_title = "Parameters and progress"
        self.query_one("#loss-panel").border_title = "Loss history"
        self.query_one("#training-log").border_title = "Training log"
        self.write_log("UI ready. No model or training job is running.")

    def set_status(self, status: str) -> None:
        self.query_one("#status", Static).update(status)

    def show_progress(
        self,
        *,
        step: int,
        total_steps: int,
        loss: float,
        weight: float,
        bias: float,
        loss_history: Sequence[float],
    ) -> None:
        """Display a training snapshot; call on Textual's UI thread."""
        self.query_one("#step", Static).update(f"Step: {step:,} / {total_steps:,}")
        self.query_one("#loss", Static).update(f"Loss: {loss:.6g}")
        self.query_one("#weight", Static).update(f"Weight: {weight:.6g}")
        self.query_one("#bias", Static).update(f"Bias: {bias:.6g}")
        self.query_one("#loss-caption", Static).update(
            "Loss per training step — lower is better."
        )
        self.query_one("#loss-history", Sparkline).data = list(loss_history)

    def write_log(self, message: str) -> None:
        self.query_one("#training-log", RichLog).write(message)
