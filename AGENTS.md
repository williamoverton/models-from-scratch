# Project goals

This is a toy project for learning how large language models work by
building one from scratch with PyTorch.

The primary goals are:
- Understand the core components of an LLM and how they fit together.
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

# Diagrams

Use custom, editable tldraw Offline diagrams saved in `diagrams/`.
Read `diagrams/AGENTS.md` for the diagram index, related decisions, and
diagram maintenance instructions before working on diagrams.

# Code comments

Keep code and comments focused on the current implementation.

Comments explaining non-obvious math, intent, constraints, or invariants
are useful. Historical explanations of previous implementations and
past choices belong in the design log, not in the code.

# Verification

Don't add tests or run verification tasks unless the user asks you to.
Smoke tests are banned unless explicitly requested by the user. This includes
throwaway checks, headless UI runs, and ad hoc verification scripts. Permission
to implement a change or run a learning example does not authorize smoke tests.
