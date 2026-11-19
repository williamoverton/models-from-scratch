from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        products = rng.sample(("mugs", "lamps", "bottles", "vases", "clocks", "notebooks", "pens", "rulers"), 3)
        maximums = [rng.randint(10, 100) for _ in products]
        offsets = [rng.randint(1, 20), 0, -rng.randint(1, 9)]
        rng.shuffle(offsets)
        rows = [f"{product}|{maximum + offset}|{maximum}" for product, maximum, offset in zip(products, maximums, offsets)]
        rng.shuffle(rows)
        yield {"inventory": "; ".join(rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("|") for row in case["inventory"].split(";")]
    product = next(product for product, stock, maximum in rows if int(stock) > int(maximum))
    return Decision(fields=case, arguments={"product": product})


def resolve(product):
    return f"Flagged product {product}"


SCHEMA = Schema(
    id="inventory_overstock_maximum",
    tool_names=("flag_overstock", "flag_inventory_product", "mark_inventory_product", "flag_product_by_name", "mark_product", "tag_inventory_product", "flag_selected_product", "mark_selected_item", "record_product_flag", "set_product_flag"),
    descriptions=("Flag the supplied product.", "Flag a product identified by name.", "Mark the specified inventory product.", "Flag the selected product using its name.", "Apply a flag to the given product.", "Record a flag for the supplied inventory item.", "Mark a product identified by name.", "Set a flag on the selected item.", "Flag an inventory product specified by name.", "Mark the supplied product for attention."),
    parameters=(Parameter(names=("product", "item")),),
    tasks=(Task(id="overstock", prompts=("Flag the overstocked product in {inventory}. Entries are product|stock|maximum; overstock means stock strictly exceeds maximum.", "Which product should be flagged for exceeding its maximum? {inventory}. Each entry is product|stock|maximum; stock equal to maximum is not overstocked.", "Inventory entries are product|stock|maximum: {inventory}. Flag the product whose stock is strictly above its maximum; equality does not count.", "Find and flag the overstocked product in {inventory}, formatted product|stock|maximum. Only stock greater than maximum qualifies.", "For {inventory} (product|stock|maximum), flag the product exceeding its maximum; a stock equal to the maximum is not overstock.", "Compare stock with maximum in {inventory}, where entries are product|stock|maximum. Flag the product strictly over its maximum.", "Which item in {inventory} has stock greater than its maximum? Flag it. Entries are product|stock|maximum; equal values do not qualify.", "Flag the product above its stock maximum from {inventory}. Each record is product|stock|maximum; being exactly at maximum is acceptable.", "In these product|stock|maximum records, flag the only product whose stock exceeds its maximum, not one merely equal to it: {inventory}.", "Use {inventory}, listed as product|stock|maximum, to flag the product with stock strictly greater than maximum.", "The stock report {inventory} uses product|stock|maximum entries. Flag the product over its limit; equality with the limit is not overstock.", "Identify and flag the product in {inventory} for which stock is higher than maximum. The entries are product|stock|maximum, and equality does not qualify."), answers=("{result}.", "{result}."), cases=cases),),
)
