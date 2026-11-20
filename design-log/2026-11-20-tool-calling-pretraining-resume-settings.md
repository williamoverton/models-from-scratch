# Tool calling: allow pretraining reporting changes on resume

Pretraining and tool training now ignore `eval_interval`, `eval_batches`, and
`checkpoint_interval` when checking resume compatibility. The prepared bundle,
tokenizer, and settings that affect training updates still have to match, as in
[the pretraining decision](2026-11-20-tool-calling-pretraining.md).

Changing when validation and saves run should not force a fresh run. Changing
`eval_batches` can change the held-out sample size, so the old best loss and new
validation results are not necessarily directly comparable.
