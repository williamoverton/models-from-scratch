# Tool calling: normalize shared-core outputs

Add a standalone `"l2-norm"` schedule block after the last attention block in
the shared core, so it runs after every pass. It L2-normalizes each token's
hidden vector in FP32 without learned parameters. The same block can be placed
in the outer stack or elsewhere in the core.

This borrows Dory's output-boundary normalization without replacing the
[existing loop re-entry LayerNorm](2026-11-20-tool-calling-looped-core.md) or
changing the attention kernels. It limits the magnitude of finite state passed
onward, but cannot repair an overflow inside the core. Changing the schedule
requires a fresh run; keep the previous schedule to resume an older checkpoint.
