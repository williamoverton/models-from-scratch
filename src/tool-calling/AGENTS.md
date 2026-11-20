# Tool Calling

- Keep data preparation, framing, model, training, and checkpoint ownership in `tool_calling`. Use the shared `model-tokenizer` for ordinary byte BPE and `model-training` for the dashboard. Neither shared library should depend on this project.
- Keep bundled schema splits separate. Schema code is trusted local simulation; do not connect it to live services or execute model-generated calls. Fit the vocabulary on training text only. Keep structured JSONL inspectable and write prepared splits as typed Parquet with inline schema IDs and assistant-only loss masks.
- Pretraining prepares disk-backed next-token windows separately from tool-call data. Keep source readers out of the training loop; split by document before packing and bind resume to the prepared manifest and tokenizer.
- The prepared manifest owns the context limit for both the loader and model. Do not drop or truncate overlength data or weaken artifact identity checks. Keep generated corpora, tokenizers, logs, and run checkpoints in ignored local paths.
- Keep local attention windows inline in `Config.block_schedule`; changing the schedule requires a fresh run, not a checkpoint migration.
- Training is CUDA-only and uses Adam with FP16 autocast and gradient scaling. Do not add alternate device, precision, optimizer, or checkpoint compatibility paths. Stop and Quit must preserve the latest completed training state without publishing a partially generated preview.
- Training runs without a step ceiling and reports completed steps without a total. Keep periodic saves and previews independent of cooperative Stop and Quit.
- Keep the fixed preview's generated call separate from the answer conditioned on a reference call and result. The dashboard receives literal display text, not model state or token IDs.
- Keep the README current with launch, preparation, and recovery commands. Follow the root policy on explicit test and smoke-run authorization.
