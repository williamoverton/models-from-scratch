from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = [f'S-{ident}' for ident in rng.sample(range(100, 1000), 4)]
        complete, runnable, blocked, waiting = ids
        entries = [(complete, 'completed', 'none'), (runnable, 'pending', complete), (blocked, 'pending', waiting), (waiting, 'running', 'none')]
        rng.shuffle(entries)
        yield {'steps': '; '.join(f'{ident} {status} {dependency}' for ident, status, dependency in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['steps'].split('; ')]
    completed = {ident for ident, status, _ in entries if status == 'completed'}
    step = next(ident for ident, status, dependency in entries if status == 'pending' and (dependency == 'none' or dependency in completed))
    return Decision(fields=case, arguments={'step': step})


def resolve(step):
    return f'Started step {step}'


SCHEMA = Schema(
    id='jobs_start_next_runnable_step',
    tool_names=('start_job_step', 'run_job_step', 'simulate_step_start', 'start_step_by_id', 'simulate_job_step', 'run_selected_step', 'start_selected_step', 'simulate_running_step', 'launch_job_step', 'simulate_step_launch'),
    descriptions=('Simulate starting the supplied step ID.', 'Start a job step by ID in the simulation.', 'Simulate launching the specified job step.', 'Run the selected step by ID in the simulation.', 'Start the supplied step in the simulation.', 'Simulate running a job step identified by ID.', 'Launch the given step ID in the simulation.', 'Simulate starting the selected job step.', 'Start the caller-specified step by ID in the simulation.', 'Run the specified job step as a simulation.'),
    parameters=(Parameter(names=('step', 'step_id')),),
    tasks=(Task(id='start', prompts=('Start the unique runnable step: {steps}. Entries are ID, status, dependency ID (or none). A step is runnable only if pending and its dependency is completed or none.', 'Steps are {steps}, as ID, status, dependency ID or none. Start the only pending step whose dependency is completed or absent.', 'Simulate starting the runnable step in {steps}. Entries give ID, status and dependency ID or none; runnable means pending with a completed or absent dependency.', 'Among {steps}, start the sole runnable step in the simulation. Each entry is ID, status, dependency ID or none; it must be pending and its dependency completed or absent.', 'The steps {steps} are listed as ID, status, dependency ID or none. Simulate starting the pending step with no dependency or a completed one.', 'Identify and simulate starting the only runnable step in {steps}: each entry gives ID, status, dependency ID or none, and runnable requires pending status plus a completed or absent dependency.', 'Which step can run? In {steps}, entries are ID, status, dependency ID or none. Simulate starting the pending step whose dependency is completed or none.', 'Using {steps} (ID, status, dependency ID or none), simulate a start for the step that is pending and has either no dependency or a completed dependency.', 'Simulate launching the unique pending step in {steps} whose dependency is completed or none. Records give ID, status and dependency ID or none.', 'From the step list {steps}, simulate starting the runnable step: entries specify ID, status and dependency ID or none, and a runnable step is pending with its dependency completed or absent.', 'Select and simulate starting the step in {steps} that is pending and whose dependency is none or completed. The entry fields are ID, status, dependency ID or none.', 'Given {steps} as ID, status and dependency ID or none, simulate starting the sole step that is pending and has no dependency or a completed dependency.'), answers=('{result}.', '{result}.'), cases=cases),),
)
