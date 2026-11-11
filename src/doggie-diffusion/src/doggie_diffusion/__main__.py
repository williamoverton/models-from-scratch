from threading import Event

from model_training.app import TrainingApp
from model_training.progress import ProgressCallback

from .settings import ModelSettings, TrainingSettings
from .training import train


def run_training(report: ProgressCallback, stop_event: Event) -> None:
    """Start or resume dog generation training with the configured settings."""
    train(
        report,
        stop_event,
        model_settings=ModelSettings(),
        settings=TrainingSettings(),
    )


def main() -> None:
    """Launch the training dashboard with its three-image preview panel."""
    app = TrainingApp(
        run_training,
        title="Doggie Diffusion",
        image_generation=True,
    )
    app.run()


if __name__ == "__main__":
    main()
