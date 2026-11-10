# Editable tldraw diagrams

## Decision

Maintain custom tldraw Offline diagrams as `.tldraw` files in `diagrams/`.
Keep their index, purpose, related decision links, and agent maintenance guidance
in `diagrams/AGENTS.md`. The root `AGENTS.md` provides a brief pointer there.

## Why

Editable diagrams let us explain the model's layout and calculations at the
level useful for learning, without adding visualization dependencies to the
Python application.

## Alternatives and tradeoffs

We discussed automatic architecture and computation-graph viewers, including
TensorBoard, Netron, and torchviz, and an in-terminal custom diagram. Separate
tldraw documents keep the application simple and allow tailored explanations,
but must be maintained alongside the code. They do not automatically reflect
model changes or live parameter values; example values must be labeled.
