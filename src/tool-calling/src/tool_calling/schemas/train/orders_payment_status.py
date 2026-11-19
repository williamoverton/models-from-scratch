from ...schema_types import Decision, Parameter, Schema, Task


PAYMENTS = {
    "O-2101": "paid", "O-2102": "pending", "O-2103": "failed", "O-2104": "refunded",
    "O-2105": "paid", "O-2106": "pending", "O-2107": "failed", "O-2108": "refunded",
    "O-2109": "paid", "O-2110": "pending",
}


def cases(rng, count):
    for _ in range(count):
        yield {"order": rng.choice(tuple(PAYMENTS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(order):
    return f"{order}: {PAYMENTS[order]}"


SCHEMA = Schema(
    id="orders_payment_status_lookup",
    tool_names=("get_payment_status", "lookup_order_payment", "find_sample_payment_status", "get_sample_order_payment", "lookup_sample_payment", "read_sample_payment_status", "retrieve_order_payment_status", "query_sample_order_payment", "check_sample_payment_status", "report_sample_order_payment"),
    descriptions=("Look up an order's payment status in the sample registry.", "Find a sample order's payment status by ID.", "Retrieve the payment status for an order from the sample registry.", "Report the sample payment state for the supplied order ID.", "Query the sample registry for an order's payment status.", "Read a sample order's payment status using its ID.", "Return the sample registry's payment status for the given order.", "Find the recorded sample payment state of an order.", "Get an order's payment status from the sample data.", "Retrieve the sample payment record identified by order ID."),
    parameters=(Parameter(names=("order", "order_id")),),
    tasks=(Task(id="payment", prompts=("Look up the payment status of order {order} in the sample registry.", "What is the sample payment status for {order}?", "Check the sample registry for order {order}'s payment status.", "Please retrieve the payment state recorded for {order} in the sample data.", "In the sample registry, what payment status is listed for order {order}?", "Find the sample payment record for {order} and report its status.", "Could you look up {order} in the sample payment registry?", "Report the payment status associated with order {order} in the sample registry.", "What does the sample registry say about payment for {order}?", "Query the sample payment data for the status of order {order}.", "Give me the recorded sample payment status of {order}.", "For order {order}, retrieve its payment status from the sample registry."), answers=("The payment registry reports {result}.", "Payment status: {result}."), cases=cases),),
)
