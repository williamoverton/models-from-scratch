from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"WO-{number}" for number in range(100, 200)], 3)
        severities = rng.sample(range(1, 6), 3)
        yield {"orders": ", ".join(f"{order}={severity}" for order, severity in zip(ids, severities))}


def prepare(*, task_id, case):
    orders = (entry.split("=") for entry in case["orders"].split(", "))
    order, _ = max(orders, key=lambda entry: int(entry[1]))
    return Decision(fields=case, arguments={"order": order})


def resolve(order):
    return f"Prioritized work order: {order}."


SCHEMA = Schema(
    id="facilities_prioritize_work_order",
    tool_names=("prioritize_work_order", "mark_order_for_attention", "record_priority_order", "flag_priority_work_order", "report_priority_order", "mark_priority_work_order", "set_work_order_priority", "register_priority_order", "identify_priority_work_order", "record_order_for_attention"),
    descriptions=("Record a work order as the priority.", "Mark the specified work order for attention.", "Report the work order chosen as the priority.", "Flag a specified work order for attention.", "Record the identifier of the priority work order.", "Mark an order as the selected priority.", "Register a work order for priority attention.", "Return the work order designated as the priority.", "Identify the supplied work order as prioritized.", "Record which work order is marked for attention."),
    parameters=(Parameter(names=("order", "work_order_id")),),
    tasks=(Task(id="prioritize", prompts=("Work orders and severity scores: {orders}. Higher scores mean greater severity. Prioritize the highest-severity order.", "Choose the most severe work order from {orders}; severity increases with the numeric score.", "From {orders}, prioritize the work order with the largest severity score; higher is more severe.", "Which work order in {orders} has the highest severity? Higher scores indicate greater severity; prioritize it.", "Select the most severe work order in {orders}, where larger numeric scores mean more severe.", "Order severities are {orders}. Flag the order with the highest score as the priority; higher means more severe.", "Prioritize one order from {orders}: choose the greatest score, since higher scores represent greater severity.", "Given {orders}, identify the priority work order by maximum severity score, with higher meaning more severe.", "Choose the highest-scoring work order in {orders} for priority attention; scores rise with severity.", "Work orders: {orders}. Mark the most severe as priority, interpreting a higher score as greater severity.", "Find and prioritize the order with the largest severity value in {orders}; a larger value indicates greater severity.", "Among {orders}, which work order should be prioritized based on the highest score? Larger scores mean more severe."), answers=("{result}", "{result}"), cases=cases),),
)
