"""Prepare local text or tool-call data and train the model in Textual."""

import argparse
import os
from functools import partial
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
    pretrain.add_argument("--init-from", type=Path,
                          help="Load model weights from a pretraining checkpoint into a fresh run.")
    pretrain.add_argument("--sample-prompt", default="Training an LLM is",
                          help="Text to continue in the preview (default: %(default)s).")
    pretrain.add_argument("--verify-shards", action="store_true",
                          help="Scan every shard for SHA-256 and token ID validity before training.")
    for command in (train, pretrain):
        command.add_argument("--headless", action="store_true",
                             help="Start immediately without the dashboard; SIGINT or SIGTERM saves and stops.")
    args = parser.parse_args()
    if args.command == "pretrain" and not args.sample_prompt.strip():
        pretrain.error("--sample-prompt must contain non-whitespace text.")

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

    raise SystemExit(_run_training(args))


def _run_training(args: argparse.Namespace) -> int:
    """Send the same training worker to the dashboard or the headless runner."""
    if args.command == "pretrain":
        from .pretraining import run_pretraining

        worker = partial(run_pretraining, sample_prompt=args.sample_prompt,
                         verify_shards=args.verify_shards, init_from=args.init_from)
        title = "Language Pretraining"
    else:
        from .training import run_training

        worker = run_training
        title = "Tool Calling"

    train = partial(worker, data_dir=args.data_dir, run_dir=args.run_dir)
    log_path = args.run_dir / "training.log"
    if args.headless:
        from .headless import run_headless

        return run_headless(train, log_path)

    from model_training.app import TrainingApp

    def dashboard_train(report, stop_event):
        train(report, stop_event, log=app.file_logger)

    app = TrainingApp(dashboard_train, title=title, preview_mode="text", log_path=log_path)
    app.run()
    return 0


if __name__ == "__main__":
    main()
