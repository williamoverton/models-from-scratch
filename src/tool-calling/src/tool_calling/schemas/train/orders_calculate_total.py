from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        cents = rng.randint(1, 50000)
        yield {"price": f"{cents // 100}.{cents % 100:02d}", "quantity": str(rng.randint(1, 100))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(price, quantity):
    return f"{Decimal(price) * int(quantity):.2f}"


SCHEMA = Schema(
    id="orders_price_quantity_total",
    tool_names=("calculate_total", "compute_order_total", "multiply_price_quantity", "calculate_item_total", "compute_price_quantity_total", "get_order_price_total", "calculate_units_cost", "compute_units_price", "calculate_untaxed_total", "compute_line_item_total"),
    descriptions=("Multiply a unit price in dollars by a quantity, returning dollars.", "Compute the dollar total from price and quantity.", "Calculate the total cost of the supplied units at their unit price.", "Multiply the given dollar price by the number of units.", "Return the price times quantity in dollars.", "Compute the total before tax or other charges.", "Calculate the untaxed cost for a quantity at a dollar unit price.", "Determine the dollar amount for the supplied price and count.", "Return the product of unit price and quantity as a dollar amount.", "Compute an order line total without additional charges."),
    parameters=(Parameter(names=("price", "unit_price")), Parameter(names=("quantity", "units"))),
    tasks=(Task(id="total", prompts=("Calculate the total for {quantity} units at ${price} each, with no tax or other charges.", "What is the price of {quantity} items at ${price} per item? Exclude taxes and other charges.", "Find the untaxed total for {quantity} units priced at ${price} each, with no other charges.", "Multiply ${price} per unit by {quantity} units to get the total before tax or other charges.", "How much do {quantity} items cost at ${price} each, excluding tax and additional charges?", "Compute the line total for {quantity} units at a unit price of ${price}; add no taxes or fees.", "At ${price} apiece, what is the total for {quantity} items without tax or other charges?", "Calculate the price times quantity: ${price} per unit and {quantity} units, excluding all other charges.", "Give the total cost of {quantity} units at ${price} each before taxes and other charges.", "What is the untaxed amount for {quantity} items costing ${price} per item, without additional charges?", "Please calculate the order line total for {quantity} units at ${price} each, with no tax or extras.", "For {quantity} items at a unit price of ${price}, calculate the total excluding tax and other charges."), answers=("The total is ${result}.", "The order total is ${result}."), cases=cases),),
)
