from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(("A101", "A102", "A103", "A104", "A105", "A106"), 3)
        limit = rng.randint(40, 80)
        values = [rng.randint(1, limit) for _ in ids]
        values[rng.randrange(3)] = limit + rng.randint(1, 20)
        rows = list(zip(ids, values))
        yield {"rows": rows, "limit": str(limit), "readings": "; ".join(f"{alert}: {value}" for alert, value in rows)}


def prepare(*, task_id, case):
    alert = next(alert for alert, value in case["rows"] if value > int(case["limit"]))
    return Decision(fields=case, arguments={"alert": alert})


def resolve(alert):
    return f"Acknowledged alert: {alert}."


SCHEMA = Schema(
    id="observability_acknowledge_alert",
    tool_names=("acknowledge_metric_alert", "ack_alert", "acknowledge_alert_by_id", "record_alert_acknowledgment", "mark_alert_acknowledged", "confirm_alert_acknowledgment", "register_alert_acknowledgment", "acknowledge_selected_alert", "submit_alert_acknowledgment", "acknowledge_specified_alert"),
    descriptions=("Acknowledge an alert by ID.", "Record acknowledgment of the specified alert.", "Mark the selected alert ID as acknowledged.", "Register acknowledgment for the given alert.", "Submit acknowledgment of the specified alert ID.", "Record that the identified alert has been acknowledged.", "Acknowledge the selected alert using its ID.", "Mark the given alert as acknowledged.", "Register an acknowledgment for the selected alert.", "Confirm acknowledgment of the alert identified by ID."),
    parameters=(Parameter(names=("alert", "alert_id")),),
    tasks=(Task(id="acknowledge", prompts=("Acknowledge the alert whose metric is above {limit}; equality is within the limit. Alerts: {readings}.", "For these alerts, acknowledge the one with a value strictly greater than {limit}: {readings}.", "From {readings}, acknowledge the alert exceeding {limit}; a value equal to the limit does not exceed it.", "Please acknowledge the alert with a metric strictly above {limit}. Readings: {readings}.", "Which alert exceeds {limit}? Acknowledge it, treating equality as within the limit: {readings}.", "Look at {readings} and acknowledge the alert whose value is greater than {limit}, not equal to it.", "The threshold is {limit}. Acknowledge the alert above it, excluding equality: {readings}.", "Find and acknowledge the alert whose reading exceeds {limit}; equal values are within bounds. Alerts: {readings}.", "For {readings}, acknowledge the alert with a reading strictly over {limit}.", "Acknowledge the alert over the {limit} limit in these readings: {readings}. A reading at the limit is not over it.", "Among {readings}, select and acknowledge the alert where the metric is greater than {limit}, excluding equality.", "These alerts have readings {readings}; acknowledge the one above {limit}, not one equal to it."), answers=("{result}", "{result}"), cases=cases),),
)
