from ...schema_types import Decision, Parameter, Schema, Task


LOCATIONS = {"P1": "Oak School", "P2": "River Hall", "P3": "Hill Library", "P4": "Pine Center"}


def cases(rng, count):
    for _ in range(count):
        yield {"precinct": rng.choice(tuple(LOCATIONS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(precinct):
    return LOCATIONS[precinct]


SCHEMA = Schema(
    id="civic_polling_location",
    tool_names=("lookup_polling_location", "find_precinct_polling_place", "get_sample_precinct_location", "lookup_precinct_voting_site", "find_sample_polling_place", "query_precinct_location", "resolve_precinct_polling_site", "get_polling_place_by_precinct", "find_precinct_voting_location", "lookup_sample_voting_place"),
    descriptions=("Look up the polling location for a precinct in the sample schedule.", "Find a sample precinct's polling place.", "Return the polling place assigned to the precinct in the sample mapping.", "Query the sample voting locations by precinct ID.", "Identify a precinct's polling location from the fixed sample table.", "Find the sample voting site for the supplied precinct.", "Resolve a precinct identifier to its sample polling place.", "Retrieve the polling location mapped to the specified precinct.", "Look up where a sample precinct votes.", "Find the precinct's location in the sample polling schedule."),
    parameters=(Parameter(names=("precinct", "precinct_id")),),
    tasks=(Task(id="location", prompts=('Sample polling places: P1 Oak School, P2 River Hall, P3 Hill Library, P4 Pine Center. Where does precinct {precinct} vote?', 'Find the polling place for {precinct}: P1=Oak School; P2=River Hall; P3=Hill Library; P4=Pine Center.', 'A voter belongs to {precinct}. Use the sample assignments P1 to Oak School, P2 to River Hall, P3 to Hill Library, and P4 to Pine Center to identify their polling place.', 'Which site serves {precinct}? The sample directory lists Oak School for P1, River Hall for P2, Hill Library for P3, and Pine Center for P4.', 'Locate precinct {precinct} in this sample: P4 votes at Pine Center, P3 at Hill Library, P2 at River Hall, and P1 at Oak School. Return its location.', 'For the sample precinct {precinct}, give the voting site. Assignments are P1: Oak School; P2: River Hall; P3: Hill Library; P4: Pine Center.', 'The sample places Oak School, River Hall, Hill Library, and Pine Center serve P1, P2, P3, and P4 respectively. Where should {precinct} vote?', 'Look up {precinct} in the sample polling directory: P1/Oak School, P2/River Hall, P3/Hill Library, P4/Pine Center. Name the assigned place.', 'Pine Center is the sample site for P4; Hill Library is for P3; River Hall is for P2; Oak School is for P1. Identify the site for {precinct}.', 'A polling-place lookup is needed for {precinct}. Use P1 = Oak School, P2 = River Hall, P3 = Hill Library, and P4 = Pine Center.', 'Match {precinct} with its sample location: Oak School (P1), River Hall (P2), Hill Library (P3), Pine Center (P4).', 'From the sample voting schedule—P1 at Oak School, P2 at River Hall, P3 at Hill Library, P4 at Pine Center—which location corresponds to {precinct}?', 'The precinct is {precinct}. The sample assigns P3 to Hill Library and P4 to Pine Center, while P1 goes to Oak School and P2 to River Hall. Give its polling place.', 'Return the sample polling location for {precinct}, using P4: Pine Center; P2: River Hall; P1: Oak School; P3: Hill Library.'), answers=("The location is {result}.", "Vote at {result}."), cases=cases),)
)
