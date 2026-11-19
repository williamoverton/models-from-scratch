# Model Training

Read [README.md](README.md) for the callback and dashboard mode contract.

- Require each launcher to select `preview_mode`: `"none"`, `"image"`, or `"text"`.
  Keep the existing image panel layout and only expose **G** in image mode with
  both generation hooks. Metrics-only launchers must not gain preview controls.
- Keep model imports, Torch, tokenization, tool definitions and execution, and
  sampling policy out of this library. Model workers publish complete, display-ready
  snapshots through `TrainingProgress`; update widgets only on the UI thread.
- Keep text payloads immutable and render their labels, context, and completion
  literally. Replace whole previews, retain them across metric-only updates and
  Stop, and clear them on Start. Preview-only reports (`metrics={}` with a preview)
  must not change the training step display, metrics, or loss history.
