from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        received = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        yield {'received': received.isoformat(timespec='minutes'), 'allowance': str(rng.randrange(1, 2881))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(received, allowance):
    deadline = datetime.fromisoformat(received) + timedelta(minutes=int(allowance))
    return f'Response deadline: {deadline.isoformat(timespec="minutes")}.'


SCHEMA = Schema(
    id='support_response_deadline_from_allowance',
    tool_names=('calculate_response_deadline', 'add_response_allowance', 'compute_response_deadline', 'find_response_deadline', 'derive_response_deadline', 'determine_response_deadline', 'get_response_deadline', 'calculate_ticket_response_deadline', 'compute_allowance_deadline', 'add_minutes_for_response'),
    descriptions=('Add the allowance in elapsed minutes to the received timestamp.', 'Calculate a response deadline from a timestamp and minute allowance.', 'Compute the response deadline by adding elapsed minutes.', 'Find the deadline from the received time and minute allowance.', 'Derive the response deadline from the supplied timestamp and allowance.', 'Determine when a response is due by adding the allowance.', 'Get the response deadline after the specified elapsed minutes.', 'Calculate the ticket response deadline in the timestamp timezone.', 'Add the minute allowance to the receipt time.', 'Compute the response due time from receipt and allowance.'),
    parameters=(Parameter(names=('received', 'received_at')), Parameter(names=('allowance', 'allowance_minutes'))),
    tasks=(Task(id='deadline', prompts=('A ticket arrived at {received}. The response allowance is {allowance} elapsed minutes. What is the deadline in the same timezone?', 'Add {allowance} elapsed minutes to the received timestamp {received} to find the response deadline in that timezone.', 'Calculate the response deadline in the same timezone for a ticket received at {received} with {allowance} elapsed minutes allowed.', 'A ticket arrives at {received}; it has {allowance} elapsed minutes for a response. Give the deadline in the received timestamp’s timezone.', 'What timestamp is {allowance} elapsed minutes after {received}? This is the ticket response deadline; retain the timezone.', 'Find the response deadline in the same timezone: received {received}, allowance {allowance} elapsed minutes.', 'For a ticket received at {received}, when is the deadline after {allowance} elapsed minutes? Use the same timezone.', 'The response window is {allowance} elapsed minutes starting at {received}. Calculate its deadline in that timezone.', 'Determine the deadline for responding to a ticket received {received} with an allowance of {allowance} elapsed minutes, in the same timezone.', 'Add the {allowance}-elapsed-minute response allowance to {received} and report the deadline in the same timezone.', 'At {received} a ticket arrives. When does its {allowance} elapsed-minute response allowance end, in that timezone?', 'Using the received time {received} and allowance {allowance} elapsed minutes, return the response deadline in the same timezone.'), answers=('{result}', '{result}'), cases=cases),),
)
