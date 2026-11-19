from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        base = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(300 * 24 * 60))
        ids = rng.sample(range(100, 1000), 3)
        ages = sorted(rng.sample(range(1, 1000), 3))
        entries = [(ids[0], 'closed', base - timedelta(minutes=ages[2])), (ids[1], 'open', base - timedelta(minutes=ages[1])), (ids[2], 'open', base - timedelta(minutes=ages[0]))]
        rng.shuffle(entries)
        yield {'tickets': '; '.join(f'T-{ident} {status} {created.isoformat(timespec="minutes")}' for ident, status, created in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['tickets'].split('; ')]
    ticket, _, _ = min((entry for entry in entries if entry[1] == 'open'), key=lambda entry: datetime.fromisoformat(entry[2]))
    return Decision(fields=case, arguments={'ticket': ticket})


def resolve(ticket):
    return f'Flagged ticket: {ticket}'


SCHEMA = Schema(
    id='support_flag_oldest_open_ticket',
    tool_names=('flag_support_ticket', 'mark_support_ticket', 'flag_ticket_by_id', 'mark_ticket_by_id', 'flag_selected_ticket', 'mark_selected_ticket', 'report_flagged_ticket', 'submit_ticket_flag', 'record_flagged_ticket', 'acknowledge_ticket_flag'),
    descriptions=('Flag the supplied ticket ID.', 'Mark a support ticket by ID.', 'Flag the selected support ticket.', 'Mark the supplied ticket identifier.', 'Record the ticket selected for flagging.', 'Report the flagged support ticket.', 'Submit a ticket ID to be flagged.', 'Acknowledge the selected ticket flag.', 'Flag a support ticket by its ID.', 'Mark the selected ticket for attention.'),
    parameters=(Parameter(names=('ticket', 'ticket_id')),),
    tasks=(Task(id='oldest', prompts=('Flag the oldest open ticket by creation time. Entries are ID, status, creation timestamp: {tickets}. All timestamps use the same timezone.', 'From {tickets}, flag the open ticket with the earliest creation timestamp; each entry is ID, status, creation time in the same timezone.', 'Which open ticket was created first? Flag it from {tickets}; entries give ID, status and creation timestamp, all in the same timezone.', 'Flag the earliest-created open ticket in {tickets}. Each entry lists ID, status, creation timestamp; all timestamps share a timezone.', 'Among {tickets}, select and flag the oldest open ticket by creation timestamp. Entries are ID, status, timestamp in the same timezone.', 'Review {tickets} and flag the open ticket with the earliest creation time. Entries contain ID, status and creation timestamp in one timezone.', 'Using the same-timezone entries {tickets} (ID, status, creation timestamp), flag the open ticket created earliest.', 'Find and flag the oldest open ticket in {tickets}, where each entry gives ID, status and creation time and all timestamps share a timezone.', 'Flag the open ticket with the minimum creation timestamp from {tickets}; entries are ID, status, creation timestamp and use the same timezone.', 'The entries {tickets} list ID, status and creation timestamp, all in one timezone. Flag the earliest-created open ticket.', 'Which ticket should be flagged as oldest open? Use creation timestamps in {tickets}, whose entries are ID, status, timestamp in the same timezone.', 'From the ID, status and creation timestamp entries {tickets}, flag the oldest open ticket. All timestamps are in the same timezone.'), answers=('{result}.', '{result}.'), cases=cases),),
)
