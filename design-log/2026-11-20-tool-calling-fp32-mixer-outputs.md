# Tool calling: keep mixer outputs in FP32

After [moving the SwiGLU down-projection to FP32](2026-11-20-tool-calling-swiglu-fp32-down-projection.md),
update 56,460 first overflowed in the short-convolution output projection.
Keep its input projection under FP16 autocast and use FP32 for the gate
products, depthwise convolution, and output projection so the amplifying
operations and their consumers share the same range.

Update 59,699 first overflowed in the global attention output projection.
Use FP32 for the output projection in both attention mixers, without changing
Q/K/V, gating, SDPA, or the FP16 sliding-window kernel. Both changes preserve
checkpoint state and write directly into the existing FP32 residual stream.
