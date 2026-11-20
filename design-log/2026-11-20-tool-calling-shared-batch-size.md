# Tool calling: one batch-size setting

Use `Config.batch_size` in both text pretraining and tool-call training. Remove
pretraining's CLI override and separate default; the prepared manifest still
owns context length. This supersedes the separate pretraining batch-size default
used after the [text pretraining decision](2026-11-20-tool-calling-pretraining.md).

Keep exact resume checks. Batch size determines how many shuffled rows each
completed step consumes, so changing it requires a new run directory. A run
started with the old default can still resume with that value set in `config.py`
and its other settings unchanged.
