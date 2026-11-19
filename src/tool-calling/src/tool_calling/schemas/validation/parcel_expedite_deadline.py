from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        days = rng.sample(range(1, 31), 3)
        entries = [(f"P{number}", (date(2026, 11, 1) + timedelta(days=offset)).isoformat()) for number, offset in zip(ids, days)]
        rng.shuffle(entries)
        yield {"shipments": "; ".join(f"{number}: {deadline}" for number, deadline in entries)}


def prepare(*, task_id, case):
    entries = [item.split(": ") for item in case["shipments"].split("; ")]
    shipment, _ = min(entries, key=lambda item: item[1])
    return Decision(fields=case, arguments={"shipment": shipment})


SCHEMA = Schema(
    id="parcel_expedite_earliest_deadline",
    tool_names=('report_shipment_expedite', 'report_priority_shipment', 'acknowledge_shipment_expedite', 'report_expedite_request', 'confirm_shipment_priority', 'report_shipment_expedite_request', 'report_selected_expedite_shipment', 'confirm_expedite_request', 'acknowledge_expedite_shipment', 'acknowledge_priority_shipment'),
    descriptions=('Acknowledge an expedite request for a shipment.', 'Report an expedite request for a specified shipment.', 'Confirm the supplied shipment ID in an expedite-request message.', 'Return a simulated expedite request for the given shipment.', 'Acknowledge the selected shipment as requested for expedited handling.', 'Report that an expedite was requested for the provided shipment ID.', 'Output an expedite-request confirmation for a selected shipment.', 'Present the supplied shipment ID as the subject of an expedite request.', 'Echo the given shipment in an expedite-request acknowledgment.', 'Return an acknowledgment of an expedite request for the specified shipment.'),
    parameters=(Parameter(names=("shipment", "shipment_id")),),
    tasks=(Task(id="expedite", prompts=("Shipment deadlines are {shipments}. Request an expedite for the shipment with the earliest deadline.", "Prioritize the earliest-due shipment from {shipments} for expedited handling.", 'Request expedited handling for the shipment with the earliest deadline in {shipments}.', 'From {shipments}, find the earliest deadline and request an expedite for that shipment.', 'Which shipment in {shipments} is due first? Request an expedite for it.', 'Compare the deadlines in {shipments} and request an expedite for the earliest shipment.', 'Select the shipment with the soonest deadline from {shipments} and request expedited handling.', 'For {shipments}, request an expedite for the shipment whose deadline comes first.', 'Identify the earliest-due shipment in {shipments} and request its expedite.', 'The shipment deadlines are {shipments}; request expedited handling for the first due.', 'Request an expedite for the earliest deadline among these shipments: {shipments}.', 'Use {shipments} to select the shipment due soonest and request an expedite.'), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(shipment):
    return f"Expedite requested for shipment {shipment}."
