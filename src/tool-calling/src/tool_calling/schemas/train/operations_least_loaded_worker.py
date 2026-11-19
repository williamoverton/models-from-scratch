from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        workers = rng.sample(("W101", "W102", "W103", "W104", "W105", "W106"), 3)
        loads = rng.sample(range(0, 100), 3)
        rows = list(zip(workers, loads))
        yield {"rows": rows, "workers": "; ".join(f"{worker}: {load} jobs" for worker, load in rows)}


def prepare(*, task_id, case):
    worker = min(case["rows"], key=lambda row: row[1])[0]
    return Decision(fields=case, arguments={"worker": worker})


def resolve(worker):
    return f"Selected worker: {worker}."


SCHEMA = Schema(
    id="operations_least_loaded_worker",
    tool_names=("select_worker", "choose_least_loaded_worker", "record_worker_selection", "choose_worker_by_id", "select_worker_by_id", "register_selected_worker", "mark_selected_worker", "set_worker_selection", "submit_worker_selection", "identify_selected_worker"),
    descriptions=("Select a worker by ID.", "Record the selected worker.", "Register the specified worker as selected.", "Mark the given worker ID as the selection.", "Submit a selection for the specified worker.", "Record which worker was chosen by ID.", "Set the selected worker to the provided ID.", "Identify the chosen worker by its ID.", "Register a worker selection using its ID.", "Return confirmation of the specified worker selection."),
    parameters=(Parameter(names=("worker", "worker_id")),),
    tasks=(Task(id="worker", prompts=("Select the worker with the fewest jobs: {workers}.", "Choose the least loaded worker, where load is job count: {workers}.", "From {workers}, select the worker handling the fewest jobs.", "Which worker has the smallest job count? Select them from: {workers}.", "Record the worker with the lowest number of jobs: {workers}.", "Pick the least busy worker by job count from {workers}.", "Given these job counts, choose the worker with the minimum load: {workers}.", "Identify and select the worker assigned the fewest jobs in {workers}.", "Workers and job counts: {workers}. Register the least loaded worker.", "Please choose the worker with the lowest job count among {workers}.", "Select the worker carrying the smallest number of jobs: {workers}.", "Compare the job counts in {workers} and record the least loaded worker."), answers=("{result}", "{result}"), cases=cases),),
)
