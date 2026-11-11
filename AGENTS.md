# Project goals

This is a monorepo for learning how different kinds of models work by
building and training small toy models with PyTorch, not just language models.

The primary goals are:
- Understand model architectures, their components, and how they learn.
- Learn PyTorch through practical implementation and experimentation.
- Keep the implementation small, readable, and easy to reason about.

Model quality, performance, and production readiness are secondary to
learning. Do not add complexity without a concrete need.

# Implementation approach

Use PyTorch built-ins where available and follow idiomatic PyTorch practices,
including standard layers such as `nn.Linear`. Build and train our own model
rather than using a ready-made pretrained model; do not reimplement standard
components solely to avoid using built-ins.

Default PyTorch models and tensors to CUDA in both the main app and experiments;
this workstation has an NVIDIA GPU. Do not silently fall back to CPU when CUDA
is unavailable. Use CPU only when explicitly requested.

When introducing a feature, tool, function, layer, or other API for the first
time, offer to explain what it does and how it works underneath. Using a
built-in should not prevent us from learning the underlying concepts.

Prefer straightforward code. Avoid unnecessary abstractions that hide the
concepts we are trying to learn.

Do not add backward-compatibility code unless the user explicitly permits it.
Prefer a clean change that updates affected callers over compatibility
shims, legacy aliases, or parallel old and new implementations.

# Code structure

Use modular code to make each concept easier to understand in isolation.

Avoid huge main functions. Keep entry points focused on connecting the
components and running the experiment.

Prefer classes for components with state or a clear responsibility,
and focused functions for stateless operations. Organize files by purpose
where it helps understanding.

Keep the structure simple: do not introduce classes, extra files, or
abstraction layers merely for the sake of modularity.

Keep each model project in its own `src/<project-name>/` directory, with its
own `pyproject.toml` and Python package. The first project is `src/hello-world/`.
Use the root uv workspace and shared lockfile for dependencies and local packages.

Shared libraries live in `libs/`. `libs/model-training/` owns the reusable
Textual dashboard and the model-independent `TrainingProgress` callback contract.
Model projects own their models, data, training loops, and experiment settings.
They supply a training function to the dashboard; shared code must not import
individual model projects or hardcode their training settings.
Extract only genuinely shared concepts; do not build a general training framework.

The Textual TUI is the main application. Keep small, self-contained console
experiments in `scripts/` for learning and future reference. These may use
top-level code and duplicate a small calculation to make the concept visible;
do not turn them into application infrastructure or delete them as temporary
scaffolding. Use descriptive filenames and document how to run each experiment.

# Design decisions

Record key agreed decisions in:
design-log/YYYY-MM-DD-name-of-decision.md

Each entry should explain:
- What we decided.
- Why we decided it.
- Alternatives considered, when relevant.
- Consequences or tradeoffs, when relevant.

Keep entries concise. Record meaningful decisions, not every small
implementation detail. Do not record proposals as agreed decisions.

Read relevant design-log entries before revisiting an existing choice.
If a decision changes, add a new entry referencing the previous one;
preserve the history.

# README

Keep `README.md` focused on important, high-level information that helps a
human understand the repository and how to use it. It is not a changelog or
a dumping ground for every change, experiment, or implementation detail.
Use well-structured Markdown with clear headings and logically grouped content.
Update it only when a change affects that high-level understanding or usage.

# Diagrams

Use custom, editable tldraw Offline diagrams saved in `diagrams/`.
Read `diagrams/AGENTS.md` for the diagram index, related decisions, and
diagram maintenance instructions before working on diagrams.

# Code comments

Keep code and comments focused on the current implementation.

Give classes and functions a concise docstring at the top explaining their
purpose. Include non-obvious input/output shapes or constraints where useful.

Add a simple, concise comment before important logic steps explaining what
the code does. Do not comment every line or obvious operation. Keep comments
free of discussion or planning references.

Comments explaining non-obvious math, intent, constraints, or invariants
are useful. Historical explanations of previous implementations and
past choices belong in the design log, not in the code.

# Verification

Don't add tests or run verification tasks unless the user asks you to.
Smoke tests are banned unless explicitly requested by the user. This includes
throwaway checks, headless UI runs, and ad hoc verification scripts. Permission
to implement a change or run a learning example does not authorize smoke tests.
