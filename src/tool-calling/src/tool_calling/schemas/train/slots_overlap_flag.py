from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        base = datetime(2026, 1, 1, 9) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 1000), 3)
        intervals = [(base + timedelta(minutes=start), base + timedelta(minutes=end)) for start, end in ((0, 30), (20, 50), (60, 90))]
        target_start = base + timedelta(minutes=5)
        target_end = base + timedelta(minutes=20)
        # Only the first interval overlaps: the second begins exactly at the target's end.
        entries = list(zip(ids, intervals))
        rng.shuffle(entries)
        yield {'target': f'{target_start.isoformat(timespec="minutes")} to {target_end.isoformat(timespec="minutes")}', 'appointments': '; '.join(f'A-{ident}={start.isoformat(timespec="minutes")} to {end.isoformat(timespec="minutes")}' for ident, (start, end) in entries)}


def prepare(*, task_id, case):
    target_start, target_end = (datetime.fromisoformat(value) for value in case['target'].split(' to '))
    for entry in case['appointments'].split('; '):
        ident, interval = entry.split('=')
        start, end = (datetime.fromisoformat(value) for value in interval.split(' to '))
        if start < target_end and target_start < end:
            return Decision(fields=case, arguments={'appointment': ident})
    raise ValueError('No overlapping appointment')


def resolve(appointment):
    return f'Flagged appointment: {appointment}'


SCHEMA = Schema(
    id='schedule_appointment_overlap_flag',
    tool_names=('flag_appointment', 'mark_appointment', 'flag_appointment_by_id', 'record_flagged_appointment', 'mark_selected_appointment', 'acknowledge_appointment_flag', 'report_flagged_appointment', 'submit_appointment_flag', 'identify_flagged_appointment', 'flag_selected_appointment'),
    descriptions=('Flag the supplied appointment ID.', 'Mark an appointment by ID.', 'Acknowledge the appointment identifier supplied for flagging.', 'Return the supplied appointment ID as flagged.', 'Record a flag against the specified appointment identifier.', 'Report the appointment selected for flagging by ID.', 'Mark the provided appointment identifier.', 'Identify the supplied appointment as the flagged one.', 'Acknowledge a flag for the chosen appointment ID.', 'Return an acknowledgement of the specified appointment flag.'),
    parameters=(Parameter(names=('appointment', 'appointment_id')),),
    tasks=(Task(id='overlap', prompts=('Flag the appointment overlapping {target} from {appointments}. Intervals are start-inclusive and end-exclusive; touching endpoints do not overlap. All times share a timezone.', 'For the interval {target}, flag the overlapping appointment: {appointments}. All times are in the same timezone and an endpoint touching another is not an overlap.', 'From {appointments}, flag the interval overlapping {target}; times share a timezone and touching endpoints do not overlap.', 'Identify and flag the appointment in {appointments} that overlaps {target}. Use one timezone and half-open intervals.', 'Compare {target} against {appointments} and flag the overlap; all times share a timezone, and touching endpoints are excluded.', 'Which appointment in {appointments} overlaps {target}? Flag it using same-timezone, start-inclusive end-exclusive intervals.', 'Flag the overlapping entry in {appointments} for {target}; same timezone, no overlap at merely touching endpoints.', 'Using half-open intervals in the same timezone, flag the appointment overlapping {target} among {appointments}.', 'For {target}, find and flag the overlap in {appointments}; endpoint contact alone is not overlap and times share a timezone.', 'Consider {appointments} against {target}. Flag the overlapping appointment, with shared timezone and exclusive ends.', 'Flag the appointment sharing actual time with {target}: {appointments}. All times use one timezone; touching endpoints do not overlap.', 'Select and flag the overlapping appointment from {appointments} for {target}, treating all intervals as half-open and same-timezone.'), answers=('{result}.', '{result}.'), cases=cases),),
)
