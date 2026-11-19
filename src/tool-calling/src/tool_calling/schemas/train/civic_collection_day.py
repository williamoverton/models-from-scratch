from ...schema_types import Decision, Parameter, Schema, Task


DAYS = {"North": "Monday", "East": "Tuesday", "South": "Thursday", "West": "Friday"}


def cases(rng, count):
    for _ in range(count):
        yield {"zone": rng.choice(tuple(DAYS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(zone):
    return DAYS[zone]


SCHEMA = Schema(
    id="civic_collection_day",
    tool_names=("lookup_collection_day", "get_zone_collection_day", "find_sample_collection_weekday", "query_zone_collection_schedule", "resolve_zone_collection_day", "get_sample_zone_pickup_day", "lookup_weekly_zone_collection", "find_collection_day_by_zone", "read_sample_collection_schedule", "retrieve_zone_collection_weekday"),
    descriptions=("Look up the sample weekly collection day by zone.", "Find the sample collection weekday for a zone.", "Return the weekday mapped to the zone in the sample schedule.", "Query the fixed sample collection schedule by zone.", "Find the weekly collection day for the specified sample zone.", "Resolve a collection zone to its scheduled sample weekday.", "Retrieve a zone's collection day from the sample table.", "Look up the weekday assigned to the given collection zone.", "Identify the scheduled sample collection day for a zone.", "Find the zone's weekday in the sample weekly collection mapping."),
    parameters=(Parameter(names=("zone", "collection_zone")),),
    tasks=(Task(id="day", prompts=('Weekly collection schedule: North Monday, East Tuesday, South Thursday, West Friday. What is the collection day for {zone}?', 'Which weekday is collection in {zone}? Schedule: North Monday; East Tuesday; South Thursday; West Friday.', 'For {zone}, find the collection weekday using the sample schedule: North on Monday, East on Tuesday, South on Thursday, West on Friday.', 'The sample assigns Monday to North, Tuesday to East, Thursday to South, and Friday to West. When is collection in {zone}?', 'A resident lives in {zone}. Consult the weekly schedule—North Monday, East Tuesday, South Thursday, West Friday—and give their collection day.', 'Identify the day for {zone}: West collects Friday, South Thursday, East Tuesday, and North Monday in the sample schedule.', 'Collection lookup for {zone}: North/Monday, East/Tuesday, South/Thursday, West/Friday. Return the weekday.', 'On the sample route, North is serviced Monday and East Tuesday; South is serviced Thursday and West Friday. Which day belongs to {zone}?', 'What day should {zone} expect collection? Use the weekly assignments North = Monday, East = Tuesday, South = Thursday, West = Friday.', 'Match the zone {zone} to its scheduled weekday: Monday for North, Tuesday for East, Thursday for South, Friday for West.', 'The weekly sample has Friday pickups in West, Thursday in South, Tuesday in East, and Monday in North. Name the collection day for {zone}.', 'Using North: Monday; East: Tuesday; South: Thursday; West: Friday, determine the collection weekday associated with {zone}.', 'A collection schedule lists North on Monday, East on Tuesday, South on Thursday, and West on Friday. Retrieve the day assigned to {zone}.', 'Which weekday corresponds to {zone} in this sample: West Friday, North Monday, South Thursday, East Tuesday?'), answers=("Collection is on {result}.", "{result}."), cases=cases),)
)
