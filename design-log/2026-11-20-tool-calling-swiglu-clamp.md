# Tool calling: clamp SwiGLU products before down-projection

Clamp the signed SwiGLU product to ±2048 by default in every feed-forward
block. Keep FP16 autocast on the projection. Unlike uniformly scaling the
product, this leaves in-range activations unchanged. `None` disables it.

On the original schedule at step 37,000, weighted held-out loss moved from
2.82804 to 2.84333 before any updates; roughly 0.0023% of product values exceeded
the cap. Lower tested caps (1024, 512, 256) hurt held-out loss more. On the exact
batch and model state that produced NaN before update 37,174, the cap gave
finite loss (2.82656) and Adam took the step at the existing gradient scale on
the first attempt. The diagnostic did not save that update or test long-run
stability. Keep the [forward tracer](2026-11-20-tool-calling-forward-overflow-trace.md):
bounding the product does not bound the weighted sum or repair an upstream NaN.
