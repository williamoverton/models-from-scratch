from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randrange(5, 50)
        ids = rng.sample(range(100, 999), 4)
        quantities = [rng.randrange(threshold), threshold + rng.randrange(20), threshold + rng.randrange(20), threshold + rng.randrange(20)]
        rng.shuffle(quantities)
        yield {"threshold": str(threshold), "items": "; ".join(f"I{n}: {q}" for n, q in zip(ids, quantities)), "winner": f"I{ids[quantities.index(min(quantities))]}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"item_id": case["winner"]})


def resolve(item_id):
    return f"Low-stock item selected: {item_id}."


SCHEMA = Schema(id="purchasing_low_stock", tool_names=("flag_low_stock", "select_low_stock_item", "report_low_stock_item", "identify_selected_low_stock", "record_low_stock_selection", "show_low_stock_item", "report_selected_item", "mark_low_stock_item", "return_low_stock_selection", "note_low_stock_item"), descriptions=("Report an item selected as low stock.", "Identify a selected low-stock item by ID.", "Return the identifier of the item selected as low stock.", "Report the selected low-stock product.", "Mark the specified item as the low-stock selection.", "Show which item was selected for low stock.", "Record an item ID as the low-stock selection.", "Return the selected low-stock item identifier.", "Note the item identified as low stock.", "Report the product selected for low stock by ID."), parameters=(Parameter(names=("item_id", "product_id")),), tasks=(Task(id="low", prompts=("Stock is low when strictly below {threshold} units. Item quantities: {items}. Flag the sole low-stock item.", "Select the only item below {threshold} units from {items}; equality is not low stock.", "Which item in {items} is strictly below the {threshold}-unit threshold? Flag that item.", "Identify the sole low-stock item in {items}; low means fewer than {threshold} units.", "Report the item ID with stock under {threshold} units: {items}. Equality does not count.", "From {items}, flag the one item whose quantity is less than {threshold}.", "Quantities are {items}. Select the only item below {threshold} units, not equal to it.", "Find the low-stock item among {items}, using a strict cutoff of {threshold} units.", "Which ID in {items} has fewer than {threshold} units? Mark it low stock.", "Given {items}, report the sole item under the {threshold}-unit limit; equal is not low.", "Pick the item with quantity strictly less than {threshold} from {items}.", "Flag the unique item below {threshold} units in this inventory: {items}."), answers=("{result}", "Selection: {result}"), cases=cases),))
