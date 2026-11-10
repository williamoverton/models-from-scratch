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

Use PyTorch for tensor operations and automatic differentiation.
Implement the model components and training loop ourselves rather than
using a ready-made model.

Prefer straightforward code over abstractions that hide the concepts
we are trying to learn.

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

# Code comments

Keep code and comments focused on the current implementation.

Comments explaining non-obvious math, intent, constraints, or invariants
are useful. Historical explanations of previous implementations and
past choices belong in the design log, not in the code.

# Verification

Don't add tests or run verification tasks unless the user asks you to.
