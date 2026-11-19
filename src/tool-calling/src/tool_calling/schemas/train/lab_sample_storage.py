from ...schema_types import Decision, Parameter, Schema, Task


LOCATIONS = {"S-101": "Freezer A, rack 1", "S-102": "Freezer B, rack 2", "S-103": "Refrigerator C, shelf 1", "S-104": "Freezer A, rack 3"}


def cases(rng, count):
    for _ in range(count):
        yield {"sample": rng.choice(tuple(LOCATIONS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(sample):
    return LOCATIONS[sample]


SCHEMA = Schema(
    id="lab_sample_storage",
    tool_names=("lookup_sample_storage", "find_sample_location", "get_sample_storage_location", "retrieve_sample_location", "lookup_sample_location_by_id", "find_recorded_sample_storage", "get_recorded_sample_location", "locate_lab_sample", "lookup_lab_sample_storage", "find_sample_storage_by_id"),
    descriptions=("Look up a sample's recorded storage location by sample ID.", "Find the recorded storage location for a sample.", "Retrieve the storage location associated with a sample ID.", "Locate a laboratory sample using its recorded ID.", "Get the recorded freezer or refrigerator location for a sample.", "Find where a specified lab sample is stored.", "Look up the storage record for a sample identifier.", "Return the recorded storage location of the selected sample.", "Retrieve a sample's recorded freezer rack or refrigerator shelf.", "Find the storage location corresponding to a laboratory sample ID."),
    parameters=(Parameter(names=("sample", "sample_id")),),
    tasks=(Task(id="location", prompts=("Recorded storage: S-101=Freezer A, rack 1; S-102=Freezer B, rack 2; S-103=Refrigerator C, shelf 1; S-104=Freezer A, rack 3. Where is sample {sample}?", "Find the recorded location of {sample}: S-101 Freezer A rack 1; S-102 Freezer B rack 2; S-103 Refrigerator C shelf 1; S-104 Freezer A rack 3.", "Where is {sample} stored? Records: S-101=Freezer A rack 1; S-102=Freezer B rack 2; S-103=Refrigerator C shelf 1; S-104=Freezer A rack 3.", "Locate sample {sample} using S-101=Freezer A rack 1, S-102=Freezer B rack 2, S-103=Refrigerator C shelf 1, and S-104=Freezer A rack 3.", "The storage records are S-101: Freezer A rack 1; S-102: Freezer B rack 2; S-103: Refrigerator C shelf 1; S-104: Freezer A rack 3. Give the location of {sample}.", "For sample {sample}, report its recorded storage: S-101 in Freezer A rack 1; S-102 in Freezer B rack 2; S-103 in Refrigerator C shelf 1; S-104 in Freezer A rack 3.", "Which location corresponds to {sample}? S-101 is Freezer A rack 1, S-102 is Freezer B rack 2, S-103 is Refrigerator C shelf 1, and S-104 is Freezer A rack 3.", "Look up {sample} in these storage mappings: S-101=Freezer A rack 1; S-102=Freezer B rack 2; S-103=Refrigerator C shelf 1; S-104=Freezer A rack 3.", "Sample locations: S-101 at Freezer A rack 1, S-102 at Freezer B rack 2, S-103 at Refrigerator C shelf 1, S-104 at Freezer A rack 3. Find {sample}.", "From S-101=Freezer A rack 1; S-102=Freezer B rack 2; S-103=Refrigerator C shelf 1; S-104=Freezer A rack 3, identify the storage location of {sample}.", "Give the freezer or refrigerator location for {sample} according to these records: S-101 Freezer A rack 1; S-102 Freezer B rack 2; S-103 Refrigerator C shelf 1; S-104 Freezer A rack 3.", "Using S-101 at Freezer A rack 1, S-102 at Freezer B rack 2, S-103 at Refrigerator C shelf 1, and S-104 at Freezer A rack 3, find where {sample} is stored."), answers=("The sample is at {result}.", "Recorded location: {result}."), cases=cases),),
)
