from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        local = datetime(2026, 1, 1) + timedelta(minutes=30 * rng.randrange(365 * 48))
        source, destination = rng.sample((-12, -8, -5, -3, 0, 1, 3, 5, 8, 10, 12, 14), 2)
        yield {'local': local.isoformat(timespec='minutes'), 'source_offset': str(source), 'destination_offset': str(destination)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(local, source_offset, destination_offset):
    converted = datetime.fromisoformat(local) + timedelta(hours=int(destination_offset) - int(source_offset))
    return f'Destination local time: {converted.isoformat(timespec="minutes")}.'


SCHEMA = Schema(
    id='schedule_convert_explicit_utc_offsets',
    tool_names=('convert_offset_time', 'translate_local_time', 'convert_fixed_offset_timestamp', 'shift_between_utc_offsets', 'calculate_destination_local_time', 'translate_fixed_offset_datetime', 'convert_utc_offset_datetime', 'find_local_time_at_offset', 'adjust_timestamp_for_offset', 'convert_local_datetime_offsets'),
    descriptions=('Convert a local timestamp using explicit UTC offsets in hours.', 'Translate between two fixed UTC offsets.', 'Find the destination date and time from a local timestamp and two fixed hourly UTC offsets.', 'Shift a local datetime from one explicit UTC offset to another.', 'Calculate a destination local timestamp using source and destination offsets in hours.', 'Translate a date and time between fixed offsets without daylight-saving rules.', 'Convert a local datetime between specified UTC offsets, preserving date changes.', 'Apply the difference between two fixed UTC offsets to a local timestamp.', 'Determine local date and time at a destination offset from a source offset.', 'Adjust a timestamp using explicit source and destination UTC offsets.'),
    parameters=(Parameter(names=('local', 'local_time')), Parameter(names=('source_offset', 'from_utc_offset')), Parameter(names=('destination_offset', 'to_utc_offset'))),
    tasks=(Task(id='convert', prompts=('Convert {local} from UTC offset {source_offset} hours to UTC offset {destination_offset} hours. Use fixed offsets, not daylight-saving rules; include the date.', 'At fixed UTC offset {source_offset} hours the local timestamp is {local}. What is the local date and time at fixed UTC offset {destination_offset} hours?', 'Translate {local} from fixed UTC{source_offset} hours to fixed UTC{destination_offset} hours, including the date.', 'Find the destination date and time for {local}, shifting from fixed UTC offset {source_offset} hours to {destination_offset} hours.', 'What local date and time corresponds to {local} at UTC offset {source_offset} hours in fixed offset {destination_offset} hours?', 'Convert the local datetime {local} from offset {source_offset} to {destination_offset} hours; offsets are fixed, including across dates.', 'Using fixed hourly offsets, convert {local} from UTC {source_offset} to UTC {destination_offset}, returning date and time.', 'At UTC offset {source_offset} hours it is {local}; give the date and time at fixed UTC offset {destination_offset} hours.', 'Shift {local} from source UTC offset {source_offset} hours to destination UTC offset {destination_offset} hours without daylight-saving rules, preserving date changes.', 'Calculate the destination local datetime for {local} using fixed source offset {source_offset} hours and destination offset {destination_offset} hours.', 'Express {local} at UTC offset {source_offset} hours in UTC offset {destination_offset} hours; use fixed offsets and include the date.', 'Convert the date and time {local} between fixed UTC offsets {source_offset} and {destination_offset} hours, respectively.'), answers=('{result}', '{result}'), cases=cases),),
)
