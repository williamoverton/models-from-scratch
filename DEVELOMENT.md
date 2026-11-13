# Development

This repository uses Python 3.12 or newer and [uv](https://docs.astral.sh/uv/).
The current PyTorch model projects require an NVIDIA GPU with CUDA available;
they do not automatically fall back to the CPU. The shared tokenizer does not
require PyTorch or a GPU.

## NixOS development environment

The pinned Nix flake supplies Python 3.14, uv, GCC, Python headers, and native
library paths for PyTorch. CUDA userspace libraries come from the Python wheels;
the NVIDIA driver comes from the host. Triton uses the host driver directory
directly through `TRITON_LIBCUDA_PATH`, avoiding its `/sbin/ldconfig` lookup.
This is a normal development shell, not an FHS container: the host filesystem
remains accessible.

Enter it from the repository root and install the workspace dependencies:

```bash
nix develop path:.
uv sync
```

Then launch a model, for example:

```bash
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

## Workspace structure

Each model lives in `src/<project-name>/`, with its own package and
`pyproject.toml`. Shared libraries live in `libs/`. The uv workspace uses one
root `uv.lock`.

- `src/hello-world/`: single-neuron learning project.
- `src/doggie-diffusion/`: dog-image generation project.
- `libs/model-training/`: shared Textual training dashboard and progress contract.
- `libs/model-tokenizer/`: shared byte-level BPE tokenizer;
  see its [README](libs/model-tokenizer/README.md) for usage and artifact details.
- `scripts/`: retained, standalone learning experiments.
- `design-log/`: agreed decisions, rationale, and tradeoffs.
- `diagrams/`: editable tldraw Offline diagrams.

Model projects own their data, training loops, settings, and trained artifacts.
The shared dashboard accepts model-provided training functions rather than
importing individual projects. The shared tokenizer similarly leaves datasets,
control-token choices, and sequence formatting to its consumers.

## Learning experiments

Small console experiments remain in `scripts/` for learning and future reference.
Run them from the repository root. For the tokenizer training example:

```bash
uv run --package model-tokenizer python scripts/train-simple-english-tokenizer.py
```

It replaces `trained-models/tokenizers/simple-english.json` when re-run. See the
[tokenizer guide](libs/model-tokenizer/README.md) for what it demonstrates.

For Hello World's command-line options:

```bash
uv run hello-world --help
```

## Project guidance

Contributor and coding-agent instructions live in `AGENTS.md`. Architecture
choices and their rationale are recorded in [the design log](design-log/).
Keep component-specific technical documentation with the relevant component;
keep the root README focused on understanding and using the repository.
