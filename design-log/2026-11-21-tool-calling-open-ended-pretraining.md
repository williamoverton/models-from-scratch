# Tool calling: run pretraining until stopped

Remove the automatic pretraining stop from the
[budgeted fused AdamW decision](2026-11-21-tool-calling-pretraining-schedule.md).
The 200M-token point now only marks the end of learning-rate decay. Training
continues at the existing floor, with periodic validation and checkpoints.

Keep the existing checkpoint schedule identity so completed runs can resume
with their optimizer, scaler, and data position intact.
