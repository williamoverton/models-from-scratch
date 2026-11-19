from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 1000), 3)
        durations = rng.sample(range(1, 600), 3)
        entries = list(zip(ids, durations))
        rng.shuffle(entries)
        yield {'jobs': '; '.join(f'J-{ident} {minutes}' for ident, minutes in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['jobs'].split('; ')]
    job, _ = max(entries, key=lambda entry: int(entry[1]))
    return Decision(fields=case, arguments={'job': job})


def resolve(job):
    return f'Flagged job {job}'


SCHEMA = Schema(
    id='jobs_flag_longest_running',
    tool_names=('flag_job', 'mark_job', 'simulate_job_flag', 'flag_job_by_id', 'mark_selected_job', 'simulate_mark_job', 'flag_selected_job', 'mark_job_by_id', 'simulate_flag_job', 'tag_job_in_simulation'),
    descriptions=('Simulate flagging the supplied job ID.', 'Mark a job by ID in the simulation.', 'Simulate marking the specified job.', 'Flag the selected job by ID in the simulation.', 'Simulate applying a flag to the supplied job.', 'Mark the given job identifier in the simulation.', 'Simulate a flag for the selected job ID.', 'Flag the job identified by the caller in the simulation.', 'Simulate marking a job for attention by ID.', 'Apply a simulated flag to the specified job.'),
    parameters=(Parameter(names=('job', 'job_id')),),
    tasks=(Task(id='flag', prompts=('Flag the longest-running job: {jobs}. All are running; entries are ID and elapsed minutes.', 'The running jobs are {jobs}, listed as ID and elapsed minutes. Flag the job with the largest elapsed duration.', 'All these jobs are running: {jobs}. Entries give ID and elapsed minutes; flag the one running longest.', 'From {jobs}, flag the running job with the most elapsed minutes. Each entry is ID and elapsed minutes; all are running.', 'Compare elapsed minutes for the running jobs {jobs} (ID and elapsed minutes) and flag the longest-running one.', 'The entries {jobs} list ID and elapsed minutes for running jobs. Flag the job with the greatest duration.', 'Which of the running jobs {jobs} has run longest? Flag it; entries contain ID and elapsed minutes.', 'Flag the maximum-duration job in {jobs}. All jobs are running, and each entry gives ID and elapsed minutes.', 'Given running jobs {jobs}, expressed as ID and elapsed minutes, flag the job with the highest elapsed time.', 'Each entry in {jobs} is a running job ID and its elapsed minutes. Flag the one with the most minutes.', 'Find the longest elapsed duration among the running jobs {jobs} and flag its job; entries are ID and elapsed minutes.', 'The running-job list {jobs} contains ID and elapsed minutes. Flag the job that has been running the longest.'), answers=('{result}.', '{result}.'), cases=cases),),
)
