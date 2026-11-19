from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        start = datetime(2026, 1, 1) + timedelta(minutes=30 * rng.randrange(365 * 48))
        yield {"start": start.strftime("%Y-%m-%d %H:%M"), "minutes": str(rng.choice((30, 45, 60, 90, 120, 180, 360)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(start, minutes):
    end = datetime.strptime(start, "%Y-%m-%d %H:%M") + timedelta(minutes=int(minutes))
    return end.strftime("%Y-%m-%d %H:%M")


SCHEMA = Schema(
    id="lab_incubation_end",
    tool_names=("calculate_incubation_end", "add_incubation_minutes", "compute_incubation_end_time", "find_incubation_end_timestamp", "calculate_incubation_finish", "add_minutes_to_incubation_start", "determine_incubation_end_time", "compute_incubation_finish_time", "find_incubation_completion_time", "calculate_incubation_end_timestamp"),
    descriptions=("Add elapsed minutes to the incubation start timestamp.", "Calculate the end timestamp for an incubation.", "Find the incubation end date and time by adding the duration in minutes to its start.", "Compute the UTC incubation finish time from its start and elapsed minutes.", "Determine when incubation ends by adding the specified minutes to the start timestamp.", "Add the incubation duration in minutes to the UTC start time.", "Calculate the end date and time for a given incubation start and duration.", "Return the timestamp reached after the specified incubation minutes have elapsed.", "Find the UTC completion timestamp for an incubation of the given duration.", "Compute the incubation end timestamp from a start date and time and a minute count."),
    parameters=(Parameter(names=("start", "start_time")), Parameter(names=("minutes", "duration_minutes"))),
    tasks=(Task(id="end", prompts=("Incubation starts at {start} UTC and lasts {minutes} minutes. What is the end time in UTC?", "Add {minutes} elapsed minutes to the incubation start {start} UTC. Give the end date and time in UTC.", "Calculate the UTC end date and time for incubation beginning {start} UTC and lasting {minutes} minutes.", "A {minutes}-minute incubation begins at {start} UTC. When does it finish, in UTC?", "What UTC timestamp is {minutes} elapsed minutes after the incubation begins at {start} UTC?", "From the incubation start of {start} UTC, advance {minutes} minutes and report the end date and time in UTC.", "The incubation starts {start} UTC. Find its UTC finishing date and time after {minutes} minutes.", "Which UTC date and time falls {minutes} minutes after the incubation start at {start} UTC?", "Determine when incubation ends in UTC if it runs for {minutes} minutes starting at {start} UTC.", "Starting at {start} UTC, an incubation runs {minutes} elapsed minutes. State its UTC end timestamp.", "Add the {minutes}-minute incubation duration to {start} UTC and return the resulting date and time in UTC.", "At what UTC date and time does a {minutes}-minute incubation starting {start} UTC end?"), answers=("It ends at {result} UTC.", "End: {result} UTC."), cases=cases),),
)
