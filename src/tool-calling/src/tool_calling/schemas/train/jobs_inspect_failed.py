from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 1000), 3)
        entries = list(zip(ids, ('failed', 'running', 'completed')))
        rng.shuffle(entries)
        yield {'jobs': '; '.join(f'J-{ident} {status}' for ident, status in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['jobs'].split('; ')]
    job = next(ident for ident, status in entries if status == 'failed')
    return Decision(fields=case, arguments={'job': job})


def resolve(job):
    return f'Inspected job {job}'


SCHEMA = Schema(
    id='jobs_inspect_failed',
    tool_names=('inspect_job', 'inspect_failed_job', 'simulate_job_inspection', 'inspect_job_by_id', 'inspect_selected_job', 'simulate_inspect_job', 'review_job_in_simulation', 'simulate_job_review', 'inspect_identified_job', 'simulate_inspection_by_id'),
    descriptions=('Simulate inspection of the supplied job ID.', 'Inspect a job by ID in the simulation.', 'Simulate inspecting the specified job.', 'Inspect the selected job by ID in the simulation.', 'Simulate a review of the supplied job.', 'Inspect the given job identifier in the simulation.', 'Simulate inspection of the selected job ID.', 'Review the job identified by the caller in the simulation.', 'Simulate inspecting a job using its ID.', 'Inspect the specified job as a simulation.'),
    parameters=(Parameter(names=('job', 'job_id')),),
    tasks=(Task(id='inspect', prompts=('Inspect the only failed job: {jobs}. Entries are ID and status.', 'From {jobs}, inspect the job whose status is failed; entries are ID and status.', 'The jobs are {jobs}, each given as ID and status. Inspect the one marked failed.', 'Which job failed? Inspect it from this ID-and-status list: {jobs}.', 'Find and inspect the unique failed job among {jobs}; each entry contains its ID and status.', 'Inspect the failed entry in {jobs}, where each job is listed by ID and status.', 'Given job IDs and statuses {jobs}, inspect the one whose status is failed.', 'In the list {jobs} (ID and status), identify the failed job and inspect it.', 'Review the one failed job in {jobs}; the entries give job ID and status.', 'The following entries specify job ID and status: {jobs}. Inspect the only job in failed status.', 'From the ID-and-status entries {jobs}, select the failed job for inspection.', 'Inspect whichever job is marked failed in {jobs}; entries consist of ID and status.'), answers=('{result}.', '{result}.'), cases=cases),),
)
