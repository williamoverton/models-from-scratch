# Tool calling: warm-start or resume compatible pretraining weights

`pretrain --init-from` loads model weights from a latest or best pretraining
checkpoint into a separate run with a fresh optimizer, scaler, cursor and
validation history. Require a matching tokenizer and exact parameter names
and shapes, not the original data bundle or schedule.

Ordinary pretraining resume preserves trained weights, Adam moments, scaler,
RNGs and the cursor. Require the original bundle, batch size and sampler seed,
but allow model settings changes that still load the saved weights exactly.
Use the current learning rate. This supersedes the schedule restriction in the
[loop normalization decision](2026-11-20-tool-calling-loop-output-normalization.md)
and the narrower [resume policy](2026-11-20-tool-calling-pretraining-resume-settings.md).
Tool training keeps its existing checkpoint rules.
