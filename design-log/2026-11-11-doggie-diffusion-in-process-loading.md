# Doggie Diffusion: start with in-process data loading

## Decision

Supersede the four-worker starting choice in
[the training baseline](2026-11-11-doggie-diffusion-training-baseline.md).
Use `loading_workers=0`: PyTorch loads data in the training process rather
than starting loading subprocesses. A value of one would still spawn a
subprocess and would not remove the multiprocessing startup failure.

The first training attempt failed while Python 3.14 started its multiprocessing
resource tracker under Textual's redirected stderr, with
`ValueError: bad value(s) in fds_to_keep`. Do not add resource-tracker startup
workarounds. Start simple and introduce parallel loading only if measurements
show data loading is a bottleneck.

Keep the existing configurable DataLoader wiring and bounded streaming dataset.
The zero-worker configuration already disables persistent workers and the
spawn context. CUDA training and image preprocessing behavior are unchanged.

This change has not yet been exercised in a training run; it removes the
subprocess startup path implicated by the traceback, not proof that all later
training paths work.
