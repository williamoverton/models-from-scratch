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

### NixOS development environment

The pinned Nix flake supplies Python 3.14, uv, GCC, Python headers, and native
library paths for PyTorch. CUDA userspace libraries come from the Python wheels;
the NVIDIA driver comes from the host. Triton uses the host driver directory
directly through `TRITON_LIBCUDA_PATH`, avoiding its `/sbin/ldconfig` lookup.
This is a normal development shell, not an FHS container: the host filesystem
remains accessible.

Enter it from the repository root:

```bash
nix develop path:.
uv sync
uv run doggie-diffusion
```

For automatic activation, enable your shell's direnv integration and run
`direnv allow` once in this repository. The committed `.envrc` loads the same
environment whenever you enter the directory. Python dependencies remain
managed by the uv workspace and `uv.lock`; Nix dependencies are pinned in
`flake.lock`.

The shell selects its pinned Python for uv. If uv recreates `.venv` to use that
interpreter, it reinstalls dependencies; model checkpoints in `trained-models/`
are separate and remain untouched.

### Running models

From the repository root, run Hello World:

```bash
uv run hello-world
```

Press **S** to start a fresh training run and **Q** to quit.

For command-line help:

```bash
uv run hello-world --help
```

## Repository layout

- `src/`: individual model projects, each with its own Python package.
- `libs/model-training/`: shared training dashboard and progress contract.
- `scripts/`: standalone learning experiments.
- `design-log/`: decisions, rationale, and implementation tradeoffs.
- `diagrams/`: editable tldraw Offline diagrams.

The repository uses a uv workspace with one shared `uv.lock`. Architecture
choices and their rationale are recorded in [`design-log/`](design-log/).
