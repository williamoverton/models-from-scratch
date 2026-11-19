from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        latencies = rng.sample(range(5, 100), 3)
        statuses = ["reachable", "reachable", "unreachable"]
        rng.shuffle(statuses)
        entries = list(zip(ids, latencies, statuses))
        rng.shuffle(entries)
        yield {"routes": "; ".join(f"R-{i}={latency}ms,{status}" for i, latency, status in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["routes"].split(";")]
    candidates = [(int(details.split("ms,")[0]), route) for route, details in entries if details.endswith(",reachable")]
    return Decision(fields=case, arguments={"route": min(candidates)[1]})


def resolve(route):
    return f"Selected route {route}"


SCHEMA = Schema(
    id="network_reachable_lowest_latency",
    tool_names=("select_network_route", "report_network_route", "record_route_selection", "report_selected_route_id", "record_selected_route_id", "return_route_selection", "report_chosen_route", "record_route_identifier", "return_selected_route_id", "report_route_identifier"),
    descriptions=("Report the selected route ID.", "Record a route selection without changing routing.", "Return the identifier of the selected route without changing routing.", "Report the chosen route by ID without modifying network routes.", "Record the supplied route identifier as a selection, not a routing change.", "Return the selected route ID without applying it to the network.", "Report a route selection by its identifier without changing routing.", "Record the chosen route ID without modifying routing configuration.", "Return the supplied route identifier as the selection only.", "Report the selected route identifier rather than changing routes."),
    parameters=(Parameter(names=("route", "route_id")),),
    tasks=(Task(id="route", prompts=("Select the reachable route with lowest latency. Entries are ID=latency,status: {routes}.", "From {routes} (ID=latency,status), select the lowest-latency reachable route; ignore unreachable routes.", "Which route ID has the smallest latency among reachable entries? Routes are ID=latency,status: {routes}.", "Given {routes}, with each entry formatted ID=latency,status, report the reachable route ID with the lowest latency.", "Pick the fastest reachable route from {routes}; entries use ID=latency,status.", "For the routes {routes} (ID=latency,status), identify the reachable ID with minimum latency.", "Consider only reachable routes in {routes}, formatted ID=latency,status, and select the one with the least latency.", "What is the lowest-latency reachable route ID in {routes}? Each entry is ID=latency,status.", "Choose the route ID with the shortest latency among reachable routes: {routes}. Format: ID=latency,status.", "From the ID=latency,status entries {routes}, return the ID of the fastest reachable route.", "Among these routes, {routes}, choose the reachable route with the lowest latency; entries are ID=latency,status.", "Find the minimum-latency reachable route in {routes} and report its ID. Entries follow ID=latency,status."), answers=("{result}.", "{result}."), cases=cases),),
)
