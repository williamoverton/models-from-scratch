# Tool calling: replace standalone Orca Math with PrimeIntellect Math

Replace the standalone 0.2% Orca Math source from the [Orca Math decision](2026-11-27-tool-calling-orca-math-mix.md) with 0.5% [PrimeIntellect Verifiable Math Problems](https://huggingface.co/datasets/PrimeIntellect/verifiable-math-problems/tree/2ad7c92aaa5efa5a4a8c74e43d57b432529f339b). It broadens the worked math examples while keeping math a small part of pretraining. Use the full snapshot, including its Orca examples, rather than maintaining a filtered PrimeIntellect bundle and sampling standalone Orca alongside it. Keep the raw datasets.

Use the frozen `pretrain-primeintellect-math-8k-ctx1024` bundle with the existing 8K tokenizer and 1,024-token windows. Each 1,000-update cycle draws 361 from Wikipedia, 287 from FineWeb, 165 from arXiv, 146 from YouTube Commons, 36 from Stack Exchange Q&A, and 5 from PrimeIntellect. Report PrimeIntellect validation loss separately and weight it at 0.5% in the combined loss.

Allow resume from the Orca mix and all previously supported mixes. Retain training state and the cursors of surviving sources, start PrimeIntellect at its first batch, and retire the Orca cursor. Check the historical Orca manifest against its pinned identity without requiring the retired packed bundle on disk. Reset the best weighted validation loss because it is not comparable across mixes.
