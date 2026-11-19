"""Prepare local tool-calling data or train the model in Textual."""

import argparse
from pathlib import Path

from .data_generation import DEFAULT_SEED
from .prepare_data import DEFAULT_CONTEXT_LENGTH, prepare_data


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def main() -> None:
    """Dispatch preparation separately from the CUDA-first dashboard worker."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare-data", help="Build a fresh prepared bundle offline.")
    prepare.add_argument("--output-dir", type=Path, required=True, help="New directory for the bundle.")
    prepare.add_argument("--context-length", type=_positive_int, default=DEFAULT_CONTEXT_LENGTH,
                         help=f"Maximum encoded row length (default: {DEFAULT_CONTEXT_LENGTH}).")
    prepare.add_argument("--seed", type=int, default=DEFAULT_SEED,
                         help=f"Corpus generation seed (default: {DEFAULT_SEED}).")

    train = commands.add_parser("train", help="Open the dashboard, then press S to start or resume.")
    train.add_argument("--data-dir", type=Path, required=True, help="Directory from prepare-data.")
    train.add_argument("--run-dir", type=Path, required=True, help="Directory for checkpoint.pt and training.log.")
    args = parser.parse_args()

    if args.command == "prepare-data":
        try:
            manifest = prepare_data(args.output_dir, context_length=args.context_length, seed=args.seed)
        except (OSError, ValueError) as error:
            prepare.error(str(error))
        counts = ", ".join(f"{name}: {split['records']:,} rows" for name, split in manifest["splits"].items())
        print(f"Prepared {args.output_dir} ({counts}; context length: {manifest['context_length']}).")
        return

    _open_dashboard(args)


def _open_dashboard(args: argparse.Namespace) -> None:
    from model_training.app import TrainingApp

    from .training import run_training

    def train(report, stop_event):
        run_training(report, stop_event, data_dir=args.data_dir, run_dir=args.run_dir,
                     log=app.file_logger)

    app = TrainingApp(train, title="Tool Calling", preview_mode="text",
                      log_path=args.run_dir / "training.log")
    app.run()


if __name__ == "__main__":
    main()
