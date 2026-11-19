from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        today = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 999), 3)
        offsets = [rng.randint(-90, -1), 0, rng.randint(1, 90)]
        rng.shuffle(offsets)
        yield {"today": today.isoformat(), "records": "; ".join(f"R-{record}={(today + timedelta(days=offset)).isoformat()}" for record, offset in zip(ids, offsets))}


def prepare(*, task_id, case):
    today = date.fromisoformat(case["today"])
    entries = [entry.strip().split("=") for entry in case["records"].split(";")]
    record = next(record for record, retention_date in entries if date.fromisoformat(retention_date) < today)
    return Decision(fields=case, arguments={"record": record})


def resolve(record):
    return f"Record {record} flagged for disposal review"


SCHEMA = Schema(
    id="archive_retention_disposal",
    tool_names=("flag_record_for_disposal_review", "mark_retention_review", "request_record_disposal_review", "flag_archive_record_review", "mark_record_for_disposal_review", "submit_retention_review_flag", "flag_retained_record", "request_archive_disposal_review", "mark_archive_record_for_review", "flag_record_retention_review"),
    descriptions=("Flag the supplied record ID for disposal review, without disposing it.", "Mark a record for retention disposal review.", "Flag the identified archive record for review, not disposal.", "Request disposal review for the supplied record ID without deleting it.", "Mark one record for review of its retention disposal status.", "Submit a disposal-review flag for the identified record.", "Flag a record for a later disposal decision without disposing it.", "Identify a record for archive disposal review only.", "Record a review flag against the specified record ID.", "Mark the selected record for disposal review rather than disposal."),
    parameters=(Parameter(names=("record", "record_id")),),
    tasks=(Task(id="review", prompts=(
        'Today is {today}. Flag for disposal review the one record whose retention date is strictly before today; equality is not past. Entries are ID=retention date: {records}.',
        'From {records} (record ID=retention date), flag for disposal review the record past its retention date as of {today}. A date equal to today is not past.',
        'Review the ID=retention date entries {records} against {today}. Flag the record dated strictly earlier for disposal review; a date on today does not qualify.',
        'Which archive record needs a disposal-review flag? On {today}, inspect {records} (ID=retention date) and select only a date before today, not equal to it.',
        'The archive lists {records}, each as ID=retention date. As of {today}, flag for disposal review the one whose date has passed strictly before today; equality is not past.',
        'Please flag the qualifying record for disposal review, not disposal. Today is {today}; {records} maps IDs to retention dates, and only dates earlier than today qualify.',
        'Using {today} as the current date, find the record in {records} (ID=retention date) with a strictly earlier retention date and flag it for disposal review. Today itself is excluded.',
        'One retention date in {records} precedes {today}. Treat entries as ID=retention date and flag that record for disposal review; a date equal to today is not past.',
        'Flag for disposal review, without disposing, the record whose retention date is before {today}. The ID=retention date list is {records}; equality with today does not count.',
        'From the archive entries {records} (ID=retention date), select the date strictly less than {today} and flag its record for disposal review rather than disposal.',
        'As of {today}, which record in {records} has passed its retention date? Entries are ID=retention date; equality is not past. Flag the selected record for disposal review.',
        'Check {records}, where each ID is paired with a retention date, against today ({today}). Only an earlier date qualifies; flag its record for disposal review.',
    ), answers=("{result}.", "{result}."), cases=cases),),
)
