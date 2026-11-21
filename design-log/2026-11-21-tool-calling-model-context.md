# Tool calling: model-owned context length

Use `Config.context_length` for the model in both training modes and in
pretraining previews. This supersedes manifest-owned context in the
[pretraining launch config decision](2026-11-21-tool-calling-pretraining-launch-config.md).
The manifest still describes and validates the prepared data, but choosing a
bundle no longer changes model shape or context-dependent GPU memory use.

Pretraining indexes shorter windows inside each prepared row without
repacking or dropping targets. The final window overlaps when the lengths do
not divide evenly; a model context larger than a stored row requires a wider
bundle. Tool training instead rejects any interaction whose shifted inputs
exceed the model context, preserving the prompt and supervision together.
Changing model context requires a new run because positional embedding shape
and, for pretraining, window sampling and token accounting change.
