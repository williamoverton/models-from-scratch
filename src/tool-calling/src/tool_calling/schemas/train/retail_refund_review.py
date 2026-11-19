from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randrange(30, 200)
        ids = rng.sample(range(1000, 9999), 3)
        amounts = [threshold + rng.randrange(1, 50), rng.randrange(threshold + 1), rng.randrange(threshold + 1)]
        rng.shuffle(amounts)
        yield {"threshold": str(threshold), "orders": "; ".join(f"R{n}: ${amount}" for n, amount in zip(ids, amounts)), "winner": f"R{ids[amounts.index(max(amounts))]}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"order_id": case["winner"]})


def resolve(order_id):
    return f"Order selected for refund review: {order_id}."


SCHEMA = Schema(id="retail_refund_review", tool_names=("flag_refund_review", "select_refund_order", "report_refund_review_order", "identify_order_for_refund_review", "mark_refund_order", "record_refund_review_selection", "submit_refund_review_order", "flag_order_for_refund_review", "register_refund_review_order", "choose_refund_review_order"), descriptions=("Report an order selected for refund review.", "Identify the order chosen for refund review.", "Flag the specified order for refund review.", "Record an order ID selected for refund review.", "Submit the chosen order for refund review.", "Mark a named order for refund review.", "Register the selected refund review order.", "Return the ID of the order selected for refund review.", "Capture the order chosen for refund review.", "Provide the order reference selected for refund review."), parameters=(Parameter(names=("order_id", "order_reference")),), tasks=(Task(id="review", prompts=("Refunds strictly above ${threshold} require review. Amounts by order: {orders}. Flag the sole order requiring review.", "Select the only order with a refund exceeding ${threshold} for review: {orders}. Equality does not exceed the threshold.", 'Flag the sole refund strictly above ${threshold} for review: {orders}.', 'Which order in {orders} exceeds ${threshold}? Flag it for refund review; equality does not qualify.', 'Review threshold: ${threshold}, exclusive. Flag the only qualifying order from {orders}.', 'From {orders}, select for refund review the single order over ${threshold}, not equal to it.', 'Flag the unique order needing refund review: amounts must be greater than ${threshold}; {orders}.', 'Given {orders}, identify and flag the sole refund exceeding ${threshold} for review.', 'Refund review applies only above ${threshold}. Select the only matching order: {orders}.', 'Select the order for review whose refund is strictly greater than ${threshold}: {orders}.', 'For {orders}, flag the one order with a refund over ${threshold}; equal amounts are excluded.', 'Find the single order above the ${threshold} refund-review threshold and flag it: {orders}.'), answers=("{result}", "Selection: {result}"), cases=cases),))
