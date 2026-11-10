# Models from scratch

A monorepo for learning how different kinds of models work by building and
training small toy models with PyTorch. The emphasis is on readable code and
understanding the underlying concepts, not production readiness or model quality.

## Model projects

- **Hello World** (`src/hello-world/`): a single linear neuron trained on
  `y = 2x + 1`.

Projects use a shared Textual dashboard for training progress, loss history,
and a scrollable log.

## Getting started

Requires Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and an NVIDIA GPU
with CUDA available to PyTorch. Models and training tensors use CUDA; there is
no automatic CPU fallback.

From the repository root, run Hello World:

```bash
uv run hello-world
```

Press **S** to start a fresh training run and **Q** to quit.

For command-line help:

```bash
uv run hello-world --help
```

## Console experiments

Small, self-contained learning experiments are retained in `scripts/`.
To train a linear neuron without the dashboard:

```bash
uv run python scripts/train_linear.py
```

The script prints training loss and the learned weight and bias.

## Repository layout

- `src/`: individual model projects, each with its own Python package.
- `libs/model-training/`: shared training dashboard and progress contract.
- `scripts/`: standalone learning experiments.
- `design-log/`: decisions, rationale, and implementation tradeoffs.
- `diagrams/`: editable tldraw Offline diagrams.

The repository uses a uv workspace with one shared `uv.lock`. Architecture
choices and their rationale are recorded in [`design-log/`](design-log/).
