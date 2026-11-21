# Tool calling: discard incomplete pretraining windows

Tile each packed row into complete, non-overlapping model-sized windows for
both training and validation. Discard incomplete tails instead of overlapping
with the preceding window. This supersedes the overlap policy in the
[model-owned context decision](2026-11-21-tool-calling-model-context.md).

For a row with 1,024 targets, context 800 uses the first 800, while context
256 uses all 1,024 over four windows. Truncation avoids counting some targets
twice at the cost of leaving the tail unused. The stored bundle is unchanged.
An overlapping run must start a new data cursor; exact splits are unchanged.
