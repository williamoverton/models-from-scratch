import argparse

from model_training.app import TrainingApp
from model_training.progress import ProgressCallback

from hello_world.model import create_model
from hello_world.training import train


def run_training(report: ProgressCallback) -> None:
    """Create and train a fresh linear neuron for each dashboard run."""
    train(
        create_model(),
        steps=200,
        learning_rate=0.01,
        report_every=20,
        on_progress=report,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train a single linear neuron on y = 2x + 1 using CUDA.",
    )
    parser.parse_args()

    app = TrainingApp(run_training, title="Hello World — Linear Neuron")
    app.run()


if __name__ == "__main__":
    main()
