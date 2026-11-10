# Retained console experiments

## Decision

Keep the Textual TUI as the main application. Store small, self-contained
console experiments in `scripts/`, with descriptive filenames and run commands
in the README. Retain these exploratory scripts for future learning reference.

## Rationale and tradeoffs

A script makes concepts such as the training loop visible without UI code or
pasted terminal snippets. Experiments may use top-level code and duplicate small
calculations instead of adding reusable abstractions. They are not a second
application architecture and need not track every change in the main app.
