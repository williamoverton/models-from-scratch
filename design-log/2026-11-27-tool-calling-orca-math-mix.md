# Tool calling: add Orca Math to pretraining

Reserve two of every 1,000 updates for Orca Math's worked question-and-answer documents. Take one update each from Wikipedia and FineWeb and leave Stack Exchange Q&A unchanged. The aim is light exposure to the Q&A pattern, not a math-heavy run.

Use a separate frozen bundle with the existing 8K tokenizer. Report its validation loss independently and weight it at 0.2% in the combined loss. Follow the [FineWeb cutover](2026-11-22-tool-calling-fineweb-mix.md) precedent: preserve training state and existing cursors, start the new source at its first batch, and reset the best-loss record because the validation mix changed.
