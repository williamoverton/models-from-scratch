from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        start = rng.randrange(6 * 60, 21 * 60, 5)
        duration = rng.randrange(1, min(180, 23 * 60 + 59 - start) // 5 + 1) * 5
        yield {"duration": str(duration), "start": f"{start // 60:02d}:{start % 60:02d}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="appointment_end",
    tool_names=("appointment_end", "finish_time", "calculate_appointment_end", "compute_visit_end", "add_appointment_minutes", "find_end_time", "get_appointment_finish", "derive_visit_end_time", "calculate_finish_time", "appointment_end_time"),
    descriptions=("Calculate the end time of a same-day appointment from its start and duration in minutes.", "Add minutes to an appointment start time.", "Find when a same-day appointment ends given its start and length in minutes.", "Compute the finish time from a start time and minute duration.", "Determine an appointment's end by adding its duration to its start.", "Return the same-day end time for a timed appointment.", "Work out a visit's finishing time using its starting time and duration.", "Calculate a clock end time from appointment start and elapsed minutes.", "Add a minute duration to a same-day appointment's start.", "Find the finishing clock time of an appointment."),
    parameters=(
        Parameter(names=("duration", "minutes")),
        Parameter(names=("start", "start_time")),
    ),
    tasks=(Task(id="end", prompts=("An appointment starts at {start} and lasts {duration} minutes. When does it end?", "Find the end time for {start} plus {duration} minutes.", "What time does a {duration}-minute appointment beginning at {start} finish?", "Add {duration} minutes to {start} to find the appointment end.", "Calculate the finish time of a visit starting at {start} with duration {duration} minutes.", "A visit begins at {start} for {duration} minutes; when is it over?", "Determine the end clock time for {start} and a length of {duration} minutes.", "Starting at {start}, when will an appointment lasting {duration} minutes end?", "Work out the finishing time after {duration} minutes from {start}.", "Give the end time of an appointment that starts at {start} and runs {duration} minutes.", "How late does a {duration}-minute visit starting at {start} go?", "Compute the appointment end by adding {duration} minutes to {start}."), answers=("It ends at {result}.", "The end time is {result}."), cases=cases),),
)


def resolve(duration, start):
    hours, minutes = map(int, start.split(":"))
    total = hours * 60 + minutes + int(duration)
    return f"{total // 60:02d}:{total % 60:02d}"
