from ...schema_types import Decision, Schema, Parameter, Task


ROUTES = {
    ("Harbor", "Museum"): "Blue line",
    ("Museum", "Harbor"): "Blue line",
    ("Airport", "Central"): "Express line",
    ("Central", "Airport"): "Express line",
    ("Central", "Park"): "Green line",
    ("Park", "Central"): "Green line",
    ("Harbor", "Airport"): "Coastal line",
    ("Airport", "Harbor"): "Coastal line",
}


def cases(rng, count):
    for _ in range(count):
        origin, destination = rng.choice(tuple(ROUTES))
        yield {"origin": origin, "destination": destination}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="travel_route_lookup",
    tool_names=('lookup_route', 'find_transit_line', 'lookup_direct_line', 'get_sample_route', 'find_sample_line', 'lookup_station_route', 'get_direct_route', 'find_direct_transit_line', 'retrieve_station_line', 'lookup_sample_transit_route'),
    descriptions=('Look up a direct line in the sample network by origin and destination.', 'Find the sample direct route between two stations.', 'Retrieve the sample line connecting the specified stations.', 'Return the sample direct line for an origin and destination.', 'Look up the sample transit route between two stations.', 'Find the direct line for a sample station pair.', 'Get the sample route connecting an origin to a destination.', 'Retrieve a direct transit line from the sample network.', 'Find the sample line for the supplied station pair.', 'Look up the direct sample route by departure and arrival station.'),
    parameters=(Parameter(names=("origin", "from_station")), Parameter(names=("destination", "to_station"))),
    tasks=(Task(id="route", prompts=("Which direct line goes from {origin} to {destination} in the sample network?", "Find the sample transit route from {origin} to {destination}.", 'In the sample network, identify the direct line connecting {origin} to {destination}.', 'Look up the sample direct line from {origin} to {destination}.', 'For a trip from {origin} to {destination}, which direct line does the sample network list?', 'Find the line serving {origin} to {destination} directly in the sample network.', 'What sample network line connects {origin} and {destination} directly?', 'Give the sample direct transit line for origin {origin} and destination {destination}.', 'Consult the sample network: which direct line runs from {origin} to {destination}?', 'Identify the sample route between {origin} and {destination}.', 'Using the sample transit network, retrieve the direct route from {origin} to {destination}.', 'From {origin} to {destination}, name the direct line in the sample network.'), answers=("The route is {result}.", "Take the {result}."), cases=cases),),
)


def resolve(origin, destination):
    return ROUTES[origin, destination]
