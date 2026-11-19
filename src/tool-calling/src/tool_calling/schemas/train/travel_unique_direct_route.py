from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        routes = rng.sample(("Amber", "Birch", "Cedar", "Delta", "Elm", "Fjord"), 3)
        transfers = [0, rng.randint(1, 3), rng.randint(1, 3)]
        rng.shuffle(transfers)
        entries = list(zip(routes, transfers))
        rng.shuffle(entries)
        yield {"routes": "; ".join(f"{route}={number}" for route, number in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["routes"].split(";")]
    route = next(route for route, transfers in entries if int(transfers) == 0)
    return Decision(fields=case, arguments={"route": route})


def resolve(route):
    return f"Selected route: {route}"


SCHEMA = Schema(
    id="travel_unique_direct_route_select",
    tool_names=('report_direct_route_choice', 'identify_selected_route', 'return_selected_route', 'state_route_choice', 'show_selected_route', 'report_route_choice', 'name_selected_route', 'display_route_choice', 'present_selected_route', 'provide_selected_route'),
    descriptions=('Report the supplied selected route name.', 'Return a selected route without booking it.', 'State the chosen route by name.', 'Present the provided route selection.', 'Identify a route already selected by name.', 'Show the supplied route choice.', 'Return the name of a chosen route.', 'Report a route selection without reservation.', 'Display the provided selected route name.', 'Provide the chosen route name.'),
    parameters=(Parameter(names=("route", "route_name")),),
    tasks=(Task(id="direct", prompts=("Select the direct route from {routes}. Entries are route=transfer count; direct means zero transfers.", "Which route in {routes} is direct? Each entry gives its transfer count, and a direct route has no transfers.", 'Report the zero-transfer route in {routes}, where entries are route=transfer count.', 'From the route=transfer count list {routes}, select the direct route, meaning zero transfers.', 'Which name in {routes} has no transfers? Entries pair route with transfer count; select it.', 'Choose the direct option from {routes}: each entry is route=transfer count and direct means zero.', 'In {routes}, find and report the route whose transfer count is zero; entries are route=count.', 'Identify the direct route among {routes}; route=transfer count, and zero transfers defines direct.', 'Using {routes} as route=transfer count, select the route with no transfers.', 'The routes and transfer counts are {routes}. Report the one that is direct (zero transfers).', 'Find the zero in the route=transfer count entries {routes} and select its route.', 'Select the route without transfers from {routes}; the entries map route names to transfer counts.'), answers=("{result}.", "The choice is {result}."), cases=cases),),
)
