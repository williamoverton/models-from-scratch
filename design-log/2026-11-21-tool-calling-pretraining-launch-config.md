# Tool calling: configure pretraining in one place

Launch text pretraining with `uv run --locked tool-calling pretrain` from the
workspace root. Keep the bundle, run directory, optional warm-start checkpoint,
preview prompt, shard verification, and dashboard/headless choice in
`config.py`, alongside the model and optimizer settings. This makes the current
run reproducible without recovering shell history. The bundle manifest still
owns context length; launch settings are not serialized as model settings.
Data preparation and the tool-training CLI are unchanged.
