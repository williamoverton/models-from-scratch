from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 4)
        statuses = ["blocked", "eligible", "eligible", "blocked"]
        rng.shuffle(statuses)
        yield {"queue": "; ".join(f"P-{patron}={status}" for patron, status in zip(ids, statuses))}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["queue"].split(";")]
    patron = next(patron for patron, status in entries if status == "eligible")
    return Decision(fields=case, arguments={"patron": patron})


def resolve(patron):
    return f"Hold assigned to {patron}"


SCHEMA = Schema(
    id="library_hold_queue",
    tool_names=("assign_library_hold", "allocate_hold_to_patron", "assign_hold_to_patron", "allocate_library_hold", "record_hold_assignment", "assign_available_hold", "allocate_available_hold", "assign_selected_patron_hold", "record_patron_hold_allocation", "assign_hold_by_patron_id"),
    descriptions=("Assign the available hold to the specified patron ID.", "Allocate a hold to a supplied patron.", "Record assignment of the available library hold to the selected patron.", "Assign the hold to the patron identified by the supplied ID.", "Allocate the available hold to a specified library patron.", "Record a hold allocation for the selected patron ID.", "Assign a library hold to the given patron.", "Allocate the hold using the chosen patron identifier.", "Record that the available hold is assigned to the specified patron.", "Assign the selected patron to the available library hold."),
    parameters=(Parameter(names=("patron", "patron_id")),),
    tasks=(Task(id="assign", prompts=("Assign the available hold to the first eligible patron in this queue, listed front to back. Skip blocked patrons. Entries are patron=status: {queue}.", "Queue order is front to back: {queue} (patron=status). Assign the hold to the earliest eligible patron, skipping blocked entries.", "The queue {queue} runs front to back with entries patron=status. Skip blocked patrons and assign the available hold to the first eligible one.", "Who should receive the available hold? In {queue}, patron=status entries run front to back; skip blocked patrons and assign it to the first eligible patron.", "Read {queue} from front to back, where entries are patron=status. Assign the hold to the earliest eligible patron, passing over blocked patrons.", "Allocate the available hold using queue {queue} (patron=status, front to back): skip blocked entries and choose the first eligible patron.", "In this front-to-back queue {queue}, entries are patron=status. Bypass blocked patrons and assign the hold to the first eligible one.", "Assign the available hold to the earliest eligible patron in {queue}; the patron=status list is ordered front to back, and blocked patrons are skipped.", "Starting at the front of {queue}, find the first eligible patron and assign the hold. Entries are patron=status, ordered front to back; skip blocked patrons.", "The hold queue is {queue}, listed front to back as patron=status. Skip anyone blocked and allocate the available hold to the first eligible patron.", "Use {queue} to assign the available hold: entries are patron=status in front-to-back order, and blocked patrons must be skipped before choosing the first eligible one.", "From the front-to-back patron=status queue {queue}, assign the hold to the first eligible patron rather than any blocked patron."), answers=("{result}.", "{result}."), cases=cases),),
)
