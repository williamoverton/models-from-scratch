# Tool Calling

Train a small language model to propose one tool call and write an answer from
its result. The corpus is synthetic; neither the training dashboard nor the
model executes a generated call.

## Prepare the data

Set up the repository environment using the [development guide](../../DEVELOMENT.md).
Run these commands from the workspace root:

```sh
uv run tool-calling prepare-data --output-dir datasets/tool-calling
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
  --data-dir datasets/tool-calling \
  --run-dir trained-models/tool-calling/runs/first
```

Press **S** to start or resume. Training runs until you press **X** to stop or
**Q** to stop and quit. The dashboard shows completed steps without a total.
Training requires CUDA and uses Adam with FP16 mixed precision. Eligible
operations use FP16; model weights and Adam state stay FP32. Gradient scaling
skips overflowing updates without advancing the step count.

The panel below loss shows a fixed prompt after the first completed step of
each session and every 500 steps. **Generated tool call** is the model's proposal.
**Generated answer from supplied reference result** is a separate generation;
it receives a reference call and result even when the proposed call is wrong.
Control markers such as `<EXECUTE>` are displayed, not acted on. Text remains
visible when progress metrics update or training stops.

`training.log` and `checkpoint.pt` live in the run directory. The trainer
checkpoints periodically and saves the latest completed step on Stop or Quit.
Reuse the data and run directories to resume a compatible checkpoint. Use a
new run directory to start fresh; incompatible checkpoints are not overwritten.

## What the model learns

The model combines causal convolution with local and global attention. During
training, the whole interaction is visible as a causal prefix; next-token loss
is applied only to assistant tokens, including structured calls and answers.
The validation split holds out schemas, not necessarily operation patterns.
Greedy tool-name accuracy checks call framing and the name, not argument
correctness or end-to-end tool success.

### Attention windows

Edit `Config.block_schedule` in [`config.py`](src/tool-calling/config.py) to
set the mixer for each block. Use `("local", 64)` for a 64-token causal window
(including the current token), `"global"` for full causal attention, or
`"convolution"` for a causal convolution. By default, blocks 5 and 13 use
64 tokens; blocks 7 and 11 use 128. Global attention is at blocks 3, 9, and 15.

Changing the schedule requires a new `--run-dir`, but you can reuse the
prepared data bundle. Checkpoints from the previous uniform-window
configuration cannot resume under the per-layer schedule.
