# Tool-calling text pretraining

## Decision

Pretrain the existing language model at context 350 with the 8,192-token
Simple English Wikipedia byte-BPE vocabulary, including the existing tool
control tokens. Start with 90% full English Wikipedia and 10% Stack Exchange
Q&A by next-token targets. Use the local February 2026 NOMAD Wikipedia archive
and the pinned Stack Exchange snapshot documented in the project README.

Keep corpus readers in offline preparation. Split by document before packing
and bind resumable training to one prepared manifest and tokenizer. Run until
stopped and report validation separately by source. Keep a resumable latest
checkpoint and weights at the best weighted validation loss.

## Why and tradeoffs

The 8K tokenizer cut held-out Wikipedia token counts by 26% versus the old
2K tool-calling vocabulary without making complete tool calls longer. The
16K candidate saved only another 4.7% on Wikipedia and doubled the output
vocabulary. Keeping the tokenizer and context fixed across pretraining and
later tool-call runs makes scratch and transfer comparisons interpretable.

Wikipedia provides prose; the smaller Q&A share exposes the model to user
questions and procedural answers. Capping preparation can get a run started
without encoding the whole corpus, but only the frozen prepared subset is
available to that run. A 350-token window cannot preserve a long document's
full context: consecutive windows keep the text, not the attention history.
