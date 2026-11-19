from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        species = rng.sample(("heron", "otter", "fox", "badger", "deer"), 3)
        locations = rng.sample(("Marsh", "North Wood", "Riverbank", "Meadow", "Pond"), 3)
        dates = rng.sample(tuple(f"2026-04-{day:02d}" for day in range(1, 29)), 3)
        records = "; ".join(f"{name}: {location}, {date}" for name, location, date in zip(species, locations, dates))
        yield {"species": rng.choice(species), "records": records}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(species, records):
    observations = dict(record.split(": ") for record in records.split("; "))
    return f"{species}: {observations[species]}"


SCHEMA = Schema(
    id="conservation_species_observation",
    tool_names=("lookup_species_observation", "get_observation_details", "find_species_sighting", "retrieve_species_observation", "query_observation_records", "find_recorded_species_location", "lookup_species_sighting_details", "get_species_observation_record", "resolve_species_observation", "find_species_observation_date"),
    descriptions=("Look up the location and date of a species observation.", "Find an observation's recorded location and date.", "Find the named species in the supplied records and return its location and date.", "Retrieve the recorded observation details for the specified species.", "Query the supplied species records for the matching location and date.", "Return the species and its recorded place and observation date.", "Look up a species in the provided observation list.", "Identify where and when the named species was observed from the records.", "Find the location and date associated with the specified species.", "Extract the matching species observation from the supplied records."),
    parameters=(Parameter(names=("species", "species_name")), Parameter(names=("records", "observations"))),
    tasks=(Task(id="lookup", prompts=('Find the location and date of the {species} observation: {records}.', 'Where and when was {species} observed? Records: {records}.', 'From the observation records {records}, retrieve the place and date associated with {species}.', 'The field log reads {records}. Look up {species} and give its observation location and date.', 'Using {records}, identify where and on what date the {species} was recorded.', 'Find the entry for {species} in {records}; report both its location and observation date.', 'An observation list contains {records}. What location and date does it record for {species}?', 'Locate the {species} sighting in these records: {records}. Return where and when it occurred.', 'For the species {species}, extract the recorded date and location from {records}.', 'Which place and date are paired with {species} in the observation log {records}?', 'Consult {records} for the {species} record and provide its observation location and date.', 'Report when and where {species} was seen, based on these observation records: {records}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
