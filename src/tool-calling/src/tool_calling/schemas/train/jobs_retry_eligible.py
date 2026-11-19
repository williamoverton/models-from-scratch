from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 1000), 3)
        limit = rng.randint(1, 5)
        entries = [(ids[0], 'failed', rng.randrange(limit)), (ids[1], 'failed', rng.randint(limit, limit + 3)), (ids[2], 'completed', rng.randrange(limit))]
        rng.shuffle(entries)
        yield {'jobs': '; '.join(f'J-{ident} {status} {retries}' for ident, status, retries in entries), 'limit': str(limit)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['jobs'].split('; ')]
    job = next(ident for ident, status, retries in entries if status == 'failed' and int(retries) < int(case['limit']))
    return Decision(fields=case, arguments={'job': job})


def resolve(job):
    return f'Retry requested for job {job}'


SCHEMA = Schema(
    id='jobs_retry_eligible_by_count',
    tool_names=('retry_job', 'request_job_retry', 'simulate_job_retry', 'retry_job_by_id', 'submit_simulated_retry', 'request_retry_by_id', 'simulate_retry_request', 'retry_selected_job', 'request_selected_job_retry', 'simulate_retry_job'),
    descriptions=('Simulate retrying the supplied job ID.', 'Request a simulated retry for a job.', 'Simulate a retry request for the specified job.', 'Request a retry for the given job ID in the simulation.', 'Retry the selected job by ID in the simulation.', 'Submit a simulated retry for the supplied job.', 'Simulate requesting another attempt for the identified job.', 'Issue a simulated retry request for the selected job ID.', 'Request that the specified job be retried in the simulation.', 'Simulate retrying the job identified by the caller.'),
    parameters=(Parameter(names=('job', 'job_id')),),
    tasks=(Task(id='retry', prompts=('Retry the only eligible job: {jobs}. Entries are ID, status, retries already attempted. Eligible means failed with fewer than {limit} retries.', 'Jobs: {jobs} (ID, status, retry count). Simulate retrying the unique failed job with a retry count strictly below {limit}.', 'Simulate a retry for the only eligible job in {jobs}. Entries are ID, status, retries already attempted; eligibility requires failed status and fewer than {limit} retries.', 'From {jobs}, select the failed job with fewer than {limit} retries already attempted and simulate retrying it. Entries list ID, status and retry count.', 'The job list {jobs} contains ID, status and retries attempted. Simulate a retry for the unique failed job below the {limit}-retry threshold.', 'Which job in {jobs} is failed and has attempted strictly fewer than {limit} retries? Simulate retrying it; entries are ID, status, retry count.', 'Apply the retry rule to {jobs} (ID, status, retries already attempted): a job must be failed and have fewer than {limit} retries. Simulate the eligible retry.', 'Simulate retrying the eligible job from {jobs}; each entry gives ID, status, and retries attempted, and only failed jobs with counts below {limit} qualify.', 'With retry limit {limit}, find the failed job in {jobs} whose retries attempted are strictly under the limit and simulate a retry. Entries are ID, status, retry count.', 'Request a simulated retry for the sole failed job with fewer than {limit} attempted retries in {jobs}, formatted ID, status, retry count.', 'Jobs are listed by ID, status and already-attempted retries: {jobs}. Simulate a retry for the one that failed and has a count less than {limit}.', 'Using {limit} as the exclusive retry-count limit, simulate retrying the failed eligible job in {jobs}; entries provide ID, status and retries already attempted.'), answers=('{result}.', '{result}.'), cases=cases),),
)
