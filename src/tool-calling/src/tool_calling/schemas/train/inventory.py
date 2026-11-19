from ...schema_types import Decision, Schema, Parameter, Task


QUANTITIES = {
    "north": {"notebooks": 18, "pens": 45, "folders": 12, "pencils": 64, "erasers": 23, "rulers": 16, "markers": 31, "binders": 9, "staplers": 8, "tape rolls": 20},
    "south": {"notebooks": 7, "pens": 22, "folders": 30, "pencils": 38, "erasers": 19, "rulers": 11, "markers": 14, "binders": 15, "staplers": 6, "tape rolls": 26},
    "east": {"notebooks": 25, "pens": 35, "folders": 16, "pencils": 48, "erasers": 21, "rulers": 13, "markers": 29, "binders": 12, "staplers": 4, "tape rolls": 18},
    "west": {"notebooks": 11, "pens": 53, "folders": 27, "pencils": 32, "erasers": 17, "rulers": 24, "markers": 20, "binders": 8, "staplers": 10, "tape rolls": 14},
    "central": {"notebooks": 33, "pens": 62, "folders": 19, "pencils": 41, "erasers": 28, "rulers": 22, "markers": 34, "binders": 17, "staplers": 12, "tape rolls": 31},
    "uptown": {"notebooks": 14, "pens": 29, "folders": 22, "pencils": 37, "erasers": 16, "rulers": 10, "markers": 18, "binders": 7, "staplers": 5, "tape rolls": 12},
    "downtown": {"notebooks": 28, "pens": 48, "folders": 34, "pencils": 55, "erasers": 24, "rulers": 19, "markers": 27, "binders": 13, "staplers": 9, "tape rolls": 23},
    "harbor": {"notebooks": 9, "pens": 17, "folders": 14, "pencils": 26, "erasers": 12, "rulers": 8, "markers": 15, "binders": 6, "staplers": 3, "tape rolls": 11},
    "airport": {"notebooks": 21, "pens": 39, "folders": 25, "pencils": 44, "erasers": 18, "rulers": 15, "markers": 22, "binders": 10, "staplers": 7, "tape rolls": 16},
    "riverside": {"notebooks": 16, "pens": 32, "folders": 20, "pencils": 36, "erasers": 15, "rulers": 12, "markers": 19, "binders": 11, "staplers": 5, "tape rolls": 13},
}


def cases(rng, count):
    for _ in range(count):
        warehouse = rng.choice(tuple(QUANTITIES))
        yield {"warehouse": warehouse, "item": rng.choice(tuple(QUANTITIES[warehouse]))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="inventory_lookup",
    tool_names=("check_stock", "inventory_lookup", "get_warehouse_stock", "lookup_item_stock", "find_inventory_quantity", "get_stock_on_hand", "check_warehouse_inventory", "lookup_warehouse_item", "retrieve_stock_quantity", "query_sample_inventory"),
    descriptions=("Look up stock in a fixed sample inventory by warehouse and item.", "Return the sample quantity on hand for an item at a warehouse.", "Find an item's quantity in a specified sample warehouse.", "Check the fixed inventory for a warehouse and product.", "Retrieve stock on hand for a named item and warehouse from the sample data.", "Query the sample inventory quantity by location and product.", "Report how many units of an item a sample warehouse holds.", "Get a warehouse item's quantity from the fixed sample inventory.", "Look up the on-hand count for an item at a sample location.", "Return the fixed sample stock count for the specified warehouse and item."),
    parameters=(
        Parameter(names=("warehouse", "location")),
        Parameter(names=("item", "product")),
    ),
    tasks=(Task(id="stock", prompts=("How many {item} are in the {warehouse} warehouse?", "Check {warehouse} stock for {item}.", "Give me the quantity of {item} on hand at the {warehouse} warehouse.", "At warehouse {warehouse}, what is the inventory count for {item}?", "Find the number of {item} stocked in {warehouse}.", "For {item}, report how much stock warehouse {warehouse} holds.", "What does the inventory show for {item} at {warehouse}?", "Please retrieve the {warehouse} warehouse's count of {item}.", "How much {item} does the {warehouse} location have in stock?", "I need the stock quantity for {item} in warehouse {warehouse}.", "Identify the on-hand inventory of {item} at the {warehouse} warehouse.", "In the {warehouse} warehouse, determine the available count of {item}."), answers=("The {warehouse} warehouse has {result} {item}.", "There are {result} {item} in {warehouse}."), cases=cases),),
)


def resolve(warehouse, item):
    return str(QUANTITIES[warehouse][item])
