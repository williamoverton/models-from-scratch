from ...schema_types import Decision, Parameter, Schema, Task


TABLES = {
    "customers": "customer_id INT, name TEXT",
    "orders": "order_id INT, customer_id INT, total DECIMAL",
    "products": "product_id INT, price DECIMAL",
    "events": "event_id INT, event_time TIMESTAMP",
}


def cases(rng, count):
    for _ in range(count):
        yield {"table": rng.choice(tuple(TABLES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"table": case["table"]})


def resolve(table):
    return f"{table}: {TABLES[table]}"


SCHEMA = Schema(
    id="data_table_description_lookup",
    tool_names=('describe_sample_table', 'get_sample_table_columns', 'describe_catalog_table', 'list_sample_table_columns', 'lookup_table_description', 'get_table_schema', 'describe_table_columns', 'fetch_sample_schema', 'show_catalog_columns', 'lookup_sample_table_schema'),
    descriptions=('Look up columns and types in the sample table catalog.', 'Describe a named table from the sample catalog.', 'Describe columns and types for a named sample table.', 'List the named sample table’s columns and types.', 'Look up a table description in the sample catalog.', 'Retrieve column names and types for a sample table.', 'Describe the supplied table’s catalog columns.', 'Fetch the schema of a named sample table.', 'Show columns and types from the sample catalog.', 'Find the named table schema in the sample catalog.'),
    parameters=(Parameter(names=("table", "table_name")),),
    tasks=(Task(id="describe", prompts=("Describe the columns and types of {table} in the sample table catalog.", "What columns and types does the sample catalog list for {table}?", "Look up the column names and types for {table} in the sample catalog.", "Show the sample catalog schema for table {table}, including column types.", "Which columns and types are recorded for {table} in the sample table catalog?", "Give me the columns and their types for {table} from the sample catalog.", "Describe {table} using its columns and types in the sample catalog.", "Retrieve the sample table catalog description of {table}: column names and types.", "For sample table {table}, list its cataloged columns and data types.", "What is the column-and-type schema of {table} in the sample catalog?", "Consult the sample catalog and describe the columns and types of {table}.", "Please provide the column names and types listed for {table} in the sample table catalog."), answers=("{result}.", "Description: {result}."), cases=cases),),
)
