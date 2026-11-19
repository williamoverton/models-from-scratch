from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        today = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(1000, 9999), 3)
        offsets = [rng.randint(-30, -1), 0, rng.randint(1, 30)]
        rng.shuffle(offsets)
        rows = [f"O-{order}|{today + timedelta(days=offset)}" for order, offset in zip(ids, offsets)]
        rng.shuffle(rows)
        yield {"today": str(today), "orders": "; ".join(rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("|") for row in case["orders"].split(";")]
    order = next(order for order, promised in rows if date.fromisoformat(promised) < date.fromisoformat(case["today"]))
    return Decision(fields=case, arguments={"order": order})


def resolve(order):
    return f"Flagged order {order}"


SCHEMA = Schema(
    id="orders_late_promised_date",
    tool_names=("flag_late", "flag_late_order", "flag_order_by_id", "flag_selected_order", "mark_order_flagged", "flag_supplied_order", "report_flagged_order", "flag_order_identifier", "mark_selected_order", "flag_chosen_order"),
    descriptions=("Flag the supplied order ID.", "Flag an order identified by ID.", "Report the given order as flagged.", "Flag the selected order using its ID.", "Return a flagged message for the supplied order.", "Mark the specified order ID as flagged.", "Report a flag for the order identified by the input.", "Flag an already selected order by its identifier.", "Return the supplied order ID in a flag message.", "Identify the provided order as flagged."),
    parameters=(Parameter(names=("order", "order_id")),),
    tasks=(Task(id="late", prompts=("Today is {today}. Flag the late order among these unshipped orders, listed as ID|promised date: {orders}. Late means the promised date is strictly before today.", "Using {today} as today's date, flag the order whose promised date has passed in {orders}. Each entry is ID|promised date; all are unshipped, and a date of today is not late.", "As of {today}, flag the unshipped order promised before today. Entries are ID|promised date: {orders}.", "Which unshipped order is late on {today}? Flag the one with a promised date strictly earlier than today: {orders} (ID|promised date).", "Flag the overdue order in {orders}; all are unshipped, fields are ID|promised date, and today is {today}. A promise for today is not late.", "Given today's date {today}, flag the unshipped order with a promised date before today. The ID|promised date records are {orders}.", "Review these unshipped orders as of {today}: {orders}. Each is ID|promised date; flag the order promised strictly before today.", "Find and flag the late unshipped order in {orders}, formatted ID|promised date. Today is {today}; today's date itself does not count as late.", "For {today}, flag the order whose promised date is earlier than today among these unshipped ID|promised date entries: {orders}.", "All orders in {orders} are unshipped and listed as ID|promised date. Using {today} as today, flag the one with a past promised date.", "Please flag the late order: today is {today}, all entries are unshipped, and {orders} uses ID|promised date. Late requires a date strictly before today.", "With {today} as the current date, identify and flag the unshipped order already past its promise date in {orders} (ID|promised date)."), answers=("{result}.", "{result}."), cases=cases),),
)
