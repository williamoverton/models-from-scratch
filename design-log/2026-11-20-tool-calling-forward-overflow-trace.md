# Tool calling: trace forward overflow on the original schedule

Restore the shared core without its final L2 normalization. Keep `"l2-norm"`
available for experiments, but do not enable it by default: the output-only
warm start had much higher validation loss and failed with non-finite loss
before update 9. This supersedes the default placement in the
[loop normalization decision](2026-11-20-tool-calling-loop-output-normalization.md).

On a non-finite training loss, replay the same batch with the same model and
FP16 autocast before any backward or optimizer step. Log the first non-finite
dispatch output and its loop pass. Do not slow down healthy updates, skip the
batch, or change training precision in response to the error.
