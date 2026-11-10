# LLM from scratch

A learning project for understanding large language models by building and
training our own models with PyTorch. The emphasis is on small, readable code
and learning the underlying concepts, not production readiness or model quality.

The current experiment trains a single linear neuron on `y = 2x + 1`.
The main application is a Textual terminal dashboard showing training progress,
loss history, and a scrollable log.

## Getting started

Requires Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and an NVIDIA GPU
with CUDA available to PyTorch. Models and training tensors use CUDA; there is
no automatic CPU fallback.

From the project directory:

```bash
uv run python -m llm_from_scratch
```

Press **S** to start a fresh training run and **Q** to quit.

For command-line help:

```bash
uv run python -m llm_from_scratch --help
```

## Console experiments

Small, self-contained learning experiments are retained in `scripts/`.
To train a linear neuron without the dashboard:

```bash
uv run python scripts/train_linear.py
```

The script prints training loss and the learned weight and bias.

## Repository layout

- `src/llm_from_scratch/`: the main application, model, and training loop.
- `scripts/`: standalone learning experiments.
- `design-log/`: decisions, rationale, and implementation tradeoffs.
- `diagrams/`: editable tldraw Offline diagrams.
