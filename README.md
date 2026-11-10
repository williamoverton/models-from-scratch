# LLM from scratch

A learning project for building neural networks with PyTorch. The current app
is a Textual dashboard; no model or training loop is implemented yet.

## Run

Requires Python 3.12 or newer and uv. From the project directory:

```bash
uv run python -m llm_from_scratch
```

Press **Q** to quit. The dashboard shows status, step, loss, weight, bias,
a loss sparkline, and a scrollable log. Metrics remain unset until real
training results are provided.

Command-line help:

```bash
uv run python -m llm_from_scratch --help
```

## Code layout

- `__main__.py`: argument parsing and application launch.
- `app.py`: widgets and display updates.
- `app.tcss`: terminal layout and styling.

These files live in `src/llm_from_scratch/`.

`TrainingApp.set_status`, `show_progress`, and `write_log` update the display
on Textual's UI thread after mounting. A future training worker must hand
updates to that thread using Textual's `call_from_thread`, rather than
changing widgets directly. Training and display refresh must remain independent:
there is no training timer or artificial delay in the UI core.

The log retains up to 1,000 rendered lines. The loss sparkline summarizes
samples to fit its available width; it has no numeric axes.
