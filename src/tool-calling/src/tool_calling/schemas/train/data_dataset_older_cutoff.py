from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        cutoff = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 999), 3)
        offsets = [rng.randint(-90, -1), 0, rng.randint(1, 90)]
        rng.shuffle(offsets)
        entries = list(zip(ids, offsets))
        rng.shuffle(entries)
        yield {"cutoff": cutoff.isoformat(), "datasets": "; ".join(f"DS-{identifier}={(cutoff + timedelta(days=offset)).isoformat()}" for identifier, offset in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["datasets"].split(";")]
    dataset = next(identifier for identifier, created in entries if created < case["cutoff"])
    return Decision(fields=case, arguments={"dataset": dataset})


def resolve(dataset):
    return f"Flagged dataset {dataset}"


SCHEMA = Schema(
    id="data_dataset_older_cutoff_flag",
    tool_names=('flag_sample_dataset', 'mark_dataset_for_review', 'flag_dataset_for_review', 'mark_dataset_review', 'flag_dataset_id', 'submit_dataset_flag', 'record_dataset_review_flag', 'request_dataset_review', 'identify_dataset_for_review', 'add_dataset_review_flag'),
    descriptions=('Flag the specified dataset for review.', 'Record a dataset flag.', 'Flag the given dataset ID for review.', 'Mark the specified dataset for a review.', 'Record a review flag for the supplied dataset.', 'Submit the chosen dataset identifier as flagged.', 'Register a flag against the named dataset.', 'Request review of the specified dataset by ID.', 'Identify the provided dataset for review.', 'Add a review flag for the given dataset ID.'),
    parameters=(Parameter(names=("dataset", "dataset_id")),),
    tasks=(Task(id="flag", prompts=("Flag the dataset created strictly before {cutoff}. Entries are ID=creation date: {datasets}.", "From {datasets} (ID=creation date), flag the dataset older than {cutoff}; a date equal to the cutoff does not qualify.", "Flag the dataset with a creation date earlier than {cutoff}, not equal to it; ID=date entries: {datasets}.", "Given {datasets} as dataset ID=creation date, flag the one created strictly before {cutoff}.", "Which dataset should be flagged? Its creation date must precede {cutoff}; {datasets} lists ID=date.", "Review {datasets} (ID=creation date) and flag the dataset created before, but not on, {cutoff}.", "Using creation dates in {datasets} (ID=date), flag the dataset older than the exclusive cutoff {cutoff}.", "Find and flag the dataset created prior to {cutoff}; equality is excluded. Dataset ID=creation date: {datasets}.", "Please flag the dataset whose creation date is strictly less than {cutoff}, from ID=date entries {datasets}.", "From the dataset creation dates {datasets} (ID=date), flag the one before {cutoff}; the cutoff itself does not count.", "Identify and flag the dataset predating {cutoff} in {datasets}, where entries are ID=creation date and equality is excluded.", "The cutoff is {cutoff}; flag the dataset created earlier, not on that date, using {datasets} (ID=creation date)."), answers=("{result}.", "{result}."), cases=cases),),
)
