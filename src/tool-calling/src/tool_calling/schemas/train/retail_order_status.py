from ...schema_types import Decision, Schema, Parameter, Task

ORDERS = {f"R{1000 + i}": ("processing", "shipped", "delivered", "cancelled")[i % 4] for i in range(80)}


def cases(rng, count):
    for _ in range(count):
        order_id = rng.choice(tuple(ORDERS))
        yield {"order_id": order_id}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"order_id": case["order_id"]})


def resolve(order_id):
    return f"Order {order_id} has status {ORDERS[order_id]}."


SCHEMA = Schema(id="retail_order_status", tool_names=("lookup_order_status", "check_order_state", "get_order_status", "fetch_order_status", "retrieve_order_state", "find_order_status", "read_order_status", "query_order_state", "get_recorded_order_status", "lookup_retail_order_state"), descriptions=("Look up an order's status in the sample order records.", "Retrieve the recorded status for an order ID.", "Get the stored status of a sample order.", "Find the recorded state associated with an order ID.", "Fetch an order's current recorded status from the sample records.", "Read the status recorded for a retail order.", "Query the sample records for an order's state.", "Return the stored status for the specified order.", "Check the recorded state of a sample order.", "Identify an order's status from its order reference."), parameters=(Parameter(names=("order_id", "order_reference")),), tasks=(Task(id="status", prompts=("What is the status of order {order_id}?", "Look up the recorded state of order {order_id}.", 'Check the recorded status of order {order_id}.', 'Find the sample record state for order {order_id}.', 'Please retrieve the status for {order_id}.', 'What state is order {order_id} recorded as?', 'Get the stored order status for {order_id}.', 'Show me the recorded status of {order_id}.', 'Could you check order {order_id} in the sample records?', 'Fetch the current recorded state of order {order_id}.', 'For order {order_id}, return its recorded status.', 'Query the order records for the state of {order_id}.'), answers=("{result}", "Here is the status: {result}"), cases=cases),))
