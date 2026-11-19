from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        departure = rng.randrange(0, 24 * 60, 5)
        yield {"departure": f"{departure // 60:02d}:{departure % 60:02d}", "duration": str(rng.randrange(5, 361, 5))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="travel_arrival_estimate",
    tool_names=('estimate_arrival', 'calculate_arrival_time', 'compute_arrival_time', 'find_arrival_time', 'determine_arrival_clock', 'add_trip_duration', 'estimate_trip_arrival', 'calculate_trip_arrival', 'derive_arrival_time', 'compute_trip_arrival'),
    descriptions=('Add minutes to a departure clock time and indicate same or next day.', 'Calculate the arrival clock time and day from a departure and duration.', 'Determine when a trip arrives given its departure and duration in minutes.', 'Compute arrival time, marking a next-day arrival when applicable.', 'Find the arrival clock time after a specified number of minutes.', 'Add a trip duration in minutes to the departure time.', 'Estimate trip arrival and whether it falls on the next day.', 'Return the arrival time and same-day or next-day status.', 'Calculate a trip arrival from a clock departure and minute duration.', 'Derive the arrival clock and day relative to departure.'),
    parameters=(Parameter(names=("departure", "departure_time")), Parameter(names=("duration", "duration_minutes"))),
    tasks=(Task(id="arrival", prompts=("A trip leaves at {departure} and takes {duration} minutes. When does it arrive? Say if it is the next day.", "Calculate the arrival time for a {duration}-minute trip departing at {departure}, including whether it arrives the same or next day.", 'Depart at {departure} for {duration} minutes. Give the arrival clock time and whether it is the same or next day.', 'What clock time and relative day result from leaving at {departure} and traveling {duration} minutes?', 'Add {duration} minutes to {departure} and report the arrival time with same-day or next-day status.', 'Find when a trip departing {departure} arrives after {duration} minutes; specify same or next day.', 'A {duration}-minute journey starts at {departure}. Provide its arrival time and day relative to departure.', 'Calculate the clock arrival for departure {departure} and duration {duration} minutes, indicating whether the day changes.', 'For a departure at {departure}, determine the arrival after {duration} minutes and label it same day or next day.', 'How late does a {duration}-minute trip departing at {departure} arrive? Include whether arrival is next day.', 'Report the arrival clock and same/next-day label for {departure} plus {duration} minutes.', 'Starting at {departure}, travel lasts {duration} minutes. Calculate the arrival clock and whether it falls on the next day.'), answers=("Arrival is {result}.", "The trip arrives at {result}."), cases=cases),),
)


def resolve(departure, duration):
    hours, minutes = map(int, departure.split(":"))
    total = hours * 60 + minutes + int(duration)
    day = "next day" if total >= 1440 else "same day"
    total %= 1440
    return f"{total // 60:02d}:{total % 60:02d} ({day})"
