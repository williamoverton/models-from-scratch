from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randrange(40, 101, 10)
        totals = [rng.randrange(1, threshold), rng.randrange(1, threshold), threshold + rng.randrange(0, 31)]
        ids = rng.sample(range(100, 999), 3)
        entries = list(zip(ids, totals))
        rng.shuffle(entries)
        yield {"threshold": str(threshold), "orders": "; ".join(f"O{number}: ${total}" for number, total in entries)}


def prepare(*, task_id, case):
    entries = [item.split(": $") for item in case["orders"].split("; ")]
    order = next(order for order, total in entries if int(total) >= int(case["threshold"]))
    return Decision(fields=case, arguments={"order": order})


SCHEMA = Schema(
    id="parcel_flag_free_shipping",
    tool_names=('report_free_shipping_order', 'report_shipping_eligible_order', 'report_free_shipping_flag', 'acknowledge_shipping_eligibility', 'confirm_order_shipping_flag', 'report_flagged_shipping_order', 'return_free_shipping_flag', 'confirm_eligible_order_flag', 'acknowledge_order_shipping_flag', 'show_free_shipping_order'),
    descriptions=('Report a free-shipping flag for the specified order.', 'Acknowledge the supplied order ID as flagged for free shipping.', 'Return a simulated free-shipping flag for the given order.', 'Confirm the selected order in a free-shipping flag message.', 'Report the provided order as flagged for free shipping.', 'Echo the order ID in a free-shipping flag acknowledgment.', 'Present the selected order as flagged for free shipping.', 'Output a free-shipping flag confirmation for the supplied order.', 'Acknowledge a free-shipping flag for the specified order ID.', 'Return a message identifying the order flagged for free shipping.'),
    parameters=(Parameter(names=("order", "order_id")),),
    tasks=(Task(id="flag", prompts=("Orders: {orders}. Free shipping applies at ${threshold} or more. Flag the sole qualifying order.", "From {orders}, mark the order eligible for free shipping at a minimum total of ${threshold}, including equality.", 'Flag the sole order in {orders} with a total at least ${threshold}, the free-shipping minimum.', 'For {orders}, mark the only free-shipping order; totals of ${threshold} or more qualify.', 'The free-shipping cutoff is ${threshold}, inclusive. Flag the qualifying order in {orders}.', 'Among {orders}, flag the sole order eligible for free shipping at ${threshold} or above.', 'Which order in {orders} qualifies for free shipping? Flag it; ${threshold} itself qualifies.', 'Given {orders} and an inclusive ${threshold} free-shipping threshold, flag the sole eligible order.', 'Select and flag the only order in {orders} whose total is at least ${threshold} for free shipping.', 'Free shipping starts at ${threshold}, including that amount. Flag the eligible order from {orders}.', 'Compare {orders} to ${threshold}: flag the sole order at or above that free-shipping minimum.', 'From these orders {orders}, flag the one whose total reaches the ${threshold} free-shipping cutoff or exceeds it.'), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(order):
    return f"Flagged order {order} for free shipping."
