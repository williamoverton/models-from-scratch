# Tool Calling

Train a small language model to propose one tool call and write an answer from
its result. The corpus is synthetic; neither the training dashboard nor the
model executes a generated call.

## Prepare the data

Set up the repository environment using the [development guide](../../DEVELOMENT.md).
Run these commands from the workspace root:

```sh
uv run tool-calling prepare-data --output-dir trained-models/tool-calling/data
```

Preparation uses seed 42 by default and refuses an existing output path.
It generates inspectable JSONL from bundled Python simulations (198 training
and 12 validation schemas) under `structured/`, trains byte BPE on training
text only, then writes `train.parquet` and `validation.parquet`. Each Parquet
row stores `tokens`, `loss_mask`, and `schema_id`; the mask marks assistant
tokens that count toward loss. Keep the splits, tokenizer, and manifest
together. The manifest records the split hashes, tokenizer identity, and
context length.

Older prepared JSONL bundles are not supported. Prepare a new bundle in a
new directory, and start training in a new run directory: checkpoints are
bound to the original bundle's manifest.

The context limit defaults to 350 tokens. If preparation reports overlength
rows, retry with `--context-length N` at least as large as the reported
maximum, using a new output directory. Nothing is silently truncated. The
trainer uses the limit in the manifest; a larger limit can use more GPU memory.
Use `--seed N` to create a different corpus. The example paths keep generated
artifacts out of version control.

## Train in Textual

```sh
uv run tool-calling train \
  --data-dir trained-models/tool-calling/data \
  --run-dir trained-models/tool-calling/runs/first \
  --steps 500
```

Press **S** to start, **X** to stop training, or **Q** to stop and quit.
Training requires CUDA and uses Adam with FP16 mixed precision. Eligible
operations use FP16; model weights and Adam state stay FP32. Gradient scaling
skips overflowing updates without advancing the step count.

The panel below loss shows a fixed prompt after the first completed step, every
500 steps, and at completion. **Generated tool call** is the model's proposal.
**Generated answer from supplied reference result** is a separate generation;
it receives a reference call and result even when the proposed call is wrong.
Control markers such as `<EXECUTE>` are displayed, not acted on. Text remains
visible when progress metrics update or training stops.

`--steps` is the absolute training step limit (default 100,000). `training.log`
and `checkpoint.pt` live in the run directory. A normal Stop or Quit saves the
latest completed step. Reuse the data and run directories to resume, raising
`--steps` if the previous run reached its limit. Only checkpoints from the
current CUDA FP16/Adam trainer can resume. Use a new run directory to start
fresh; incompatible checkpoints are not overwritten.

## What the model learns

The model combines causal convolution with local and global attention. During
training, the whole interaction is visible as a causal prefix; next-token loss
is applied only to assistant tokens, including structured calls and answers.
The validation split holds out schemas, not necessarily operation patterns.
Greedy tool-name accuracy checks call framing and the name, not argument
correctness or end-to-end tool success.
