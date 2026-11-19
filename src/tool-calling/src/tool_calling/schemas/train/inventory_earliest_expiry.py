from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(1000, 9999), 3)
        days = rng.sample(range(730), 3)
        rows = [f"L-{lot}|{date(2026, 1, 1) + timedelta(days=day)}" for lot, day in zip(ids, days)]
        rng.shuffle(rows)
        yield {"lots": "; ".join(rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("|") for row in case["lots"].split(";")]
    lot = min((expiry, lot) for lot, expiry in rows)[1]
    return Decision(fields=case, arguments={"lot": lot})


def resolve(lot):
    return f"Flagged lot {lot}"


SCHEMA = Schema(
    id="inventory_earliest_expiring_lot",
    tool_names=("flag_expiring_lot", "flag_inventory_lot", "mark_inventory_lot", "flag_lot_by_id", "mark_lot", "tag_inventory_lot", "flag_selected_lot", "mark_selected_lot", "record_lot_flag", "set_lot_flag"),
    descriptions=("Flag the supplied lot ID.", "Flag an inventory lot by ID.", "Mark the specified inventory lot.", "Flag the selected lot using its ID.", "Apply a flag to the given lot identifier.", "Record a flag for the supplied inventory lot.", "Mark a lot identified by its ID.", "Set a flag on the selected lot.", "Flag an inventory lot specified by identifier.", "Mark the supplied lot for attention."),
    parameters=(Parameter(names=("lot", "lot_id")),),
    tasks=(Task(id="expiry", prompts=("Flag the lot with the earliest expiry date. Entries are lot ID|expiry date: {lots}.", "From {lots}, flag the lot that expires first; entries are lot ID|expiry date.", "Lots are listed as lot ID|expiry date: {lots}. Flag the one with the earliest expiry.", "Which lot expires soonest? Flag it using these lot ID|expiry date entries: {lots}.", "Identify and flag the first-expiring lot in {lots}; each entry is lot ID|expiry date.", "Given {lots} in lot ID|expiry date format, flag the lot whose expiry date comes first.", "Compare the expiry dates in {lots} and flag the earliest lot. The format is lot ID|expiry date.", "Flag the lot associated with the minimum expiry date in {lots}, where entries are lot ID|expiry date.", "Among these lot ID|expiry date records, flag the earliest expiring lot: {lots}.", "Use the lot ID|expiry date list {lots} to find and flag the lot expiring first.", "The inventory lots and expiry dates are {lots}, formatted lot ID|expiry date. Flag the soonest-expiring one.", "From the records {lots} (lot ID|expiry date), flag the lot with the earliest date."), answers=("{result}.", "{result}."), cases=cases),),
)
