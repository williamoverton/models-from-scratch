# Tool calling: width 768 and 1,024-token context

Set the shared model width to 768 and the SwiGLU intermediate width to 1,536.
Use 12 heads to retain the 64-dimensional geometry of the existing local
attention kernel. This is a middle step between the previous width of 512 and
1,024; throughput and peak memory are not yet measured.

Default both preparation commands to 1,024 tokens to leave more room for tool
schemas and conversation history. This revises the context choice in the
[pretraining decision](2026-11-20-tool-calling-pretraining.md). The prepared
manifest still determines the training context. Existing bundles stay at 350;
prepare new bundles and use fresh run directories for the new architecture.
