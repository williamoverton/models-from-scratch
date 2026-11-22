# Tool calling: filter citations from fetched Wikipedia windows

Strip complete numeric bracket markers from Wikipedia training windows before
computing next-token loss. Do it at batch load rather than rebuilding the packed
bundle, so the existing run can keep its checkpoint, optimizer, and data cursor.
Keep Q&A and held-out validation unchanged so existing validation losses remain
comparable. Ignore padding targets and keep the schedule based on the original
window size.

The packed text no longer distinguishes citation markup from literal numeric
brackets, and markers cut across window boundaries can survive. A future clean
bundle can remove citations structurally before packing instead.
