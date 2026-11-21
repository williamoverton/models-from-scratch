# Tool calling: budgeted fused AdamW pretraining

Use PyTorch fused AdamW for pretraining on the RTX 2080. Defer Muon: the
installed implementation uses BF16 for orthogonalization, which Turing does
not accelerate natively. Tool training keeps its existing optimizer.

For the fresh run, linearly warm up to `3e-4` over 4M target tokens and decay
with cosine interpolation to `3e-5` at 200M. Finish at a full update boundary
and validate and checkpoint there. Count only committed updates so overflow
retries and restarts do not move the schedule. This supersedes the fixed-rate,
open-ended pretraining policy and the learning-rate override on
[resume](2026-11-20-tool-calling-pretraining-warm-start.md). These rates and
budget are starting choices, not tuned optima.
