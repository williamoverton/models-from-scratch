from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        customer, other_customer = rng.sample(("Avery", "Blair", "Casey", "Devon", "Emery", "Finley"), 2)
        product, other_product = rng.sample(("mug", "lamp", "notebook", "bottle", "clock", "vase"), 2)
        ids = rng.sample(range(1000, 9999), 3)
        rows = [(ids[0], customer, product), (ids[1], customer, other_product), (ids[2], other_customer, product)]
        rng.shuffle(rows)
        yield {"customer": customer, "product": product, "orders": "; ".join(f"O-{order}|{name}|{item}" for order, name, item in rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("|") for row in case["orders"].split(";")]
    order = next(order for order, customer, product in rows if customer == case["customer"] and product == case["product"])
    return Decision(fields=case, arguments={"order": order})


def resolve(order):
    return f"Selected order {order}"


SCHEMA = Schema(
    id="orders_customer_product_match",
    tool_names=("select_order", "report_matching_order", "report_selected_order", "report_order_id", "identify_selected_order", "return_selected_order", "present_selected_order", "show_selected_order", "report_chosen_order", "return_order_selection"),
    descriptions=("Select the supplied order ID.", "Report a selected order by ID.", "Return the supplied ID as the selected order.", "Report the given order as selected.", "Identify the selected order using its supplied ID.", "Return a selection message for the given order ID.", "Report an order selection from the supplied ID.", "Show the supplied order ID as the chosen order.", "Provide the ID of an already selected order.", "Output the given order ID in a selection message."),
    parameters=(Parameter(names=("order", "order_id")),),
    tasks=(Task(id="match", prompts=("Select the order for customer {customer} and product {product}. Entries are ID|customer|product: {orders}.", "Which order in {orders} matches both {customer} and {product}? Entries are ID|customer|product; select its ID.", "Find the order ID for {customer} buying {product}; the entries are ID|customer|product: {orders}.", "From these ID|customer|product entries, select the order matching customer {customer} and product {product}: {orders}.", "Identify the order for {customer}'s {product} from {orders}, formatted ID|customer|product.", "Which ID belongs to the {product} order placed by {customer}? Records in ID|customer|product format: {orders}.", "Please select the matching order for customer {customer}, product {product}: {orders} (ID|customer|product).", "In {orders}, each record is ID|customer|product. Return the order ID matching both {customer} and {product}.", "Locate the {product} purchase by {customer} and select its order ID from {orders}; fields are ID|customer|product.", "Choose the ID whose customer is {customer} and product is {product}. The records are ID|customer|product: {orders}.", "For customer {customer}, find the {product} order in this ID|customer|product list and select it: {orders}.", "Select the order matching these two criteria: customer {customer}, product {product}. Entries are ID|customer|product: {orders}."), answers=("{result}.", "{result}."), cases=cases),),
)
