# Tool calling: add SwallowMath to pretraining

Add 6.1% [SwallowMath](https://huggingface.co/datasets/tokyotech-llm/swallow-math/tree/014870710de3c5c70e75a61f7c4946185799f958) to give math-focused text more room in pretraining. Take the full share from Wikipedia, reducing it from 36.1% to 30.0%. Keep every other share from the [PrimeIntellect mix decision](2026-11-27-tool-calling-primeintellect-math-mix.md), including PrimeIntellect at 0.5%; standalone Orca Math stays out.

Use the frozen `pretrain-swallow-math-8k-ctx1024` bundle with the existing 8K tokenizer and 1,024-token windows. It contains about 6.68 billion packed target tokens and is subject to the Llama 3.3 Community License and Common Crawl terms. Each 1,000-update cycle draws 300 from Wikipedia, 287 from FineWeb, 165 from arXiv, 146 from YouTube Commons, 61 from SwallowMath, 36 from Stack Exchange Q&A, and 5 from PrimeIntellect. Report SwallowMath validation loss separately and weight it at 6.1% in the combined loss.

Allow resume from the PrimeIntellect mix and earlier supported mixes. Keep training state and the cursors of sources already in the checkpoint; start newly added sources, including SwallowMath, at their first batch. Reset the best weighted validation loss because it is not comparable across mixes.
