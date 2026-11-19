from datetime import date, timedelta
from ...schema_types import Decision, Schema, Parameter, Task

ORDERS = {f"R{2000 + i}": (date(2024, 1, 1) + timedelta(days=i * 7), 7 + i % 54) for i in range(80)}


def cases(rng, count):
    for _ in range(count):
        yield {"order_id": rng.choice(tuple(ORDERS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"order_id": case["order_id"]})


def resolve(order_id):
    purchase_date, window_days = ORDERS[order_id]
    return (purchase_date + timedelta(days=window_days)).isoformat()


SCHEMA = Schema(id="retail_return_deadline", tool_names=("lookup_return_deadline", "return_by_date", "get_order_return_deadline", "find_return_by_date", "retrieve_order_return_date", "calculate_order_return_deadline", "check_order_return_deadline", "get_return_cutoff_date", "lookup_order_return_by", "fetch_return_deadline"), descriptions=("Look up an order's return deadline in the sample records, calculated as purchase date plus its calendar-day window.", "Retrieve the return-by date for an order from its stored purchase date and return window.", "Find an order's return-by date using its recorded purchase date and calendar-day window.", "Get the return deadline for a sample order.", "Calculate an order's return deadline from its stored purchase date and return window.", "Fetch the date through which an order can be returned from the sample records.", "Look up the calendar date ending an order's stored return window.", "Retrieve an order's purchase date plus its return window in days.", "Determine the recorded order's return-by date.", "Check the return cutoff date for an order in the sample records."), parameters=(Parameter(names=("order_id", "order_reference")),), tasks=(Task(id="deadline", prompts=("What is the return deadline for order {order_id}?", "Look up the return-by date for order {order_id}.", 'Find the return-by date for order {order_id}.', 'When is order {order_id} due to be returned?', 'Retrieve the return deadline for {order_id}.', 'Give me the return cutoff date for order {order_id}.', 'Check the sample records for the return-by date of {order_id}.', 'What date ends the return window for order {order_id}?', 'Calculate the recorded return deadline for {order_id}.', 'For order {order_id}, what is the last return date?', 'Get the return window cutoff for order {order_id}.', 'Please determine the return-by date of {order_id}.'), answers=("The deadline is {result}.", "Return by {result}."), cases=cases),))
