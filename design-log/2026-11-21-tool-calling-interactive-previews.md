# Tool calling: interactive pretraining previews

Use the dashboard's existing generation action for text pretraining. E opens
a session-local prompt editor; submitting it requests a sample just like G.
Training consumes pending requests at a completed update, and the idle worker
samples the latest checkpoint read-only. Manual samples use independent fresh
randomness; scheduled samples keep their fixed seed unless serving a manual
request at the same step.

This follows the [manual image-preview lifecycle](2026-11-12-fixed-random-and-manual-previews.md)
without sharing model or sampling code. Headless launches keep the configured
prompt and automatic previews. Interactive prompt edits do not change config
or checkpoint compatibility.
