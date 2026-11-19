from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        base = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(300 * 24 * 60))
        ids = rng.sample(range(100, 1000), 3)
        ages = sorted(rng.sample(range(1, 1000), 3))
        entries = [(ids[0], 'delivered', base - timedelta(minutes=ages[2])), (ids[1], 'failed', base - timedelta(minutes=ages[1])), (ids[2], 'failed', base - timedelta(minutes=ages[0]))]
        rng.shuffle(entries)
        yield {'webhooks': '; '.join(f'W-{ident} {status} {created.isoformat(timespec="minutes")}' for ident, status, created in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['webhooks'].split('; ')]
    webhook, _, _ = min((entry for entry in entries if entry[1] == 'failed'), key=lambda entry: datetime.fromisoformat(entry[2]))
    return Decision(fields=case, arguments={'webhook': webhook})


def resolve(webhook):
    return f'Inspected webhook {webhook}'


SCHEMA = Schema(
    id='api_inspect_oldest_failed_webhook',
    tool_names=('inspect_webhook', 'inspect_webhook_delivery', 'review_webhook_by_id', 'simulate_webhook_inspection', 'inspect_selected_webhook', 'examine_webhook_delivery', 'request_webhook_inspection', 'inspect_delivery_by_id', 'review_selected_webhook', 'simulate_delivery_inspection'),
    descriptions=('Simulate inspection of a webhook ID.', 'Inspect the supplied webhook in the simulation.', 'Simulate inspecting the specified webhook delivery.', 'Return an inspection confirmation for the given webhook ID.', 'Inspect the selected webhook by its identifier in the simulation.', 'Request simulated inspection of one webhook.', 'Review the webhook identified by the supplied ID in the simulation.', 'Produce a simulated webhook inspection result.', 'Examine the specified delivery ID in the sample workflow.', 'Simulate a review of the selected webhook identifier.'),
    parameters=(Parameter(names=('webhook', 'webhook_id')),),
    tasks=(Task(id='inspect', prompts=('Inspect the oldest failed webhook by creation time: {webhooks}. Entries are ID, status, timestamp in the same timezone.', 'From {webhooks}, inspect the failed webhook with the earliest creation time. Each entry is ID, status, timestamp; timestamps share a timezone.', 'For a simulated inspection, select the earliest-created failed delivery from {webhooks}; each entry lists ID, status and creation timestamp in the same timezone.', 'These webhook entries contain ID, status and creation time, all times in one timezone: {webhooks}. Inspect the oldest one whose status is failed.', 'Ignore successful deliveries in {webhooks} and inspect the failed webhook created first. The entries are ID, status, timestamp, with a common timezone.', 'Which failed delivery was created earliest? Inspect it using {webhooks}, where each record gives ID, status and creation timestamp in the same timezone.', 'Arrange the failed entries in {webhooks} by creation time and simulate inspection of the earliest. Fields are ID, status and timestamp; all timestamps share a timezone.', 'A webhook inspection is needed for the oldest failure, not the oldest delivery overall. Use {webhooks}, formatted ID, status, creation timestamp with a shared timezone.', 'Among the ID/status/creation-time entries {webhooks}, inspect the first-created webhook marked failed. The timestamps are in the same timezone.', 'Using {webhooks}, find the minimum creation timestamp among failed webhooks and inspect that ID. Each entry is ID, status, timestamp in a common timezone.', 'Review the earliest failure by creation timestamp in {webhooks}. Entries list webhook ID, status and timestamp, and all timestamps use the same timezone; simulate inspecting it.', 'From the failed deliveries in {webhooks}, choose the one created longest ago and request its inspection. Each entry gives ID, status and creation timestamp in the same timezone.'), answers=('{result}.', '{result}.'), cases=cases),),
)
