from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        arrival = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        minimum = rng.randint(15, 90)
        ids = rng.sample(range(100, 999), 3)
        intervals = [rng.randrange(minimum), minimum, minimum + rng.randint(1, 120)]
        rng.shuffle(intervals)
        entries = list(zip(ids, intervals))
        rng.shuffle(entries)
        yield {"arrival": arrival.isoformat(timespec="minutes"), "minimum": str(minimum), "connections": "; ".join(f"C-{connection}={(arrival + timedelta(minutes=interval)).isoformat(timespec='minutes')}" for connection, interval in entries)}


def prepare(*, task_id, case):
    arrival = datetime.fromisoformat(case["arrival"])
    minimum = timedelta(minutes=int(case["minimum"]))
    entries = [entry.strip().split("=") for entry in case["connections"].split(";")]
    connection = next(identifier for identifier, departure in entries if datetime.fromisoformat(departure) - arrival < minimum)
    return Decision(fields=case, arguments={"connection": connection})


def resolve(connection):
    return f"Flagged connection: {connection}"


SCHEMA = Schema(
    id="travel_missed_connection_flag",
    tool_names=('flag_connection', 'mark_connection_for_review', 'flag_connection_for_review', 'report_flagged_connection', 'report_connection_review', 'show_connection_review', 'flag_selected_connection', 'return_flagged_connection', 'show_connection_id', 'flag_connection_id'),
    descriptions=('Flag the specified connection for review.', 'Mark a connection identifier for review.', 'Report the given connection as flagged.', 'Return a review flag for the supplied connection.', 'Flag a connection by its identifier.', 'Mark the selected connection for review.', 'Identify the supplied connection as flagged for review.', 'Report the specified connection as needing review.', 'Report a review flag for a connection identifier.', 'Flag the provided connection identifier.'),
    parameters=(Parameter(names=("connection", "connection_id")),),
    tasks=(Task(id="flag", prompts=("Arrival is {arrival}. Flag the connection that cannot be made with a minimum transfer interval of {minimum} minutes. Departures are ID=time: {connections}. All times share a timezone; exactly the minimum is sufficient.", "From departures {connections} (ID=time), flag the one missed after arrival at {arrival}: at least {minimum} minutes must elapse before departure. All times use the same timezone.", 'Arrival: {arrival}; minimum transfer: {minimum} minutes. Flag the unmakeable connection among ID=time departures {connections}; all times share a timezone and equality is sufficient.', 'Among {connections} (ID=time), flag the connection departing less than {minimum} minutes after {arrival}; all timestamps share a timezone.', 'Which connection in {connections} (ID=time) misses the {minimum}-minute minimum after {arrival}? Flag it; times use one timezone and exactly the minimum works.', 'Review departures {connections}, formatted ID=time. After arriving at {arrival}, flag the one with under {minimum} minutes to transfer; timezone is common.', 'Flag the connection with insufficient transfer time: arrival {arrival}, departures ID=time {connections}, minimum {minimum} minutes inclusive; all times are in the same timezone.', 'Using same-timezone times, flag the departure ID from {connections} (ID=time) whose interval after {arrival} is shorter than {minimum} minutes.', 'At {arrival} the traveler arrives. From {connections} (ID=time), flag the connection leaving before {minimum} minutes have elapsed; all times share a timezone.', 'The transfer minimum is {minimum} minutes, including equality. Flag the missed connection from {connections} (ID=time) after arrival {arrival}; timestamps share a timezone.', 'For arrival {arrival}, which ID in {connections} (ID=time) has a transfer shorter than {minimum} minutes? Flag it; all times use the same timezone.', 'Identify and flag the connection not meeting a {minimum}-minute transfer from {arrival}, using the same-timezone ID=time departures {connections}; equality meets the requirement.'), answers=("{result}.", "Review recorded for {result}."), cases=cases),),
)
