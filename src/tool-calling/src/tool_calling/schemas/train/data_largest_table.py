from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        tables = rng.sample(("orders", "events", "customers", "products", "sessions", "logs"), 3)
        sizes = rng.sample(range(1, 1000), 3)
        entries = list(zip(tables, sizes))
        rng.shuffle(entries)
        yield {"tables": "; ".join(f"{name}={size} GB" for name, size in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["tables"].split(";")]
    table = max(entries, key=lambda entry: int(entry[1].split()[0]))[0]
    return Decision(fields=case, arguments={"table": table})


def resolve(table):
    return f"Inspection requested for {table}"


SCHEMA = Schema(
    id="data_largest_table_inspect",
    tool_names=('inspect_sample_table', 'request_table_inspection', 'inspect_catalog_table', 'submit_table_inspection', 'inspect_table_by_name', 'record_table_inspection', 'request_sample_table_inspection', 'flag_table_for_inspection', 'register_table_inspection', 'review_sample_table'),
    descriptions=('Request inspection of a named sample table.', 'Record a table inspection request.', 'Request inspection of the specified sample table.', 'Submit the named table for inspection.', 'Record an inspection request for a sample table.', 'Register a request to inspect the supplied table.', 'Request an inspection of the named sample table.', 'Mark the given sample table for inspection.', 'Register a table inspection request.', 'Request review of the specified sample table.'),
    parameters=(Parameter(names=("table", "table_name")),),
    tasks=(Task(id="inspect", prompts=("Inspect the largest table by size. Entries are table=size: {tables}.", "From {tables} (table=size), request inspection of the table with the greatest size.", "Request inspection of the largest table in {tables}, where entries are table=size.", "Which table is largest? Inspect it using these table=size entries: {tables}.", "Using {tables} as table=size pairs, inspect the table with the maximum size.", "Find the greatest size in {tables} (table=size) and request inspection of that table.", "Please inspect the largest table listed in these table=size records: {tables}.", "Select the table with the highest size from {tables} (table=size) and inspect it.", "For {tables}, which gives table=size, request an inspection of the biggest table.", "Inspect the table whose size is greatest among the table=size entries {tables}.", "The table sizes are {tables} (table=size). Request inspection of the largest.", "From these table=size values, identify the largest table and inspect it: {tables}."), answers=("{result}.", "{result}."), cases=cases),),
)
