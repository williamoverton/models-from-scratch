# Tool calling: two-pass recurrence with sandwich RMSNorm

Keep the shared recurrent core and full backpropagation through it, but run it
twice instead of three times. Keep the existing six-block core and re-entry
LayerNorm; this revises the pass count from the [loop decision](2026-11-20-tool-calling-looped-core.md).

Following [LFM3](https://huggingface.co/LiquidAI/LFM3-1.7B/blob/main/modeling_lfm3.py#L443),
use RMSNorm on both sides of the mixer and feed-forward branches. Normalize
branch updates in FP32 before adding them to the unchanged residual. This
controls what each branch contributes without normalizing the full recurrent
state. It does not prevent overflow inside a branch.

Start from fresh weights because the learned normalization parameters change.
Reuse the prepared data and keep the existing precision boundaries.
