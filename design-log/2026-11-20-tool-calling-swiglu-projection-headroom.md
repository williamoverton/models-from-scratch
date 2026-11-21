# Tool calling: give SwiGLU's FP16 down-projection more headroom

The [SwiGLU product clamp](2026-11-20-tool-calling-swiglu-clamp.md) passed the
original failing batch but the resumed run overflowed the same down-projection
again before update 37,908, despite its input obeying the cap.

Keep the clamp and the FP16 matrix multiply. Scale the projection input and
bias by 1/4, then multiply the result by 4 in FP32 before adding it to the
residual stream. This preserves the affine map in exact arithmetic while
increasing the magnitude it can represent at the FP16 output boundary. The
checkpoint parameter layout does not change. FP16 rounding and underflow can
still differ, and this does not protect other operations from overflow.
