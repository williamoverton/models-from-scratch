from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("North", "South", "East", "West", "Central", "Harbor"), 3)
        required = rng.randint(10, 100)
        stocks = [required + rng.randint(0, 30), required - rng.randint(1, 9), required - rng.randint(1, 9)]
        rng.shuffle(stocks)
        rows = list(zip(names, stocks))
        rng.shuffle(rows)
        yield {"required": str(required), "warehouses": "; ".join(f"{name}={stock}" for name, stock in rows)}


def prepare(*, task_id, case):
    rows = [row.strip().split("=") for row in case["warehouses"].split(";")]
    warehouse = next(name for name, stock in rows if int(stock) >= int(case["required"]))
    return Decision(fields=case, arguments={"warehouse": warehouse})


def resolve(warehouse):
    return f"Selected warehouse {warehouse}"


SCHEMA = Schema(
    id="inventory_warehouse_sufficient_stock",
    tool_names=("select_warehouse", "report_stock_location", "choose_warehouse", "report_warehouse", "select_stock_location", "record_warehouse_selection", "name_selected_warehouse", "set_selected_warehouse", "report_selected_location", "identify_warehouse"),
    descriptions=("Report the selected warehouse name.", "Select a warehouse by name.", "Record the supplied warehouse as the selection.", "Report the specified stock location.", "Select the given warehouse using its name.", "Return the selected warehouse's name.", "Identify the warehouse supplied by name.", "Record a selected stock location by name.", "Report the warehouse chosen by the caller.", "Set the supplied warehouse as the selected location."),
    parameters=(Parameter(names=("warehouse", "location")),),
    tasks=(Task(id="sufficient", prompts=("Select the warehouse that can supply {required} units from {warehouses}. Entries are warehouse=stock; an exact match is enough.", "Which warehouse in {warehouses} has at least {required} units? Entries are warehouse=stock. Select the one that can fill the entire request.", "Warehouse stocks are {warehouses}, in warehouse=stock format. Select the one able to supply all {required} units; equality is sufficient.", "Find and select the warehouse with stock of at least {required} units in {warehouses}. Each entry is warehouse=stock.", "From {warehouses} (warehouse=stock), select the warehouse that can fulfill the entire {required}-unit request, including an exact stock match.", "A request needs {required} units. Select the warehouse with enough stock in {warehouses}; entries are warehouse=stock and exactly {required} is sufficient.", "Which single warehouse can supply {required} units? Select it from {warehouses}, listed as warehouse=stock; stock equal to the request qualifies.", "Given warehouse=stock entries {warehouses}, choose the warehouse holding at least {required} units for the full request.", "Select a warehouse from {warehouses} to fill all {required} units. Entries are warehouse=stock; a warehouse with exactly the required quantity qualifies.", "The stock list {warehouses} uses warehouse=stock. Select the warehouse whose stock meets or exceeds the full requirement of {required} units.", "For a {required}-unit order, select the warehouse able to supply the whole quantity from {warehouses} (warehouse=stock); an exact match counts.", "Identify and select the warehouse in {warehouses} with at least {required} units. Records are warehouse=stock and the entire request must be filled."), answers=("{result}.", "{result}."), cases=cases),),
)
