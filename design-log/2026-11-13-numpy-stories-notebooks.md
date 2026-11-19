# Notebook-led NumPy model development

## Decision

Use Jupyter notebooks for learning and developing the NumPy Stories model.
Keep concept-focused notebooks in `src/numpy-llm-stories/notebooks/`, with
explanations, equations, calculations, and inspected outputs together.

Start with an environment notebook that imports NumPy and the project packages,
inspects an array, and loads the existing tokenizer. Do not implement embeddings
or select model dimensions as part of environment setup.

Make the model a uv workspace package with NumPy and `model-tokenizer` as direct
dependencies. Keep JupyterLab and ipykernel in its optional `notebooks` extra,
using the root lockfile and shared environment. Launch JupyterLab through uv;
use its Python kernel without global kernel registration or machine-specific
interpreter metadata.

After we understand a component and need to reuse it, move its implementation
into the model's Python package. Keep long-running training in scripts rather
than depending on notebook state. This supplements the
[inference overview](2026-11-13-numpy-llm-inference-overview.md); it does not settle
any model internals.

## Rationale and tradeoffs

Notebooks make mathematical learning and array inspection convenient without
requiring a separate dashboard for each experiment. Small reusable modules avoid
making one large notebook the only home of the model.

Cells must run in order from a fresh kernel to avoid hidden state. Standard
Jupyter kernels start in the notebook directory; document relative artifact
paths. Meaningful outputs may be retained for learning, but secrets, server
tokens, huge array dumps, and generated model artifacts must not be committed.
