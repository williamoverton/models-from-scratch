from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        stock = rng.randint(0, 1000)
        yield {"stock": str(stock), "sold": str(rng.randint(0, stock))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(stock, sold):
    return str(int(stock) - int(sold))


SCHEMA = Schema(
    id="inventory_stock_after_sales",
    tool_names=("calculate_remaining_stock", "stock_after_sales", "subtract_sold_units", "compute_stock_remaining", "calculate_inventory_after_sales", "remaining_inventory", "compute_unsold_stock", "get_remaining_units", "subtract_sales_from_stock", "calculate_stock_balance"),
    descriptions=("Subtract units sold from starting stock.", "Calculate stock remaining after sales.", "Compute starting inventory minus units sold.", "Find the remaining units given starting stock and sales.", "Calculate the stock balance after subtracting sold units.", "Return the difference between initial stock and units sold.", "Work out unsold inventory from starting stock and sales.", "Determine remaining stock with no other inventory changes.", "Subtract the sales count from the initial inventory count.", "Compute units left after the specified sales."),
    parameters=(Parameter(names=("stock", "starting_stock")), Parameter(names=("sold", "units_sold"))),
    tasks=(Task(id="remaining", prompts=("Starting with {stock} units, {sold} are sold. How many remain, assuming no other stock changes?", "Calculate remaining stock after selling {sold} of {stock} units, with no other inventory changes.", "Inventory begins at {stock} units and sales remove {sold}; there are no other changes. Find the units left.", "With {stock} units initially and {sold} sold, what is the remaining stock if nothing else changes?", "Subtract {sold} sold units from the starting inventory of {stock}; no other stock movements occur. Report the balance.", "A stock of {stock} units has sales of {sold} units and no other changes. How many units are still on hand?", "How much inventory remains when {sold} units are sold from {stock} units, assuming no other changes?", "Given an initial stock of {stock} and sales of {sold}, determine the units left without any other inventory changes.", "The only change to {stock} starting units is a sale of {sold}. Calculate the remaining units.", "After selling {sold} units from a starting count of {stock}, find the inventory balance; nothing else changes.", "From {stock} units in stock, remove {sold} sold units. Assuming no other changes, how many remain?", "No stock changes occur apart from selling {sold} of the original {stock} units. Give the remaining quantity."), answers=("{result} units remain.", "Remaining stock: {result} units."), cases=cases),),
)
