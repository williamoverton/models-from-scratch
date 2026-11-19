from ...schema_types import Decision, Schema, Parameter, Task


def clock(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randrange(6 * 60, 20 * 60, 5)
        departures = rng.sample(range(6 * 60, 23 * 60, 5), 3)
        if not any(time > threshold for time in departures):
            departures[0] = threshold + 5
        rng.shuffle(departures)
        yield {"after": clock(threshold), "departures": ", ".join(clock(time) for time in departures)}


def prepare(*, task_id, case):
    eligible = (time.strip() for time in case["departures"].split(",") if time.strip() > case["after"])
    return Decision(fields=case, arguments={"departure": min(eligible)})


SCHEMA = Schema(
    id="travel_earliest_departure",
    tool_names=('report_selected_departure', 'identify_departure', 'return_selected_departure', 'state_departure_choice', 'show_selected_departure', 'report_departure_choice', 'present_selected_departure', 'display_departure_choice', 'provide_selected_departure', 'name_selected_departure'),
    descriptions=('Report the supplied selected departure time.', 'Return a selected departure time without booking.', 'State the chosen departure time.', 'Present the provided departure selection.', 'Identify the departure already selected by time.', 'Show the supplied departure choice.', 'Return the time of a chosen departure.', 'Report a departure selection without making a booking.', 'Display the provided selected departure time.', 'Provide the chosen departure time.'),
    parameters=(Parameter(names=("departure", "departure_time")),),
    tasks=(Task(id="departure", prompts=("Departures are {departures}. Select the earliest strictly after {after}.", "From {departures}, choose the first departure later than {after}; a departure at {after} does not count.", 'Which departure in {departures} is earliest strictly later than {after}? Select it.', 'Pick the first time after {after} from {departures}; a time equal to {after} is excluded.', 'From the listed departures {departures}, report the earliest one that is later than {after}.', 'Find the minimum departure strictly beyond {after} among {departures}.', 'Select the earliest eligible time in {departures}, where eligibility means strictly after {after}.', 'Given {departures}, choose the earliest departure after {after}, not at {after}.', 'The cutoff is {after}, exclusive. Which time in {departures} is the earliest qualifying departure?', 'Identify the first departure later than {after} in {departures}; equality is not allowed.', 'Report the earliest time from {departures} that exceeds {after}.', 'Filter departures {departures} to those strictly after {after} and select the earliest.'), answers=("The selected departure is {result}.", "Choose the {result} departure."), cases=cases),),
)


def resolve(departure):
    return departure
