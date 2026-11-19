# Run tool-calling training until stopped

Tool Calling uses the dashboard's existing [unlimited training and cooperative
stop contract](2026-11-11-cooperative-training-stop.md). Remove the CLI step
ceiling and show completed steps without a total. Start resumes a compatible
checkpoint when present; Stop and Quit save the latest completed update.

A fixed budget helps repeatable comparisons, but interactive training does not
need one. This changes the [initial port's](2026-11-19-tool-calling-data-and-previews.md)
final-step preview: there is no scheduled final update. The first-update and
500-step previews and periodic checkpoints remain. The ceiling was already
excluded from checkpoint settings, so this does not change checkpoint format.
