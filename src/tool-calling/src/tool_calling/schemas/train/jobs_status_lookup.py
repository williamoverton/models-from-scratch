from ...schema_types import Decision, Parameter, Schema, Task


STATUSES = {'J-101': 'queued', 'J-102': 'running', 'J-103': 'failed', 'J-104': 'completed', 'J-105': 'running', 'J-106': 'failed'}


def cases(rng, count):
    for _ in range(count):
        yield {'job': rng.choice(tuple(STATUSES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(job):
    return f'{job}: {STATUSES[job]}'


SCHEMA = Schema(
    id='jobs_status_lookup',
    tool_names=('lookup_job_status', 'get_job_status', 'find_sample_job_status', 'query_job_status', 'read_job_status', 'retrieve_job_status', 'check_sample_job_status', 'lookup_status_by_job_id', 'get_registry_job_status', 'query_sample_job_registry'),
    descriptions=('Look up a job status in the sample registry.', 'Find a sample job status by ID.', 'Return the status of a job in the fixed sample registry.', 'Query the sample registry for the specified job ID.', 'Retrieve a sample job status using its identifier.', 'Read the registered status of a sample job.', 'Check the fixed sample registry for a job status.', 'Get the status associated with the supplied sample job ID.', 'Find the status of the identified job in the sample registry.', 'Report a job status from the fixed sample registry.'),
    parameters=(Parameter(names=('job', 'job_id')),),
    tasks=(Task(id='status', prompts=('What is the status of job {job} in the sample registry?', 'Look up sample job {job} and report its status.', 'Find the registered status of {job} in the sample job registry.', 'In the sample registry, which status is recorded for job {job}?', 'Retrieve the sample registry entry showing the status of job {job}.', 'For job {job}, give me its status from the sample registry.', 'How is job {job} currently listed in the sample registry?', 'Check the sample job registry for the status associated with {job}.', 'Report the status recorded against {job} in the sample registry.', 'According to the sample registry, what state is job {job} in?', 'Consult the sample registry and identify the status of job {job}.', 'I need the sample registry status for the job identified as {job}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
