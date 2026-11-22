# Tool calling: add FineWeb to pretraining

Replace 20 percentage points of Wikipedia in the [original mix](2026-11-20-tool-calling-pretraining.md) with FineWeb `sample-10BT`: seven Wikipedia, two FineWeb, and one Stack Exchange update per ten completed updates. FineWeb adds broader web prose while keeping the Q&A share fixed. Weight validation by the same mix and report each source independently.

Keep the existing 1,024-token packs and shared 8K tokenizer. Resume the original run from its latest checkpoint, preserving weights, optimizer, scaler, RNGs, step, learning-rate position, and Wikipedia/Q&A cursors. Persist the cutover step with both manifest identities and the ordered mix so later resumes continue all three cursors. Reset the best-loss record because the new weighted validation objective is not comparable.
