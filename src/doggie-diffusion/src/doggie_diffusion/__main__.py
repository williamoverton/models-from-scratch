from functools import partial
from threading import Event

from model_training.app import TrainingApp
from model_training.progress import ProgressCallback

from .settings import ModelSettings, TrainingSettings
from .training import generate_from_checkpoint, train


def run_training(
    report: ProgressCallback, stop_event: Event, *, generation_request: Event
) -> None:
    """Start or resume dog generation training with the configured settings."""
    train(
        report,
        stop_event,
        model_settings=ModelSettings(),
        settings=TrainingSettings(),
        generation_request=generation_request,
    )


def main() -> None:
    """Launch training with scheduled and on-demand image generation."""
    generation_request = Event()
    app = TrainingApp(
        partial(run_training, generation_request=generation_request),
        title="Doggie Diffusion",
        preview_mode="image",
        generate=generate_from_checkpoint,
        generation_request=generation_request,
    )
    app.run()


if __name__ == "__main__":
    main()
