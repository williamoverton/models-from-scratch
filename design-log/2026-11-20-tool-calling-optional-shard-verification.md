# Tool calling: opt-in pretraining shard scans

Keep the manifest and tokenizer binding from [the text pretraining decision](2026-11-20-tool-calling-pretraining.md). On every start or resume, validate the manifest, tokenizer, and shard paths and sizes, then memory-map the shards. Scan all shard bytes for SHA-256 and token ID validity only when `--verify-shards` is set.

The full scan read 55 GB and added roughly a minute to each launch. Skipping it assumes the prepared shard contents are unchanged: same-size corruption or replacement is no longer caught at startup without the flag. The verification choice is not part of checkpoint settings.
