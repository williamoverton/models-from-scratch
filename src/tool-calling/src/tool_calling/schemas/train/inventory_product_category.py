from ...schema_types import Decision, Parameter, Schema, Task


CATEGORIES = {
    "notebook": "stationery", "pen": "stationery", "ruler": "stationery",
    "mug": "kitchenware", "bottle": "kitchenware", "plate": "kitchenware",
    "lamp": "lighting", "bulb": "lighting", "vase": "decor", "clock": "decor",
}


def cases(rng, count):
    for _ in range(count):
        yield {"product": rng.choice(tuple(CATEGORIES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(product):
    return f"{product}: {CATEGORIES[product]}"


SCHEMA = Schema(
    id="inventory_product_category_lookup",
    tool_names=("get_product_category", "lookup_inventory_category", "find_catalog_category", "get_item_category", "lookup_product_classification", "query_sample_category", "find_product_category", "retrieve_catalog_category", "check_inventory_category", "read_product_category"),
    descriptions=("Look up a product's category in the sample inventory catalog.", "Find a sample catalog product's category by name.", "Return the category assigned to a named product in the sample catalog.", "Retrieve a product's sample inventory classification.", "Query the fixed catalog for an item's category.", "Get the catalog category for the specified sample product.", "Find how a named item is categorized in the sample inventory.", "Report a product's category from the sample catalog.", "Read the category associated with an item in the fixed catalog.", "Check the sample inventory catalog for a product's category."),
    parameters=(Parameter(names=("product", "item")),),
    tasks=(Task(id="category", prompts=("Look up the category of {product} in the sample inventory catalog.", "What category does {product} have in the sample catalog?", "Find the sample inventory catalog category assigned to {product}.", "In the sample catalog, which category contains {product}?", "How is {product} classified in the sample inventory catalog?", "Give me the category recorded for {product} in the sample catalog.", "For {product}, retrieve its classification from the sample inventory catalog.", "Consult the sample catalog and identify the category of {product}.", "What does the sample inventory catalog list as the category for {product}?", "I need the sample catalog's category entry for {product}.", "Which sample inventory category is associated with {product}?", "Report the category under which the sample catalog places {product}."), answers=("The catalog reports {result}.", "Product category: {result}."), cases=cases),),
)
