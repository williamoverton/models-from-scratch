from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        start = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        end = start + timedelta(minutes=rng.randrange(1, 24 * 60 + 1))
        yield {'start': start.isoformat(timespec='minutes'), 'end': end.isoformat(timespec='minutes')}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(start, end):
    minutes = int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds() // 60)
    return f'Duration: {minutes} minutes.'


SCHEMA = Schema(
    id='schedule_duration_between_times',
    tool_names=('calculate_appointment_duration', 'elapsed_minutes', 'compute_elapsed_minutes', 'find_duration_between_timestamps', 'get_appointment_length', 'calculate_timestamp_difference', 'measure_visit_duration', 'compute_appointment_minutes', 'find_elapsed_duration', 'duration_in_minutes'),
    descriptions=('Calculate elapsed minutes between start and end.', 'Find the duration between two timestamps.', 'Compute the number of minutes from a start timestamp to an end timestamp.', 'Determine an appointment length in minutes from its timestamps.', 'Calculate elapsed whole minutes between same-timezone datetimes.', 'Find the minute difference between an appointment start and end.', 'Return the duration in minutes between the supplied date and time values.', 'Measure elapsed time in minutes from the start to the end.', 'Compute a visit duration using its start and end timestamps.', 'Work out how many minutes separate two same-timezone timestamps.'),
    parameters=(Parameter(names=('start', 'start_time')), Parameter(names=('end', 'end_time'))),
    tasks=(Task(id='duration', prompts=('An appointment starts at {start} and ends at {end}, in the same timezone. How many minutes long is it?', 'Calculate the duration in minutes from {start} to {end}; both timestamps use the same timezone.', 'How many minutes elapse between {start} and {end}, in the same timezone?', 'Find the appointment length in minutes, starting {start} and ending {end}; the timezone is shared.', 'Compute elapsed minutes from {start} through {end}, using the same timezone for both.', 'For timestamps {start} and {end} in one timezone, report the duration in minutes.', 'What is the minute difference between {start} and {end}? Both are in the same timezone.', 'Measure the visit from {start} to {end} in minutes; timestamps share a timezone.', 'Determine how many minutes the interval {start} to {end} lasts in the same timezone.', 'The start is {start} and the end is {end}, both in one timezone. Calculate elapsed minutes.', 'Give the duration in minutes for {start} until {end}, with no timezone difference.', 'Calculate the minutes between the same-timezone start {start} and end {end}.'), answers=('{result}', '{result}'), cases=cases),),
)
