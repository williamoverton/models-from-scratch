# LLM from scratch

A learning project for building neural networks with PyTorch. The Textual app
creates a single linear neuron; no training loop is implemented yet.

## Run

Requires Python 3.12 or newer and uv. From the project directory:

```bash
uv run python -m llm_from_scratch
```

Press **Q** to quit. The dashboard shows status, step, loss, weight, bias,
a loss sparkline, and a scrollable log. Initial weight and bias are displayed
at startup. Step, loss, and loss history remain unset until training is added.

Command-line help:

```bash
uv run python -m llm_from_scratch --help
```

## Code layout

- `__main__.py`: argument parsing and application launch.
- `app.py`: widgets and display updates.
- `app.tcss`: terminal layout and styling.
- `model.py`: creates an `nn.Linear` layer with one input and one output.
- `training.py`: CUDA training on `y = 2x + 1` and UI-independent progress records.

These files live in `src/llm_from_scratch/`.

`TrainingApp.set_status`, `show_progress`, and `write_log` update the display
on Textual's UI thread after mounting. A future training worker must hand
updates to that thread using Textual's `call_from_thread`, rather than
changing widgets directly. Training and display refresh must remain independent:
there is no training timer or artificial delay in the UI core.

The log retains up to 1,000 rendered lines. The loss sparkline summarizes
samples to fit its available width; it has no numeric axes.

The training function publishes `TrainingProgress` through a caller-supplied
callback at the requested step interval and on the final step. Each record
contains completed step count, total steps, and named scalar metrics. Reported
loss is the pre-update value used to compute that step's gradients, not an
extra evaluation of the updated model. The TUI is not yet connected to it.

## Console experiments

The TUI remains the main application. `scripts/` holds small, self-contained
experiments kept for learning and future reference.

From the project directory:

```bash
uv run python scripts/train_linear.py
```

This trains one `nn.Linear` neuron on four examples of `y = 2x + 1` using
mean squared error and gradient descent. It prints loss every 20 steps and
the final weight and bias. Initialization is random, so results vary by run.
Printed losses describe the model before the corresponding update.
