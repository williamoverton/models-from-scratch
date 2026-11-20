# Tool calling: use native Turing windowed attention

Supersedes [the FlexAttention decision](2026-11-20-tool-calling-flex-attention.md).
Use the pinned `williamoverton/flash-attention-2080ti` fork for local attention.
Keep causal SDPA for global attention and do not maintain a second local backend.
The 350-token default, loop schedule, and attention windows are unchanged.

The fork provides native SM 7.5 FP16 forward and backward sliding-window
kernels, unlike the causal-only `ssiu` fork. The wheel built against the
workspace PyTorch and matched FP32 SDPA outputs and Q/K/V gradients for both
windows on the RTX 2080. No whole-model speedup has been measured.

Install the wheel separately because it is tied to the Python and PyTorch
build. Rebuild it when either changes.
