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
| `"none"` | Loss charts and log only; used by Hello World. |
| `"image"` | Image panel above the dashboard; used by Doggie Diffusion. Pass both `generate` and `generation_request` to enable **G** for manual generation. |
| `"text"` | **Generated examples** panel below the loss charts. Pass `generate_text`, `generation_request`, and the initial `generation_prompt` to enable **G** and the **E** prompt editor. |

Call `app.run()`. Use **S** to start, **X** to request a cooperative stop, and
**Q** to stop and quit. The training function should check `stop_event` and
perform any necessary cleanup before returning.

For interactive text previews, **E** opens the editor and **Enter** applies
the prompt and requests a new preview. **G** requests another preview with
the current prompt. While training, the worker consumes `generation_request`
and reads `app.generation_prompt` at a safe update boundary. While idle, the
dashboard calls `generate_text(prompt)` on its generation worker.

## Training logs

Each Start rotates the existing nonempty log before writing the new training
segment. Stop leaves the current log in place. This also applies when starting
headless training or reopening the dashboard and pressing Start.
`training.log.1` is the most recent archive, and `training.log.1000` is the oldest
retained archive. Opening and closing the dashboard without starting does not
touch the existing log.

For another launcher, attach `model_training.logs.SegmentLogHandler(path)` to
a standard Python logger. Call `handler.start_segment()` before writing the
first record of each segment, then detach and close the handler when done.
Use one writer per log path.

## Publishing progress

Report `TrainingProgress` snapshots from the worker. `step` counts completed
parameter updates; use `total_steps=None` when the run has no fixed length.
Each report owns a fresh metrics dictionary. The **Loss** tab plots `loss`
and `validation loss` side by side against completed updates using
`textual-plotext`. The validation chart only adds points when validation is
reported; other metrics remain in the training log. Do not mutate published
dictionaries or Pillow images.

For a resumable run, give `TrainingApp` a `history_path` alongside its
checkpoint. The dashboard loads the saved loss curves on open. The training
worker must publish `TrainingStarted(step)` after loading its checkpoint
(or `TrainingStarted(0)` for a fresh model), before publishing any metrics.
That event discards points beyond the restored step, so a resumed run does
not graph work lost since its last checkpoint.

`MetricsHistory` stores finite scalar reports in SQLite as `(name, step,
value)`. A new value for the same metric and step replaces the old value;
metrics absent from a report are unchanged. Headless runners can use the
same store so their reports appear in the dashboard later. History starts
with reports made while persistence is enabled; existing text logs are not
imported. Launchers without `history_path` keep transient, per-start charts.

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
