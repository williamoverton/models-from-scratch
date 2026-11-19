from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        departure = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        arrival = departure + timedelta(minutes=rng.randint(1, 3000))
        yield {"departure": departure.isoformat(timespec="minutes"), "arrival": arrival.isoformat(timespec="minutes")}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(departure, arrival):
    duration = datetime.fromisoformat(arrival) - datetime.fromisoformat(departure)
    minutes = int(duration.total_seconds() // 60)
    return f"{minutes} minutes"


SCHEMA = Schema(
    id="travel_trip_duration_minutes",
    tool_names=('calculate_trip_duration', 'measure_journey_time', 'compute_trip_minutes', 'calculate_elapsed_minutes', 'get_journey_duration', 'determine_trip_duration', 'find_elapsed_trip_time', 'compute_journey_minutes', 'derive_trip_duration', 'measure_trip_minutes'),
    descriptions=('Calculate elapsed minutes between same-timezone departure and arrival.', 'Return journey duration in minutes from two same-timezone timestamps.', 'Compute the minutes elapsed from departure to arrival.', 'Determine trip length in minutes using same-timezone timestamps.', 'Find elapsed journey time in minutes.', 'Calculate duration between departure and arrival timestamps in minutes.', 'Measure the interval from trip departure to arrival in minutes.', 'Derive the trip duration from two same-timezone timestamps.', 'Return the elapsed minutes for a journey.', 'Compute trip duration in minutes from departure and arrival.'),
    parameters=(Parameter(names=("departure", "departure_time")), Parameter(names=("arrival", "arrival_time"))),
    tasks=(Task(id="duration", prompts=("A trip departs at {departure} and arrives at {arrival}, both in the same timezone. What is its duration in minutes?", "Calculate elapsed minutes from {departure} to {arrival}; both timestamps use the same timezone.", 'How many minutes elapse between departure {departure} and arrival {arrival}? Both use the same timezone.', 'With departure at {departure} and arrival at {arrival} in one timezone, calculate the journey duration in minutes.', 'Find the elapsed trip minutes: departure {departure}, arrival {arrival}; timestamps share a timezone.', 'The same-timezone timestamps are {departure} for departure and {arrival} for arrival. Compute duration in minutes.', 'Measure the journey in minutes from {departure} to {arrival}; the timestamps are in the same timezone.', 'A journey runs from {departure} to {arrival}, both in the same timezone. Determine its length in minutes.', 'Calculate how many minutes the trip takes when it leaves {departure} and arrives {arrival}, with a common timezone.', 'Given same-timezone departure {departure} and arrival {arrival}, report elapsed minutes.', 'What is the minute interval from {departure} departure to {arrival} arrival? Both times share a timezone.', 'Work out trip duration in minutes using departure {departure} and arrival {arrival}, in the same timezone.'), answers=("The trip lasts {result}.", "Duration: {result}."), cases=cases),),
)
