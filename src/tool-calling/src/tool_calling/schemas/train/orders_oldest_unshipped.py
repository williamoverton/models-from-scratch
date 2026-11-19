from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(1000, 9999), 3)
        days = rng.sample(range(365), 3)
        statuses = ["unshipped", "unshipped", "shipped"]
        rng.shuffle(statuses)
        rows = [f"O-{order_id}|{date(2026, 1, 1) + timedelta(days=day)}|{status}" for order_id, day, status in zip(ids, days, statuses)]
        rng.shuffle(rows)
        yield {"orders": "; ".join(rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("|") for row in case["orders"].split(";")]
    order = min((placed, order) for order, placed, status in rows if status == "unshipped")[1]
    return Decision(fields=case, arguments={"order": order})


def resolve(order):
    return f"Flagged order {order}"


SCHEMA = Schema(
    id="orders_oldest_unshipped",
    tool_names=("flag_order", "flag_selected_order", "flag_order_by_id", "flag_supplied_order", "mark_order_flagged", "report_flagged_order", "flag_order_identifier", "mark_selected_order", "flag_chosen_order", "report_order_flag"),
    descriptions=("Flag the supplied order ID.", "Flag an order identified by its ID.", "Report the given order as flagged.", "Flag the selected order using its ID.", "Return a flagged message for the supplied order.", "Mark the specified order ID as flagged.", "Report a flag for the order identified by the input.", "Flag an already selected order by its identifier.", "Return the supplied order ID in a flag message.", "Identify the provided order as flagged."),
    parameters=(Parameter(names=("order", "order_id")),),
    tasks=(Task(id="oldest", prompts=("Flag the oldest unshipped order by placement date. Entries are ID|placement date|status: {orders}.", "From {orders}, flag the unshipped order with the earliest placement date. Each entry is ID|placement date|status.", "Which unshipped order was placed first? Flag it from these ID|placement date|status records: {orders}.", "Review {orders}, formatted ID|placement date|status, and flag the earliest placed order that remains unshipped.", "Flag the oldest by placement date among the unshipped orders in {orders}. Fields are ID|placement date|status.", "Using the ID|placement date|status entries {orders}, flag the unshipped order with the earliest date.", "Find and flag the earliest placed unshipped order: {orders}. Each entry gives ID|placement date|status.", "Please flag the oldest order still unshipped in this list, based on placement date: {orders} (ID|placement date|status).", "In {orders}, each record is ID|placement date|status. Exclude shipped orders and flag the earliest remaining one.", "Which order should be flagged as the oldest unshipped? Use placement dates in {orders}, where fields are ID|placement date|status.", "Select and flag the unshipped order placed earliest from these records: {orders}. Their format is ID|placement date|status.", "Among the ID|placement date|status records {orders}, flag the unshipped order with the oldest placement date."), answers=("{result}.", "{result}."), cases=cases),),
)
