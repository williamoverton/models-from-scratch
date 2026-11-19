from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"zone": rng.choice(tuple("ABCDEFGHIJ")), "rider": rng.choice(("adult", "child", "student", "senior"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="transit_fare",
    tool_names=('transit_fare', 'fare_lookup', 'lookup_sample_transit_fare', 'get_sample_ticket_price', 'calculate_sample_fare', 'find_zone_rider_fare', 'sample_transit_ticket_price', 'get_zone_passenger_fare', 'compute_sample_ticket_fare', 'lookup_zone_fare'),
    descriptions=('Look up a fixed sample transit fare by zone and passenger category.', 'Return the sample ticket price for a zone and rider type.', 'Calculate the sample transit fare for a travel zone and rider category.', 'Find the sample ticket fare for the specified zone and passenger type.', 'Get the fixed sample fare for a zone and rider category.', 'Compute the sample price of a transit ticket from zone and rider type.', 'Look up a sample transit ticket price using zone and passenger category.', 'Determine the sample fare for the given travel zone and rider.', 'Return the fixed sample zone fare adjusted for the passenger category.', 'Find a sample transit ticket price by zone and rider type.'),
    parameters=(
        Parameter(names=("zone", "travel_zone")),
        Parameter(names=("rider", "passenger")),
    ),
    tasks=(Task(id="fare", prompts=("What is the {rider} fare for zone {zone}?", "Find a zone {zone} ticket price for the {rider} rider.", 'Look up the sample fare for a {rider} travelling in zone {zone}.', 'How much is a sample zone {zone} ticket for a {rider}?', 'Give the sample transit ticket price for rider type {rider} in zone {zone}.', 'Calculate the sample fare for zone {zone} and passenger category {rider}.', 'For a {rider} in zone {zone}, find the sample ticket cost.', 'What sample transit price applies to a {rider} in zone {zone}?', 'Determine the sample zone {zone} fare for a {rider} passenger.', 'A {rider} travels in zone {zone}; what is the sample fare?', 'Find the sample fare associated with zone {zone} and rider {rider}.', 'Report the sample ticket price for a {rider} riding in zone {zone}.'), answers=("The fare is {result}.", "The {rider} ticket costs {result}."), cases=cases),),
)


def resolve(zone, rider):
    cents = {"A": 200, "B": 300, "C": 400, "D": 500, "E": 600, "F": 700, "G": 800, "H": 900, "I": 1000, "J": 1100}[zone]
    cents = cents * {"adult": 100, "child": 50, "student": 75, "senior": 60}[rider] // 100
    return f"${cents // 100}.{cents % 100:02d}"
