# CUDA FP16 and Adam for tool calling

The [tool-calling port](2026-11-19-tool-calling-data-and-previews.md) now uses
Adam with CUDA FP16 autocast and gradient scaling. There is no CPU training
path and no device, precision, or optimizer switch. The offline data pipeline
and the dashboard preview schedule are unchanged.

The workstation's RTX 2080 has native FP16 acceleration but not native BF16.
The original BF16 run did work, but this experiment favors native FP16 and a
single optimizer path over preserving the original Muon update rule. This is
not a performance claim about the migrated trainer.

The training trajectory changes. The new checkpoint version stores one Adam
state and the scaler state. Earlier checkpoints are rejected without being
overwritten; use a new run directory. The prepared dataset format is unchanged.
