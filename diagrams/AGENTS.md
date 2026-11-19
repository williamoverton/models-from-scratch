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
| [doggie-diffusion-proposed-unet.tldraw](doggie-diffusion-proposed-unet.tldraw) | Two pages: **01 · U-Net overview**, with aligned resolution rows and color-coded paths; **02 · Inside a residual block**, with a vertical processing lane, routed shortcut, timestep branch, and terminology guide. Agreed operators within illustrative 64×64 network sizing; not implemented. | [Agreed network components](../design-log/2026-11-11-doggie-diffusion-network-components.md); [initial proposal](../design-log/2026-11-10-doggy-diffusion.md); [model documentation](../src/doggie-diffusion/README.md) |
| [numpy-llm-inference-overview.tldraw](numpy-llm-inference-overview.tldraw) | Compact, README-oriented inference overview in four horizontal, alternating-direction rows, with the generation loop outside the model boundary. Shows tokenization, context, model operations, probabilities, sampling, and document-end stopping. Internal components, dimensions, and training remain undecided; no model implementation yet. | [Inference overview](../design-log/2026-11-13-numpy-llm-inference-overview.md); [TinyStories tokenizer](../design-log/2026-11-13-tinystories-tokenizer-training.md) |
| [numpy-llm-transformer-block.tldraw](numpy-llm-transformer-block.tldraw) | Implemented notebook transformer: token and position embeddings, one pre-norm decoder block, causal attention and feed-forward residual paths, final normalization, last-position vocabulary prediction. Exported to `src/numpy-llm-stories/transformer-block.png` and displayed near the top of the notebook. | [Single-block transformer](../design-log/2026-11-15-single-block-transformer.md); [Complete-story notebook dimensions](../design-log/2026-11-15-complete-story-notebook.md); [Implementation](../src/numpy-llm-stories/src/numpy_llm_stories/transformer.py) |

The NumPy overview is exported to
[`src/numpy-llm-stories/inference-overview.png`](../src/numpy-llm-stories/inference-overview.png)
for the [model README](../src/numpy-llm-stories/README.md). Regenerate that image
when changing the overview so the README stays aligned with the editable source.

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
