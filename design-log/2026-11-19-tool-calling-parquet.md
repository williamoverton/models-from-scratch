# Parquet for prepared tool-calling data

The [tool-calling pipeline](2026-11-19-tool-calling-data-and-previews.md)
keeps generated conversations as JSONL for inspection and writes its encoded
training and validation splits as Parquet. Each row stores token IDs, the
assistant loss mask, and the generating schema ID. The bundle manifest binds
the tokenizer and split hashes and records the context limit.

Parquet gives the encoded splits an explicit schema and bounded reads and
writes, using the PyArrow dependency already used in Doggie Diffusion. Inline
schema IDs replace the validation sidecar. Projects own their dataset schemas;
this does not introduce a shared loader or require Parquet for generated-in-memory
data.

The trainer still holds the encoded splits in memory for random sampling. The
new manifest version requires preparing a new bundle and starting a new run;
checkpoints remain bound to the manifest they were trained with.
