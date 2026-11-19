from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    items = ("oats", "rice", "beans", "flour", "pasta", "lentils", "barley")
    for _ in range(count):
        names = rng.sample(items, 3)
        dates = [date(2027, 1, 1) + timedelta(days=n) for n in rng.sample(range(365), 3)]
        rows = list(zip(names, dates))
        yield {"rows": rows, "options": "; ".join(f"{name}: {expiry.isoformat()}" for name, expiry in rows)}


def prepare(*, task_id, case):
    name, _ = min(case["rows"], key=lambda row: row[1])
    return Decision(fields=case, arguments={"item": name})


def resolve(item):
    return f"Flagged pantry item: {item}."


SCHEMA = Schema(
    id="food_earliest_pantry_expiry",
    tool_names=('report_flagged_pantry_item', 'acknowledge_pantry_item_flag', 'confirm_pantry_item_flag', 'report_pantry_flag', 'identify_flagged_pantry_item', 'return_flagged_pantry_item', 'confirm_flagged_pantry_item', 'acknowledge_flagged_pantry_item', 'report_specified_pantry_flag', 'report_pantry_item_marker'),
    descriptions=('Report the specified pantry item as flagged.', 'Acknowledge the supplied pantry item flag.', 'Return the given pantry item as flagged.', 'Confirm the named pantry item provided for flagging.', 'Report which pantry item was supplied to be flagged.', 'Acknowledge a flag for the named pantry item.', 'Identify the supplied item as the flagged pantry item.', 'Return a confirmation naming the flagged pantry item.', 'Report the provided pantry item in a flag acknowledgment.', 'Confirm the named pantry item as flagged without comparing dates.'),
    parameters=(Parameter(names=("item", "ingredient")),),
    tasks=(Task(id="expiry", prompts=("Flag the pantry item with the earliest expiry date (YYYY-MM-DD): {options}.", "Which pantry item expires first? Flag it from these dates: {options}.", "Compare these pantry expiry dates and flag the earliest item: {options}.", "Flag the item that will expire first among {options}.", "Which item has the earliest expiration date? Flag it: {options}.", "From {options}, identify and flag the pantry item with the first expiry.", "Please flag the pantry item with the oldest listed expiry date: {options}.", "Review {options} and flag the item whose expiry comes soonest.", "Which of these pantry items has the minimum expiry date? Flag it: {options}.", "Find and flag the earliest-expiring pantry item: {options}.", "Use the dates in {options} to flag whichever pantry item expires first.", "Select the first expiry in {options} and flag that pantry item."), answers=("{result}", "Done. {result}"), cases=cases),),
)
