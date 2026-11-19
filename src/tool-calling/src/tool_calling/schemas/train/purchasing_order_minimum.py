from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        minimum = rng.randrange(1, 101)
        quantity = max(0, minimum + rng.randrange(-20, 21))
        yield {"quantity": str(quantity), "minimum": str(minimum)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(quantity, minimum):
    return "meets the minimum" if int(quantity) >= int(minimum) else "does not meet the minimum"


SCHEMA = Schema(id="purchasing_order_minimum", tool_names=('check_order_minimum', 'assess_minimum_quantity', 'compare_order_to_minimum', 'order_meets_minimum', 'check_minimum_order_quantity', 'evaluate_order_quantity', 'verify_quantity_minimum', 'test_order_minimum', 'get_minimum_order_status', 'compare_quantity_with_minimum'), descriptions=('Check whether an order quantity is at least the minimum.', 'Compare quantity against an inclusive minimum order quantity.', 'Determine whether the given quantity meets or exceeds the order minimum.', 'Report whether an order satisfies the minimum, including equality.', 'Check the order quantity against the minimum with equality qualifying.', 'Return whether the quantity is at least the specified minimum.', 'Assess if the order quantity meets the inclusive minimum.', 'Compare an order’s quantity to its minimum and report whether it qualifies.', 'Determine if the quantity satisfies the minimum order requirement, including equality.', 'Evaluate whether the specified quantity reaches the inclusive order minimum.'), parameters=(Parameter(names=("quantity", "order_quantity")), Parameter(names=("minimum", "minimum_quantity"))), tasks=(Task(id="minimum", prompts=("The order is for {quantity} units and the minimum is {minimum} units. Does it meet the minimum? Equality qualifies.", "Check whether {quantity} units satisfy a minimum order of {minimum} units, inclusive.", 'Does an order of {quantity} units reach the {minimum}-unit minimum? Equal quantities qualify.', 'Compare {quantity} units with the inclusive minimum of {minimum} units; does the order qualify?', 'Is {quantity} units at least the required {minimum} units?', 'The minimum order is {minimum} units. Determine whether {quantity} units meet it, including equality.', 'Check an order of {quantity} units against a {minimum}-unit minimum; meeting it exactly counts.', 'With a minimum of {minimum} units, does the {quantity}-unit order satisfy it at or above the limit?', 'Assess whether {quantity} units meet the minimum of {minimum} units, with equality accepted.', 'Is the order quantity {quantity} units greater than or equal to the {minimum}-unit minimum?', 'For {quantity} units ordered and {minimum} units minimum, decide if the inclusive requirement is met.', 'Determine if an order for {quantity} units meets a {minimum}-unit minimum; equality is sufficient.'), answers=("The order {result}.", "It {result}."), cases=cases),))
