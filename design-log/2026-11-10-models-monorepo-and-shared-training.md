# Models monorepo and shared training UI

## Decision

Broaden the repository from LLMs to small learning projects for different kinds
of models. Use the name `models-from-scratch` and a uv workspace with a single
root lockfile.

Place model projects under `src/<project-name>/`, each with its own package and
`pyproject.toml`. Move the existing linear-neuron project to `src/hello-world/`
with the Python package `hello_world` and the command `uv run hello-world`.
The root workspace installs Hello World for convenient use from the repo root.

Keep shared libraries under `libs/`. The `model-training` package owns the
Textual dashboard, its stylesheet, and the model-independent `TrainingProgress`
and `ProgressCallback` contract. A project supplies a function accepting the
progress callback and a dashboard title. The project owns model construction,
data, CUDA training, hyperparameters, and reporting frequency. The dashboard
owns background execution, UI-thread handoff, progress display, and run controls.
The shared library does not depend on PyTorch or import model projects.

Retain standalone learning scripts in `scripts/` as agreed in
[Retained console experiments](2026-11-10-retained-console-experiments.md).
Preserve the callback and UI separation described in
[Training progress and UI separation](2026-11-10-training-progress-and-ui.md),
while moving its shared contract and dashboard out of the individual project.

## Rationale and tradeoffs

Workspace packages give projects explicit dependencies while sharing one local
environment and dependency resolution. Hyphenated project directories use
underscore-named import packages inside them, following Python conventions.

Injecting a training function lets future models reuse the dashboard without
copying UI code or introducing a training framework, model registry, base class,
or model-specific branches in the shared library. New projects still define
their own launch wiring and training behavior.

The old `llm_from_scratch` package and launch command are removed rather than
kept as compatibility aliases.
