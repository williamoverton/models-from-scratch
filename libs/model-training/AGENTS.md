# Model Training

Read [README.md](README.md) for the callback and dashboard mode contract.

- Require each launcher to select `preview_mode`: `"none"`, `"image"`, or `"text"`.
  Keep the existing image panel layout and its **G** callback contract.
  Only show text prompt editing and generation controls for interactive text
  launchers that supply the generation hooks. Metrics-only launchers must not gain them.
  Preserve whitespace in submitted prompts. Enter inserts a newline in the
  editor; Generate submits and Escape cancels.
- Show **D** only when a launcher opts in with a non-`None` `step_delay_seconds`.
  The dashboard owns editing and logging this session-local value. The model
  worker reads `app.step_delay_seconds` without accessing widgets and owns waiting.
- Keep model imports, Torch, tokenization, tool definitions and execution, and
  sampling policy out of this library. Model workers publish complete, display-ready
  snapshots through `TrainingProgress`; update widgets only on the UI thread.
- Keep text payloads immutable and render their labels, context, and completion
  literally, using separate theme colors for context and completion. Replace
  whole previews, retain them across metric-only updates and
  Stop, and clear them on Start. Preview-only reports (`metrics={}` with a preview)
  must not change the training step display, metrics, or loss history.
- Keep metric history run-local and independent of model checkpoint formats.
  Only a worker's `TrainingStarted` event establishes the restored step; do
  not infer it from logs or the first metric report.
- Rotate file logs through `SegmentLogHandler` at training start, not at
  stop, dashboard mount, or a size threshold. Use one writer per path.
