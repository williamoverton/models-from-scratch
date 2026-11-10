# Diagrams

Use custom, editable tldraw Offline documents (`.tldraw`) in this folder to
explain model architecture, calculations, and other concepts alongside the code.
These are maintained learning aids, not automatically generated model graphs
or live training displays.

Read the `tldraw-offline` skill before creating or editing a diagram. Use the
app's supported API to create, edit, and save documents; do not handcraft archive
files or edit an open document's internal files directly.

## Index

Paths in this table are relative to this folder.

| Diagram | Purpose | Related decision |
| --- | --- | --- |
| [single-neuron.tldraw](single-neuron.tldraw) | Explains the linear neuron calculation `ŷ = wx + b`, distinguishes input from learnable weight and bias, and shows the illustrative calculation `2 × 3 + 1 = 7`. No model implementation yet. | [Diagram format and workflow](../design-log/2026-11-10-editable-tldraw-diagrams.md) |

## Maintenance

- Update this index when adding, renaming, removing, or changing a diagram's scope.
- Link relevant design-log entries and implementation files when they exist.
  Do not invent links or imply that a proposed model is implemented.
- Keep diagrams aligned with the concepts and code they explain. Clearly label
  illustrative values; do not present them as actual training results.
- Prefer a small, focused diagram with readable labels over an exhaustive graph.
  Distinguish data, operations, and learnable parameters where relevant.
- Use real bound connections so arrows remain attached when shapes move.
- Inspect existing content before editing; preserve unrelated user work.
- Resolve actionable diagram lints, verify the changed diagram through the app,
  and save the local document before reporting completion.
- Record changes to agreed diagram conventions in the design log rather than
  embedding historical explanations in every diagram.
