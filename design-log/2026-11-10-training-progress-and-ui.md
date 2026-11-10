# Training progress and UI separation

## Decision

Keep training independent of Textual. The training function publishes
`TrainingProgress` snapshots through a caller-supplied callback at the requested
report interval and on the final step. Snapshots contain completed update counts,
the total step count, and named scalar metrics rather than model-specific fields.

Run training in a background worker. Hand display updates back to Textual's UI
thread with `call_from_thread`; do not change widgets from the training thread.
Training and display refresh remain independent, without a UI training timer or
artificial delays.

Reported loss is the pre-update loss used to calculate that step's gradients,
not an additional evaluation after the parameter update. The dashboard plots
reported loss samples as a compact sparkline rather than a numeric-axis chart.

## Rationale and tradeoffs

The callback keeps the training loop usable without the TUI, while named metrics
let the dashboard display progress without knowing the model's parameters.
Thread handoff keeps the interface responsive and widget updates on the UI thread.

Reusing the loss from the gradient calculation avoids an extra forward pass.
The step count describes completed updates, but its associated loss describes
the calculation that produced that update. Console experiments use the same
pre-update loss convention.

A sparkline gives a compact view of the trend, not precise plotted coordinates.
Its samples are summarized to fit the available width.
