from ...schema_types import Decision, Parameter, Schema, Task


QUERIES = {
    "Q-count": ("SELECT COUNT(*) FROM orders", "3"),
    "Q-sum": ("SELECT SUM(total) FROM orders", "60"),
    "Q-max": ("SELECT MAX(total) FROM orders", "30"),
}
REQUIREMENTS = {
    "Q-count": "the number of orders",
    "Q-sum": "the sum of order totals",
    "Q-max": "the largest order total",
}


def cases(rng, count):
    for _ in range(count):
        ids = list(QUERIES)
        rng.shuffle(ids)
        chosen = rng.choice(ids)
        yield {"requirement": REQUIREMENTS[chosen], "queries": "; ".join(f"{identifier}: {QUERIES[identifier][0]}" for identifier in ids)}


def prepare(*, task_id, case):
    query = next(identifier for identifier, requirement in REQUIREMENTS.items() if requirement == case["requirement"])
    return Decision(fields=case, arguments={"query": query})


def resolve(query):
    return f"Ran {query}; result: {QUERIES[query][1]}"


SCHEMA = Schema(
    id="data_query_selection_run",
    tool_names=('run_sample_query', 'execute_sample_query', 'run_orders_query', 'execute_orders_query', 'run_query_by_id', 'execute_query_id', 'invoke_sample_query', 'run_fixed_query', 'execute_fixed_orders_query', 'query_sample_orders'),
    descriptions=('Run a named query against the fixed sample orders table.', 'Execute a query ID on sample orders with totals 10, 20, and 30.', 'Run the specified query ID on the fixed sample orders table.', 'Execute the named query against sample orders with totals 10, 20, and 30.', 'Run a query by ID on the fixed orders sample.', 'Execute a supplied query ID on the sample orders table.', 'Invoke a named query against the fixed orders sample.', 'Run the selected fixed query on sample orders.', 'Execute the selected query against the fixed orders data.', 'Query the sample orders table using the given query ID.'),
    parameters=(Parameter(names=("query", "query_id")),),
    tasks=(Task(id="run", prompts=("The sample orders table has three rows with totals 10, 20, and 30. Select and run the query returning {requirement}: {queries}.", "Run the query for {requirement} from {queries}. The sample orders table contains totals 10, 20, and 30, one per row.", "Choose and execute the query for {requirement} from {queries}; sample orders has three rows with totals 10, 20, and 30.", "The sample orders rows have totals 10, 20, and 30. Which query in {queries} returns {requirement}? Run it.", "Using the three sample orders with totals 10, 20, and 30, run the query in {queries} that returns {requirement}.", "Select the query for {requirement} from {queries} and execute it on sample orders, whose three row totals are 10, 20, and 30.", "Sample orders contains three rows, totaling 10, 20, and 30 respectively. Run the query among {queries} returning {requirement}.", "From {queries}, execute the query yielding {requirement}; the three sample order totals are 10, 20, and 30.", "Run the appropriate query for {requirement} from {queries}. Sample orders has one row each with totals 10, 20, and 30.", "Given sample orders with three row totals of 10, 20, and 30, select and run the {requirement} query from {queries}.", "Find the query in {queries} returning {requirement} and run it against the sample orders table: three rows with totals 10, 20, and 30.", "The three sample orders have totals 10, 20, and 30. Execute whichever query in {queries} returns {requirement}."), answers=("{result}.", "{result}."), cases=cases),),
)
