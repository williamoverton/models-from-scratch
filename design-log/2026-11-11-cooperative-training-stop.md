# Cooperative training stop and unlimited progress

## Decision

Extend [the training/UI contract](2026-11-10-training-progress-and-ui.md)
for interactive, unlimited training. `TrainingProgress.total_steps` may be
`None`; the dashboard then displays only completed steps. Finite projects
continue supplying their total.

Dashboard training functions accept `(report, stop_event)`, where `stop_event`
is a standard `threading.Event`. Each run receives a fresh event. Training
checks it between parameter updates; generation must check it between reverse
steps when wired into the dashboard.

Use S to start, X to request Stop, and Q to request Stop followed by Quit.
The dashboard stays responsive and waits for the training function to return
before quitting. A new run cannot start while the previous run is stopping.
A shutdown failure stays visible instead of automatically exiting.

The model project owns checkpoint saving. Doggie Diffusion's agreed normal
Stop/Quit policy is to save its latest completed update before returning;
the dashboard does not save checkpoints itself. Periodic checkpoint and
preview intervals remain independent. Forced process termination cannot
provide this cooperative shutdown guarantee.

## Consequences

The flag avoids coupling cancellation to progress reporting or interrupting
an update/save halfway through. An active CPU read or CUDA operation still
must finish before the next check. Hello World is migrated to accept the
same flag and check it before each update; it does not gain checkpointing.

The dashboard contract changes directly, without a compatibility adapter.
Diffusion stop checks and Doggie Diffusion's training/checkpoint integration
remain subject to the ongoing file-by-file implementation review.
