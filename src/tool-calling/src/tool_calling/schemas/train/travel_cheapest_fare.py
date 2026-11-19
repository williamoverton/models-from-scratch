from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("Amber", "Birch", "Cedar", "Delta", "Elm", "Fjord"), 3)
        if rng.choice((True, False)):
            lowest = rng.randint(5, 79)
            prices = [lowest, lowest, rng.randint(lowest + 1, 80)]
        else:
            prices = rng.sample(range(5, 81), 3)
        offers = list(zip(names, prices))
        rng.shuffle(offers)
        yield {"fares": ", ".join(f"{name}=${price}" for name, price in offers)}


def prepare(*, task_id, case):
    offers = (entry.strip().split("=$") for entry in case["fares"].split(","))
    name, _ = min(((name, int(price)) for name, price in offers), key=lambda item: (item[1], item[0]))
    return Decision(fields=case, arguments={"fare": name})


SCHEMA = Schema(
    id="travel_cheapest_fare",
    tool_names=('report_selected_fare', 'identify_fare', 'return_selected_fare', 'state_fare_choice', 'show_selected_fare', 'report_fare_choice', 'name_selected_fare', 'display_fare_choice', 'present_selected_fare', 'provide_selected_fare'),
    descriptions=('Report the supplied selected fare name.', 'Return a selected fare name without booking.', 'State the chosen fare by name.', 'Present the provided fare selection.', 'Identify the fare already selected by name.', 'Show the supplied fare choice.', 'Return the name of a chosen fare.', 'Report a fare selection without purchasing it.', 'Display the provided selected fare name.', 'Provide the chosen fare name without making a reservation.'),
    parameters=(Parameter(names=("fare", "fare_name")),),
    tasks=(Task(id="cheapest", prompts=("The listed fares are {fares}. Select the cheapest fare; break any price ties alphabetically by name.", "Choose the least expensive fare from {fares}; if tied, choose the alphabetically first name.", 'From {fares}, report the lowest-priced fare name; resolve price ties alphabetically by name.', 'Which fare in {fares} costs least? Select the alphabetically first name if prices tie.', 'Compare the named prices {fares} and choose the cheapest, breaking ties by alphabetical name.', 'Select a fare from {fares} with minimum price; tied names are ordered alphabetically.', 'For the offers {fares}, identify the least expensive fare, choosing alphabetically first among ties.', 'Find the cheapest name in {fares}; use alphabetical order to decide any price tie.', 'Report the fare name with the lowest price in {fares}, or the alphabetically first if tied.', 'Among {fares}, choose by price first and alphabetical fare name second.', 'Which named offer is cheapest in {fares}? If multiple share that price, select the first alphabetically.', 'Rank the fares {fares} by price then name alphabetically and select the first name.'), answers=("The selected fare is {result}.", "Choose {result}."), cases=cases),),
)


def resolve(fare):
    return fare
