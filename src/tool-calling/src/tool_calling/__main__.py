"""Prepare local text or tool-call data and train the model in Textual."""

import argparse
import os
from functools import partial
from pathlib import Path
from threading import Event

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

    train.add_argument("--headless", action="store_true",
                       help="Start immediately without the dashboard; SIGINT or SIGTERM saves and stops.")
    commands.add_parser("pretrain", help="Run text pretraining using settings in config.py.")
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

    raise SystemExit(_run_training(args))


def _run_training(args: argparse.Namespace) -> int:
    """Send the same training worker to the dashboard or the headless runner."""
    generation_request = None
    generate_text = None
    generation_prompt = ""
    if args.command == "pretrain":
        from . import config
        from .pretraining import generate_pretraining_example, run_pretraining

        if not config.PRETRAIN_SAMPLE_PROMPT.strip():
            raise SystemExit("PRETRAIN_SAMPLE_PROMPT in config.py must contain non-whitespace text.")
        run_dir = config.PRETRAIN_RUN_DIR
        headless = config.PRETRAIN_HEADLESS
        generation_prompt = config.PRETRAIN_SAMPLE_PROMPT
        train = partial(run_pretraining, data_dir=config.PRETRAIN_DATA_DIR, run_dir=run_dir,
                        sample_prompt=lambda: generation_prompt,
                        verify_shards=config.PRETRAIN_VERIFY_SHARDS, init_from=config.PRETRAIN_INIT_FROM)
        title = "Language Pretraining"
        if not headless:
            generation_request = Event()
            generate_text = partial(generate_pretraining_example, data_dir=config.PRETRAIN_DATA_DIR, run_dir=run_dir)
    else:
        from .training import run_training

        run_dir = args.run_dir
        headless = args.headless
        train = partial(run_training, data_dir=args.data_dir, run_dir=run_dir)
        title = "Tool Calling"

    log_path = run_dir / "training.log"
    if headless:
        from .headless import run_headless

        return run_headless(train, log_path)

    from model_training.app import TrainingApp

    def dashboard_train(report, stop_event):
        if generation_request is not None:
            train(report, stop_event, log=app.file_logger, sample_prompt=lambda: app.generation_prompt,
                  generation_request=generation_request)
            return
        train(report, stop_event, log=app.file_logger)

    app = TrainingApp(dashboard_train, title=title, preview_mode="text", log_path=log_path,
                      generation_request=generation_request, generate_text=generate_text,
                      generation_prompt=generation_prompt)
    app.run()
    return 0


if __name__ == "__main__":
    main()
