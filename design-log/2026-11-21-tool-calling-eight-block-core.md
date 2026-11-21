# Tool calling: eight-block hybrid core

Extend the [two-pass sandwich-RMSNorm model](2026-11-21-tool-calling-sandwich-rmsnorm.md)
from six to eight shared blocks. Alternate Conv-7 with attention, using
Local-64, Global, Local-128, and Global in that order. Run Conv-7 → Global
once on each side of the shared core.

This borrows LFM3's convolution/attention interleaving and keeps full-context
access in each half of the core. It runs 20 block applications with 12
independent sets of block weights, trading more parameter and optimizer memory
for fewer repeated applications than the older three-pass schedule. Actual
throughput and peak memory on the RTX 2080 are unmeasured. Start a fresh run.
