from ...schema_types import Decision, Schema, Parameter, Task

SUPPLIERS = {f"P{100 + i}": supplier for i, supplier in enumerate(("Acorn", "Beacon", "Cedar", "Delta", "Elm", "Fjord", "Grove", "Harbor", "Ivy", "Juniper", "Kite", "Linden"))}


def cases(rng, count):
    for _ in range(count):
        yield {"product_id": rng.choice(tuple(SUPPLIERS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"product_id": case["product_id"]})


def resolve(product_id):
    return SUPPLIERS[product_id]


SCHEMA = Schema(id="purchasing_supplier_lookup", tool_names=("lookup_product_supplier", "find_supplier", "get_product_supplier", "query_supplier_directory", "identify_product_supplier", "retrieve_item_supplier", "find_supplier_by_product", "lookup_item_supplier", "read_product_supplier", "show_product_supplier"), descriptions=("Look up the supplier of a product in the sample directory.", "Return the sample directory supplier for a product ID.", "Find the recorded supplier for a product identifier.", "Query the sample directory for a product's supplier.", "Retrieve the supplier associated with an item ID.", "Identify who supplies the given product in the sample directory.", "Show the supplier recorded for a product.", "Read a product's supplier from the sample directory.", "Get the supplier assigned to the specified product ID.", "Find an item's supplier using its product identifier."), parameters=(Parameter(names=("product_id", "item_id")),), tasks=(Task(id="supplier", prompts=("Who supplies product {product_id}?", "Find the supplier for product ID {product_id}.", "Look up {product_id} in the sample supplier directory.", "Which supplier is recorded for product {product_id}?", "Get the directory supplier assigned to {product_id}.", "Identify the supplier of item {product_id}.", "Query the sample directory for the supplier of {product_id}.", "What supplier is associated with product ID {product_id}?", "Retrieve the recorded supplier for {product_id}.", "Show who supplies item {product_id} in the sample directory.", "Check the supplier directory for product {product_id}.", "Give the supplier listed for {product_id}."), answers=("The supplier is {result}.", "{product_id} is supplied by {result}."), cases=cases),))
