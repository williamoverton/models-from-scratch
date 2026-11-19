from datetime import date, timedelta
from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        today = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        window = rng.randrange(10, 45)
        ages = [rng.randrange(window + 1), window + rng.randrange(1, 20), window + rng.randrange(20, 40)]
        rng.shuffle(ages)
        ids = rng.sample(range(1000, 9999), 3)
        yield {"today": today.isoformat(), "window": str(window), "orders": "; ".join(f"R{n}: {(today - timedelta(days=age)).isoformat()}" for n, age in zip(ids, ages)), "winner": f"R{ids[ages.index(min(ages))]}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"order_id": case["winner"]})


def resolve(order_id):
    return f"Returnable order selected: {order_id}."


SCHEMA = Schema(id="retail_returnable", tool_names=("flag_returnable", "select_returnable_order", "report_returnable_order", "identify_returnable_order", "mark_returnable_order", "record_returnable_selection", "submit_returnable_order", "flag_order_as_returnable", "register_returnable_order", "choose_returnable_order"), descriptions=("Identify an order as returnable by its ID.", "Report the selected returnable order ID.", "Flag the specified order as returnable.", "Record the ID of the selected returnable order.", "Submit the order chosen as returnable.", "Mark an order as returnable by reference.", "Register the selected returnable order.", "Return the ID of the order identified as returnable.", "Capture the order selected for return eligibility.", "Provide the reference of the returnable order."), parameters=(Parameter(names=("order_id", "order_reference")),), tasks=(Task(id="eligible", prompts=("Today is {today}. A purchase is returnable through purchase date plus {window} calendar days, inclusive. Orders (ID: purchase date): {orders}. Flag the sole returnable order.", "Using {today} as today and an inclusive {window}-day return deadline measured from purchase date, flag the only eligible order: {orders}.", 'As of {today}, flag the sole returnable order in {orders}; the deadline is purchase date plus {window} calendar days, inclusive.', 'Orders: {orders}. On {today}, select the only one still returnable through its purchase date plus {window} days inclusive.', 'Flag the unique eligible order among {orders} on {today}, using an inclusive deadline {window} calendar days after purchase.', 'With today {today}, identify and flag the only returnable purchase in {orders}; allow through purchase date plus {window} days inclusive.', 'Find the sole order in {orders} returnable on {today}; the {window}-calendar-day deadline after purchase is inclusive. Flag it.', 'Today: {today}. Purchases: {orders}. Flag the only order not past purchase date plus {window} calendar days, inclusive.', 'Select the one returnable order from {orders} as of {today}; its return deadline is {window} calendar days after purchase, inclusive.', 'For {today}, flag the sole eligible order in {orders}, counting through purchase date plus {window} calendar days inclusive.', 'Which order in {orders} is still returnable on {today}? Flag it; the deadline is purchase date plus {window} days inclusive.', 'Using {today} and {orders}, flag the one order within its inclusive return deadline of purchase date plus {window} calendar days.'), answers=("{result}", "Selection: {result}"), cases=cases),))
