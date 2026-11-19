from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        capacity = rng.randint(20, 1000)
        used = rng.randint(0, capacity)
        yield {"capacity": str(capacity), "used": str(used)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(capacity, used):
    return str(int(capacity) - int(used))


SCHEMA = Schema(
    id="operations_capacity_headroom",
    tool_names=("calculate_capacity_headroom", "compute_remaining_capacity", "subtract_used_capacity", "get_capacity_headroom", "calculate_unused_capacity", "compute_capacity_headroom", "find_remaining_capacity", "calculate_available_capacity", "compute_unused_capacity", "derive_remaining_capacity"),
    descriptions=("Subtract used capacity from total capacity.", "Calculate remaining capacity in units.", "Compute total capacity minus used capacity.", "Find the unused capacity from total and used units.", "Determine headroom by subtracting used units from total units.", "Calculate the number of capacity units remaining.", "Compute available capacity as total less used capacity.", "Return the difference between total and used capacity.", "Derive remaining units from capacity and usage.", "Find capacity headroom by subtracting usage from the total."),
    parameters=(Parameter(names=("capacity", "total_capacity")), Parameter(names=("used", "used_capacity"))),
    tasks=(Task(id="headroom", prompts=("Total capacity is {capacity} units and {used} are used. How many units of headroom remain?", "Calculate remaining capacity as total minus used: total {capacity}, used {used} units.", "How much capacity is left if {used} of {capacity} units are used?", "Find the unused units given total capacity {capacity} and usage {used}.", "Subtract {used} used units from the total capacity of {capacity}.", "What is the headroom in units for capacity {capacity} with {used} used?", "We have {capacity} units of capacity and use {used}; calculate the remainder.", "Determine available capacity: {capacity} total units, {used} used units.", "How many of the {capacity} capacity units remain after using {used}?", "Compute total minus used for {capacity} capacity units and {used} used units.", "Give me the remaining capacity when the total is {capacity} and usage is {used} units.", "What's the unused capacity in units if the total is {capacity} and {used} are already used?"), answers=("Headroom: {result} units.", "Remaining capacity: {result} units."), cases=cases),),
)
