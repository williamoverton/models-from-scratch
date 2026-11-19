from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(("E101", "E102", "E103", "E104", "E105", "E106"), 3)
        minutes = rng.sample(range(60), 3)
        rows = list(zip(ids, minutes))
        yield {"rows": rows, "events": "; ".join(f"{event} at 14:{minute:02d} UTC" for event, minute in rows)}


def prepare(*, task_id, case):
    event = max(case["rows"], key=lambda row: row[1])[0]
    return Decision(fields=case, arguments={"event": event})


def resolve(event):
    return f"Inspected event: {event}."


SCHEMA = Schema(
    id="observability_latest_error",
    tool_names=("inspect_error_event", "open_error_event", "inspect_event_by_id", "open_error_by_id", "inspect_selected_error", "open_selected_error_event", "record_error_event_inspection", "view_error_event", "inspect_specified_error_event", "open_event_by_id"),
    descriptions=("Inspect an error event by ID.", "Open the specified error event.", "Inspect the selected error event using its ID.", "Open the error event identified by the given ID.", "Record inspection of the specified error event.", "View the selected error event by ID.", "Open the selected error for inspection.", "Inspect the error associated with the provided event ID.", "Record the specified event as inspected.", "Open the given error event using its ID."),
    parameters=(Parameter(names=("event", "event_id")),),
    tasks=(Task(id="latest", prompts=("Inspect the latest error event. All times are on the same day: {events}.", "Open the most recent error by time, all on the same day: {events}.", "These errors all occurred on the same day: {events}. Inspect the one with the latest timestamp.", "Which error happened most recently? Open its event; all timestamps are from the same day: {events}.", "Please inspect the last error chronologically, assuming the same date for each: {events}.", "From {events}, open the newest error event. Every time is on the same day.", "Find and inspect the error with the latest time among these same-day events: {events}.", "Could you open the most recent event? The times all refer to one day: {events}.", "On the same day we recorded {events}. Inspect the error that occurred last.", "Review the latest of these errors, whose times are all from the same day: {events}.", "Select the error with the greatest timestamp and open it; each timestamp is on the same day: {events}.", "Inspect whichever error occurred most recently in this same-day list: {events}."), answers=("{result}", "{result}"), cases=cases),),
)
