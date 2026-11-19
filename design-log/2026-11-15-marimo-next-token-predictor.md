# End-to-end next-token learning with Marimo

## Decision

Try Marimo for an end-to-end NumPy next-token predictor before decomposing
more transformer operations. Preserve the earlier Jupyter notebooks as
references. This revisits the tool choice in
[notebook-led development](2026-11-13-numpy-stories-notebooks.md).

The learning model averages the previous eight token embeddings, then uses a
linear output layer and softmax over the shared tokenizer vocabulary. Use 16
embedding coordinates and explicit backward gradients. Train on an editable
short teaching passage; this is distinct from the planned full TinyStories
training run, not a corpus subset or change to that dataset decision.

## Why

Isolated query and key operations lacked an end-to-end purpose for the learner.
A working predictor connects inputs, parameters, predictions, loss, and updates.
Marimo lets controls drive the real Python calculations reactively, with visible
editable code and collapsed presentation helpers. No external plotting or widget
library is needed for the loss curve and tables.

## Tradeoffs

Averaging discards order and gives each context token equal weight. This makes
the reason for exploring attention concrete. The small passage demonstrates
learning, not generalization to stories. Weights remain in the notebook session;
long-running full-corpus training still belongs in scripts. This trial does not
add external agent pairing or voice integration.
