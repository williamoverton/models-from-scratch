# Tool calling: share the middle four blocks

Use `Loop(blocks=..., passes=3)` in `Config.block_schedule` to reuse one core.
The input and output stacks each run Local-64 → Global once. The core runs
Conv-7 → Local-128 → Local-64 → Global three times. Keep SwiGLU, the existing
attention backends, and the 350-token default context.

This keeps 16 block executions while reducing the number of distinct blocks to
8. The single-use stacks can specialize in preparing the input and reading out
the refined state. Compared with the non-looped model, this schedule executes
more global attention, so equal depth does not imply equal runtime.

Following Dory's input reinjection idea, hold the input stack's output fixed.
The first pass uses it directly; subsequent passes add it to the current state
and apply one shared LayerNorm before entering the core. Keep the existing
pre-LayerNorm blocks instead of adopting Dory's L2 normalization throughout.

The schedule is part of checkpoint settings. Start a fresh run; prepared data
can be reused.
