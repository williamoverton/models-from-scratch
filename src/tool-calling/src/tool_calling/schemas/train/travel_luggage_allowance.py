from ...schema_types import Decision, Parameter, Schema, Task


ALLOWANCES = {"Saver": "1 cabin bag, 7 kg", "Standard": "1 cabin bag, 10 kg and 1 checked bag, 20 kg", "Flex": "1 cabin bag, 10 kg and 2 checked bags, 23 kg each", "Basic": "1 personal item, 5 kg"}


def cases(rng, count):
    for _ in range(count):
        yield {"fare": rng.choice(tuple(ALLOWANCES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(fare):
    return f"{fare}: {ALLOWANCES[fare]}"


SCHEMA = Schema(
    id="travel_luggage_allowance_lookup",
    tool_names=('get_luggage_allowance', 'lookup_fare_baggage', 'lookup_luggage_allowance', 'get_fare_baggage', 'find_fare_allowance', 'retrieve_baggage_allowance', 'check_fare_luggage', 'show_fare_allowance', 'get_sample_baggage', 'lookup_sample_luggage'),
    descriptions=('Look up luggage allowance for a fare in the sample registry.', 'Retrieve the sample baggage allowance for a named fare.', 'Find the sample fare’s permitted baggage.', 'Return the luggage allowance associated with a sample fare.', 'Check the sample registry for a fare’s baggage allowance.', 'Show baggage limits recorded for a sample fare.', 'Get the sample luggage allowance by fare name.', 'Look up a named fare’s sample baggage limits.', 'Retrieve baggage details for a sample fare.', 'Report the sample registry allowance for a given fare.'),
    parameters=(Parameter(names=("fare", "fare_name")),),
    tasks=(Task(id="allowance", prompts=("What is the sample luggage allowance for the {fare} fare?", "Look up the baggage allowance for the sample {fare} fare.", 'Find the baggage limits listed for fare {fare} in the sample registry.', 'For the sample fare {fare}, what luggage is permitted?', 'Retrieve the sample registry baggage allowance associated with {fare}.', 'How much luggage does the sample {fare} fare allow?', 'Show the sample baggage allowance for fare {fare}.', 'Consult the sample fare registry and report the luggage allowance for {fare}.', 'Which baggage allowance applies to the sample {fare} fare?', 'Give the luggage limits recorded for {fare} in the sample registry.', 'What baggage does the sample registry specify for {fare}?', 'Identify the allowance for luggage under the sample fare named {fare}.'), answers=("The allowance is {result}.", "Sample registry: {result}."), cases=cases),),
)
