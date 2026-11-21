# Tool calling: keep SwiGLU down-projections in FP32

Replace the [scaled FP16 down-projection](2026-11-20-tool-calling-swiglu-projection-headroom.md)
with FP32 in every SwiGLU block. Scaling delayed but did not prevent overflow:
update 42,412 failed with finite clamped inputs and an infinite FP16 projection
output. Keep the product clamp, FP16 gate/value projections, and the existing
attention backends. The down-projection returns FP32 directly into the residual;
parameter names, shapes, and optimizer state remain compatible.
