from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        endpoints = rng.sample(("/login", "/orders", "/search", "/users", "/cart", "/health"), 3)
        latencies = rng.sample(range(20, 1000), 3)
        rows = list(zip(endpoints, latencies))
        yield {"rows": rows, "readings": "; ".join(f"{endpoint}: {latency} ms" for endpoint, latency in rows)}


def prepare(*, task_id, case):
    endpoint = max(case["rows"], key=lambda row: row[1])[0]
    return Decision(fields=case, arguments={"endpoint": endpoint})


def resolve(endpoint):
    return f"Flagged endpoint: {endpoint}."


SCHEMA = Schema(
    id="observability_highest_latency",
    tool_names=("flag_endpoint_latency", "mark_slow_endpoint", "flag_endpoint_by_path", "mark_endpoint_for_review", "record_flagged_endpoint", "flag_selected_endpoint", "register_endpoint_for_review", "mark_latency_endpoint", "submit_endpoint_flag", "flag_endpoint_for_review"),
    descriptions=("Flag an endpoint by path.", "Mark the specified endpoint for review.", "Record a flag for the selected endpoint path.", "Mark the given endpoint path for latency review.", "Register the selected endpoint for review.", "Flag the specified endpoint using its path.", "Record the endpoint chosen for latency review.", "Submit a review flag for the given endpoint.", "Mark the identified endpoint for review by path.", "Register a latency review flag for the specified endpoint."),
    parameters=(Parameter(names=("endpoint", "path")),),
    tasks=(Task(id="latency", prompts=("Flag the endpoint with the highest latency: {readings}.", "Mark the slowest endpoint by latency: {readings}.", "Among these latency readings, flag the slowest endpoint: {readings}.", "Please mark the endpoint with the largest latency for review: {readings}.", "Which endpoint has the greatest latency in {readings}? Flag it.", "Review these measurements and flag the highest-latency path: {readings}.", "From {readings}, mark the endpoint taking the longest to respond.", "Flag the endpoint whose latency is maximal in this list: {readings}.", "These are the endpoint latencies: {readings}. Mark the slowest one for review.", "Find the largest latency in {readings} and flag its endpoint.", "Can you flag the slowest path based on these latency measurements? {readings}.", "Use these readings to identify and mark the highest-latency endpoint: {readings}."), answers=("{result}", "{result}"), cases=cases),),
)
