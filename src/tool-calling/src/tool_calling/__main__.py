"""Prepare local text or tool-call data and train the model in Textual."""

import argparse
import os
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

    prepare_text = commands.add_parser("prepare-pretrain", help="Pack local corpora for next-token pretraining.")
    prepare_text.add_argument("--wikipedia", type=Path, required=True, help="Local Wikipedia ZIM or article Parquet.")
    prepare_text.add_argument("--qa", type=Path, required=True, help="Stack Exchange JSONL, gzip file, or shard directory.")
    prepare_text.add_argument("--tokenizer", type=Path, required=True, help="Saved tokenizer with tool protocol IDs.")
    prepare_text.add_argument("--output-dir", type=Path, required=True, help="New directory for the bundle.")
    prepare_text.add_argument("--context-length", type=_positive_int, default=DEFAULT_CONTEXT_LENGTH)
    prepare_text.add_argument("--windows-per-source", type=_positive_int,
                              help="Cap training windows per source; omit to prepare all data.")
    prepare_text.add_argument("--workers", type=_positive_int,
                              default=getattr(os, "process_cpu_count", os.cpu_count)() or 1,
                              help="CPU worker processes (default: all available logical CPUs).")

    train = commands.add_parser("train", help="Open the dashboard, then press S to start or resume.")
    train.add_argument("--data-dir", type=Path, required=True, help="Directory from prepare-data.")
    train.add_argument("--run-dir", type=Path, required=True, help="Directory for checkpoint.pt and training.log.")

    pretrain = commands.add_parser("pretrain", help="Open the next-token pretraining dashboard.")
    pretrain.add_argument("--data-dir", type=Path, required=True, help="Directory from prepare-pretrain.")
    pretrain.add_argument("--run-dir", type=Path, required=True, help="Directory for pretraining checkpoints and log.")
    pretrain.add_argument("--batch-size", type=_positive_int, default=8)
    args = parser.parse_args()

    if args.command == "prepare-data":
        try:
            manifest = prepare_data(args.output_dir, context_length=args.context_length, seed=args.seed)
        except (OSError, ValueError) as error:
            prepare.error(str(error))
        counts = ", ".join(f"{name}: {split['records']:,} rows" for name, split in manifest["splits"].items())
        print(f"Prepared {args.output_dir} ({counts}; context length: {manifest['context_length']}).")
        return

    if args.command == "prepare-pretrain":
        from .pretrain_data import prepare_pretraining

        try:
            manifest = prepare_pretraining(args.output_dir, tokenizer_path=args.tokenizer,
                                           wikipedia=args.wikipedia, qa=args.qa,
                                           context_length=args.context_length,
                                           windows_per_source=args.windows_per_source,
                                           workers=args.workers)
        except (OSError, ValueError, RuntimeError) as error:
            prepare_text.error(str(error))
        counts = ", ".join(f"{name}: {sum(shard['rows'] for shard in splits['train']):,} train windows"
                           for name, splits in manifest["sources"].items())
        print(f"Prepared {args.output_dir} ({counts}; context length: {manifest['context_length']}).")
        return

    _open_dashboard(args)


def _open_dashboard(args: argparse.Namespace) -> None:
    from model_training.app import TrainingApp

    if args.command == "pretrain":
        from .pretraining import run_pretraining

        def train(report, stop_event):
            run_pretraining(report, stop_event, data_dir=args.data_dir, run_dir=args.run_dir,
                            log=app.file_logger, batch_size=args.batch_size)

        title, preview_mode = "Language Pretraining", "none"
    else:
        from .training import run_training

        def train(report, stop_event):
            run_training(report, stop_event, data_dir=args.data_dir, run_dir=args.run_dir,
                         log=app.file_logger)

        title, preview_mode = "Tool Calling", "text"

    app = TrainingApp(train, title=title, preview_mode=preview_mode,
                      log_path=args.run_dir / "training.log")
    app.run()


if __name__ == "__main__":
    main()
