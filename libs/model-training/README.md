# Model Training

Shared Textual dashboard for the model projects in this workspace. It runs a
model's training function in a worker thread and displays progress on the UI
thread. The model project owns data loading, training, sampling, and checkpointing.

## Launching the dashboard

Pass `TrainingApp` (from `model_training.app`) a training function accepting
`(report: ProgressCallback, stop_event: threading.Event)`, a title, and a
`preview_mode`:

| Mode | Dashboard |
| --- | --- |
| `"none"` | Metrics, loss history, and log only; used by Hello World. |
| `"image"` | Image panel above the metrics; used by Doggie Diffusion. Pass both `generate` and `generation_request` to enable **G** for manual generation. |
| `"text"` | Read-only **Generated examples** panel below the loss chart. No manual generation key. |

Call `app.run()`. Use **S** to start, **X** to request a cooperative stop, and
**Q** to stop and quit. The training function should check `stop_event` and
perform any necessary cleanup before returning.

## Publishing progress

Report `TrainingProgress` snapshots from the worker. `step` counts completed
parameter updates; use `total_steps=None` when the run has no fixed length.
Each report owns a fresh metrics dictionary. A metric named `loss` adds one
point to the loss chart. Do not mutate published dictionaries or Pillow images.

An optional `preview` carries display-ready data matching the launcher's mode:
`ImageGenerationPreview` for images, or `TextGenerationPreview` for text. The
preview's own `step` is the step that produced the sample. A text snapshot contains
an immutable tuple of `TextGenerationExample(label, context, completion)` values.
For example, inside an existing training function after a completed step:

```python
from model_training.progress import (
    TextGenerationExample,
    TextGenerationPreview,
    TrainingProgress,
)

report(TrainingProgress(
    step=step,
    total_steps=total_steps,
    metrics={},
    preview=TextGenerationPreview(step=step, examples=(
        TextGenerationExample(
            label="Generated continuation",
            context=prompt,
            completion=generated_text,
        ),
    )),
))
```

Use `metrics={}` for a preview-only report. It replaces the preview without
altering the step, metrics, or loss chart. A report can also carry both metrics
and a preview. Text labels, context, and completions render literally and wrap
at the panel width; markup and control markers are not interpreted as actions.
The text panel waits for its first snapshot, keeps the latest one through metric
updates and Stop, and returns to the waiting state when Start begins another run.
