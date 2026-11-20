# Tool calling: use FlexAttention for local windows

Use PyTorch FlexAttention with block masks for local attention, and keep causal
SDPA for global attention. Keep the 350-token default and the existing window
semantics. Do not maintain a dense local-mask fallback or a custom kernel.

A dense mask restricts visibility but does not give SDPA sparse tile metadata.
FlexAttention can skip fully masked tiles and reuse mask metadata when layers
or recurrent passes have the same window and sequence length.

FlashAttention Turing is not an alternative for local attention: it supports
causality but not local masks. FlexAttention adds a first-use compilation cost;
its performance on the RTX 2080 at 350 tokens is not established.
