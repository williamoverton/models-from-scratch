from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        routes = rng.sample(("Amber", "Birch", "Cedar", "Delta", "Elm", "Fjord"), 3)
        transfers = rng.sample(range(5), 3)
        entries = list(zip(routes, transfers))
        rng.shuffle(entries)
        yield {"routes": "; ".join(f"{route}={number}" for route, number in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["routes"].split(";")]
    route = min(entries, key=lambda entry: int(entry[1]))[0]
    return Decision(fields=case, arguments={"route": route})


def resolve(route):
    return f"Selected route: {route}"


SCHEMA = Schema(
    id="travel_fewest_transfers_select",
    tool_names=('report_transfer_route', 'identify_route_choice', 'return_selected_route', 'state_route_choice', 'show_selected_route', 'report_route_choice', 'name_selected_route', 'display_route_choice', 'present_selected_route', 'provide_selected_route'),
    descriptions=('Report the supplied selected route name.', 'Return a selected route without reserving it.', 'State the chosen route by name.', 'Present the provided route selection.', 'Identify a route already selected by name.', 'Show the supplied route choice.', 'Return the name of a chosen route.', 'Report a route selection without booking.', 'Display the provided selected route name.', 'Provide the chosen route name.'),
    parameters=(Parameter(names=("route", "route_name")),),
    tasks=(Task(id="fewest", prompts=("Choose the route with the fewest transfers. Entries are route=transfer count: {routes}.", "Select the route requiring the smallest number of transfers from {routes}; entries are route=transfer count.", 'Report the route with the lowest transfer count in {routes}, formatted route=count.', 'Among {routes} (route=transfer count), which route has the fewest transfers? Select it.', 'The entries {routes} map routes to transfer counts. Choose the smallest count’s route.', 'Find and report the route requiring the least transfers from {routes}; entries are route=transfer count.', 'Using route=transfer count entries {routes}, select the minimum-transfer route.', 'Which route should be selected for the fewest transfers? Counts by route: {routes}.', 'Compare transfer counts in {routes}, each route=count, and select the lowest.', 'Choose the route with the smallest transfer count from the route=count list {routes}.', 'From {routes}, a list of route=transfer count pairs, identify the least-transfer route.', 'Select the route whose transfer count is minimal in {routes} (route=count).'), answers=("{result}.", "The choice is {result}."), cases=cases),),
)
