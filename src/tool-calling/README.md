# Tool Calling

Train a small language model to propose one tool call and write an answer from
its result. Pretrain it on ordinary text or train it on synthetic tool calls.
Neither the training dashboard nor the model executes a generated call.

## Install the Turing attention extension

On Linux x86-64 with Python 3.14, `uv sync` installs the SM 7.5 wheel from
`.wheels/` without compiling CUDA. On a fresh checkout, copy the wheel built
from the [pinned fork](https://github.com/williamoverton/flash-attention-2080ti/tree/3b3e89957f702999a8d1759c36be9136066c1d59)
into place before syncing:

```sh
install -Dm644 /path/to/flash_attn-2.7.3-cp314-cp314-linux_x86_64.whl \
  .wheels/flash_attn-2.7.3-cp314-cp314-linux_x86_64.whl
uv sync
```

The wheel is local and not checked into Git. Build it only if you don’t
already have a copy. It targets Python 3.14 and PyTorch 2.15 (`cu132`).

## Pretrain on text

Prepare a frozen local bundle once. The ZIM reader needs `libzim` only during
preparation; use local article Parquet (`id`, `title`, `text`) to skip that
dependency. The Q&A reader accepts gzip JSONL shards from the linked
[Stack Exchange dataset](https://huggingface.co/datasets/flax-sentence-embeddings/stackexchange_title_best_voted_answer_jsonl).
The downloaded snapshot is revision `88957a0e825f49aeb2a7bfd828cb46b79010b286`.

```sh
uv run --with libzim==4.1.0 tool-calling prepare-pretrain \
  --wikipedia /mnt/StorageBox/project-nomad/storage/zim/wikipedia_en_all_maxi_2026-02.zim \
  --qa /mnt/StorageBox/datasets/stackexchange-title-best-voted-answer \
  --tokenizer trained-models/tokenizers/simple-wikipedia-comparison/8192.json \
  --output-dir /mnt/StorageBox/datasets/pretrain-wiki-qa-8k

uv run tool-calling pretrain \
  --data-dir /mnt/StorageBox/datasets/pretrain-wiki-qa-8k \
  --run-dir trained-models/tool-calling/runs/pretrain-wiki-qa-8k-looped
```

The default context is 350 tokens. Preparation splits documents before
packing and writes disk-backed windows of 351 IDs for shifted inputs and
targets. Omit `--windows-per-source` to prepare all training windows, or set
it to cap each source's preparation before an overnight run. Validation uses
up to 1,024 windows per source. Each preparation uses a new directory; a
running job never picks up additional shards.
Preparation parses and tokenizes in worker processes, using all available
logical CPUs by default. Use `--workers N` to leave CPU capacity for other jobs.
It prints per-source window counts while it runs.

Startup checks the manifest, tokenizer hash, and shard paths and sizes. It
does not scan shard contents by default. Add `--verify-shards` to `pretrain`
to read every shard and check its SHA-256 and token ID range. Without the flag,
same-size shard changes aren't detected at startup.

In Textual, press **S** to start or resume, **X** to stop, or **Q** to stop and
quit. The trainer loops until stopped and targets **90% Wikipedia / 10% Q&A**
by training target tokens. It reports held-out loss separately for each source.
`pretrain-latest.pt` stores resumable state; `pretrain-best.pt` stores weights
at the best weighted validation loss. Use the same data and run directories
to resume. `--batch-size` defaults to 8; if that does not fit in GPU memory,
start a new run directory with a lower value.

The **Generated examples** panel samples a continuation after the first
completed update of each session and every 500 updates. It starts with
`Training an LLM is` by default. Pass `--sample-prompt "Your opening text"`
to change the prompt without changing checkpoint compatibility.

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
  --run-dir trained-models/tool-calling/runs/looped
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

### Block schedule

Edit `Config.block_schedule` in [`config.py`](src/tool_calling/config.py) to
change the block order. The default is:

| Stage | Block order |
| --- | --- |
| Input · once | Local-64 → Global |
| Shared core · three passes | Conv-7 → Local-128 → Local-64 → Global |
| Output · once | Local-64 → Global |

This executes 16 blocks using eight distinct sets of block weights. Every block
includes a SwiGLU feed-forward network. The first core pass takes the input
stack's output directly. Before each later pass, that same saved output is
added to the latest core state and normalized with a shared LayerNorm.

Use `("local", 64)` for a 64-token causal window (including the current token),
`"global"` for full causal attention, or `"convolution"` for causal convolution.
`Loop(blocks=(...), passes=3)` repeats a sequence of these ordinary blocks;
loops do not nest.

Local attention uses the Turing fork's native FP16 sliding-window kernels.
Global attention remains on causal PyTorch SDPA. The number of visible tokens
and the checkpoint parameter layout are unchanged by the backend switch.

Use a new `--run-dir` when changing the schedule, including when switching from
the previous non-looped model. Existing prepared data can be reused; the
default context is still 350 tokens.
