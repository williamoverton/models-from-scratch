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

The default run uses four frozen 1,024-token bundles in `/mnt/StorageBox/datasets`:
`pretrain-wiki-qa-8k-ctx1024` for Wikipedia and Q&A,
`pretrain-fineweb-8k-ctx1024` for [FineWeb `sample-10BT`](https://huggingface.co/datasets/HuggingFaceFW/fineweb/viewer/sample-10BT),
`pretrain-arxiv-8k-ctx1024` for [arXiv Papers](https://huggingface.co/datasets/common-pile/arxiv_papers),
and `pretrain-youtube-8k-ctx1024` for [YouTube Commons](https://huggingface.co/datasets/common-pile/youtube).
All four use the same 8K tokenizer. The preparation command below only builds
the Wikipedia/Q&A bundle; skip it if that bundle already exists.

```sh
uv run --with libzim==4.1.0 tool-calling prepare-pretrain \
  --wikipedia /mnt/StorageBox/project-nomad/storage/zim/wikipedia_en_all_maxi_2026-02.zim \
  --qa /mnt/StorageBox/datasets/stackexchange-title-best-voted-answer \
  --tokenizer trained-models/tokenizers/simple-wikipedia-comparison/8192.json \
  --output-dir /mnt/StorageBox/datasets/pretrain-wiki-qa-8k-ctx1024

uv run --locked tool-calling pretrain
```

Run from the workspace root. `PretrainConfig` in
[`config.py`](src/tool_calling/config.py) selects the prepared bundles
(`data_dir`, `fineweb_dir`, `arxiv_dir`, and `youtube_dir`), the run directory, and launch behavior.
`pretrain` takes no training arguments.

`Config.context_length` in [`config.py`](src/tool_calling/config.py) controls
the model context. The default bundle stores 1,024-token windows (1,025 IDs
for shifted inputs and targets). Set the model context lower to reuse the same
bundle as complete, non-overlapping windows. A 1,024-token row supplies one
window at 800 (the last 224 targets are unused), two at 512, or four at 256.
To train with a context longer than the stored windows, select or prepare a
wider bundle. Runs started with the old overlapping layout cannot resume
with truncation; use a new run directory.

Preparation splits documents before packing. Omit `--windows-per-source`
to prepare all training windows, or set it to cap each source. Preparation
stores up to 1,024 validation windows per source. Each preparation uses a new directory; a
running job never picks up additional shards.
Preparation parses and tokenizes in worker processes, using all available
logical CPUs by default. Use `--workers N` to leave CPU capacity for other jobs.
It prints per-source window counts while it runs.

During pretraining, fetched Wikipedia training windows are filtered for
complete numeric citation markers such as `[72][73]`. This does not rewrite
the bundle or reset the checkpoint. A marker split across windows is not
removed; legitimate text like `[72]` is indistinguishable from a citation.
Q&A and held-out validation windows are unchanged. Shortened windows keep
their original tensor shape, but padding is excluded from the loss. The
learning-rate schedule and token counters still use the original window
size, preserving the schedule position when resuming.

Startup checks the manifest, tokenizer hash, and shard paths and sizes. It
does not scan shard contents by default. Set `PretrainConfig.verify_shards`
to `True` to read every shard and check its SHA-256 and token ID range. Otherwise,
same-size shard changes aren't detected at startup.

### Slow down overnight

In the pretraining dashboard, press **D** to edit the delay while training
or while idle. Enter seconds (try `0.5`), press **Enter** to apply, or **Esc**
to cancel. Enter `0` to turn it off. Changes take effect without restarting,
including during an existing delay, and last until you close the dashboard.

`PretrainConfig.step_delay_seconds` in [`config.py`](src/tool_calling/config.py)
sets the initial dashboard value and the headless delay. The default is `0.0`.

The worker idles after each completed optimizer update. Each forward-only
validation batch uses one third of the same live delay. Reported training
tokens/s includes update delays but excludes validation time. Checkpoint
compatibility, learning-rate schedule, and validation cadence in steps are
unchanged. This spaces out GPU work without capping power during individual
batches or slowing previews.

### Run without the dashboard

Set `PretrainConfig.headless` to `True` to start pretraining immediately
without a TTY. The `train` command still uses `--headless`.

Metrics, text previews, and errors stream to stderr and are written to the
[training log](#training-logs). Send `SIGTERM` to the training PID printed at
startup (or press Ctrl+C in the foreground) and wait for `Training stopped.`
The worker saves its latest completed update before exiting. A failed run
exits with status 1; a cooperative stop exits with status 0.

### Checkpoints and previews

In Textual, press **S** to start or resume, **X** to stop, or **Q** to stop and
quit. Pretraining uses fused AdamW. The source mix is proportional to packed
training tokens, rounded to a 1,000-update cycle: **36.4% Wikipedia, 28.9%
FineWeb, 16.5% arXiv, 14.6% YouTube Commons, and 3.6% Q&A**. Each update draws
from one source. Validation reports each source separately and weights the
combined loss by the same mix.
Training runs until you stop it. The learning rate
warms up over 4M target tokens to `3e-4`, then decays to `3e-5` at
`Config.pretrain_decay_end_tokens` (200M by default) and stays there. Only
completed updates advance the schedule. Validation and checkpointing remain
periodic, and stopping saves the latest completed update.

`pretrain-latest.pt` stores resumable state; `pretrain-best.pt` stores weights
at the best weighted validation loss. To resume pretraining, use the same
bundle manifests, source mix, run directory, model context, batch size, seed,
and learning-rate schedule. The block
schedule may change if the parameter names and shapes still match. Resume keeps
AdamW moments, scaler, data cursor, and schedule position. Checkpoints from
the old Adam optimizer can only initialize weights via `PretrainConfig.init_from`, if
the model and tokenizer still match. Historical best loss may not be comparable
after a block schedule or validation-sample change.

To reuse weights without continuing old run state, set `PretrainConfig.init_from`
to the path of a latest or best pretraining checkpoint and set `run_dir`
to a separate run directory.

This requires the same tokenizer and matching parameter names and shapes.
Step, data cursor, validation history, optimizer state, and scaler start fresh.
Once the new run has a checkpoint, set `PretrainConfig.init_from` back to `None` to resume it.

To adopt the proportional mix in an existing run, stop normally and relaunch
with the same run directory and `init_from = None`. The trainer accepts
checkpoints from the prior arXiv, FineWeb, and original Wikipedia/Q&A mixes
when their source bundles are unchanged. It retains optimizer, scaler, RNG state, completed step,
learning-rate position, and existing source cursors. New sources start at
their first batch. The first validation under the new mix replaces the old
best checkpoint because the weighted losses are not comparable.

On a non-finite training loss, pretraining replays the failed batch before
backpropagation and logs the first non-finite operation it can observe,
including its module and loop pass. It still stops without applying the update.

The **Generated examples** panel samples after the first completed update of
each session and every 500 updates. Press **E** to edit the prompt, **Enter**
to apply it and immediately request a preview, or **Esc** to cancel.
Press **G** to draw a fresh sample without changing the prompt. While training,
requests run at a completed update; while idle, they use the latest checkpoint
without starting training or writing a checkpoint.

Edits last for the dashboard session. `PretrainConfig.sample_prompt` sets the initial
prompt and the headless prompt, without affecting checkpoint compatibility.

Set `Config.sample_temperature` in [`config.py`](src/tool_calling/config.py)
to change how much the generated previews vary in both `pretrain` and `train`.
The default is `0.95`; lower values favor more likely tokens. Use a finite,
positive value and relaunch to apply it. The setting does not affect training
updates or checkpoint compatibility.

## Training logs

For both `pretrain` and `train`, each headless launch or dashboard start
opens a new `<run-dir>/training.log` segment. This includes pressing **S**
after **X** (Stop). Launch archives any nonempty previous log as
`training.log.1`, shifting older archives up to `training.log.1000`. The
`.1` archive is the newest and `.1000` is the oldest retained. Stopping or
quitting does not rotate the log.

## Training metric history

Dashboard and headless runs share a SQLite history in the run directory:
`pretrain-metrics.sqlite3` for `pretrain`, and `metrics.sqlite3` for `train`.
The database records finite scalar metrics by step, not text previews or
log messages. On resume it keeps metrics through the restored checkpoint step
and removes later points, which may come from updates that were not saved.
Existing `training.log` files are not imported.

## Prepare the data

Set up the repository environment using the [development guide](../../DEVELOMENT.md).
Run these commands from the workspace root:

```sh
uv run tool-calling prepare-data --output-dir datasets/tool-calling-1024
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

The preparation limit defaults to 1,024 stored tokens per interaction. If
preparation reports overlength rows, retry with `--context-length N` at least
as large as the reported maximum, using a new output directory.
`Config.context_length` controls the model separately. Training rejects a bundle
if an interaction's shifted inputs exceed that setting; it never truncates
the prompt or the targets.
Use `--seed N` to create a different corpus. The example paths keep generated
artifacts out of version control.

## Train in Textual

```sh
uv run tool-calling train \
  --data-dir datasets/tool-calling-1024 \
  --run-dir trained-models/tool-calling/runs/looped-1024
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
| Input · once | Conv-7 → Global |
| Shared core · two passes | Conv-7 → Local-64 → Conv-7 → Global → Conv-7 → Local-128 → Conv-7 → Global |
| Output · once | Conv-7 → Global |

The model uses a 768-dimensional hidden state, 12 attention heads of 64
dimensions each, and a 1,536-dimensional SwiGLU intermediate layer.

The first core pass takes the input stack's output directly. Before the second
pass, that saved output is added to the latest core state and normalized with
LayerNorm. Gradients flow through both passes during training.

Each mixer and feed-forward branch applies RMSNorm to its input and to its
update before adding that update to the residual stream. The residual itself
bypasses the branch.

Use `("local", 64)` for a 64-token causal window (including the current token),
`"global"` for full causal attention, or `"convolution"` for causal convolution.
Use `"l2-norm"` anywhere in the outer stack or inside a `Loop` to normalize
each token's hidden vector to unit L2 norm (with an epsilon floor). It computes
in FP32, preserves the input dtype, and has no learned parameters or
feed-forward network. Loops do not nest.

`Config.swiglu_product_limit` clamps the signed SwiGLU product before its
down-projection in every block, including every shared-core pass. The default
is `2048.0`; `None` disables it. The clamp leaves in-range products unchanged
and cannot repair NaNs produced earlier. The SwiGLU down-projection runs in
FP32 and keeps its output in FP32 through the residual addition. Its FP16
output overflowed even with the clamp and additional scaling. Gate and value
projections still use FP16 autocast.

Short convolution keeps its input projection under FP16 autocast, then uses
FP32 for both gate products, the depthwise convolution, and the output
projection. The FP16 output projection overflowed on a finite gated input.

Local attention uses the Turing fork's native FP16 sliding-window kernels.
Global attention remains on causal PyTorch SDPA. Both attention mixers use
FP32 for the output projection into the residual stream; the attention
kernels and query, key, value, and gate projections are unchanged.

Tool training requires a new `--run-dir` when changing the schedule.
Pretraining can resume parameter-compatible changes or warm-start a separate
run as described above. Existing prepared data can be reused.
The sandwich RMSNorm architecture changes learned parameter names and requires
a fresh run; old LayerNorm checkpoints cannot initialize it.
