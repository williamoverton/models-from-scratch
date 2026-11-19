from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"units": str(rng.randint(10, 250)), "capacity": str(rng.randint(5, 40))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(units, capacity):
    units, capacity = int(units), int(capacity)
    return str((units + capacity - 1) // capacity)


SCHEMA = Schema(
    id="manufacturing_batch_capacity",
    tool_names=("calculate_batch_count", "plan_production_batches", "compute_required_batches", "determine_minimum_batches", "count_production_batches", "calculate_whole_batch_requirement", "estimate_batch_count", "find_batches_for_units", "compute_batch_capacity_requirement", "calculate_batches_needed"),
    descriptions=("Calculate the minimum whole batches needed at a fixed capacity.", "Divide units by batch capacity and round up.", "Find how many batches are required when each has a maximum unit capacity.", "Compute the whole batch count for a production quantity, counting a partial batch.", "Determine the minimum number of capacity-limited batches for the given units.", "Calculate production batch requirements by rounding the unit-to-capacity ratio up.", "Count the full and partial batches needed to produce the requested units.", "Return the smallest whole number of batches that can hold all units.", "Work out how many batches are needed at the specified units per batch.", "Compute the ceiling of units divided by batch capacity."),
    parameters=(Parameter(names=("units", "unit_count")), Parameter(names=("capacity", "units_per_batch"))),
    tasks=(Task(id="batches", prompts=("Produce {units} units in batches of at most {capacity} units. How many whole batches are needed?", "Each batch holds up to {capacity} units. Calculate the minimum batches for {units} units; a partial batch counts as one.", "How many batches are required for {units} units if each batch can hold at most {capacity}?", "Plan {units} units using a maximum of {capacity} per batch. Count any partial batch.", "What's the minimum whole batch count for {units} units at a capacity of {capacity} units per batch?", "A production run needs {units} units, with no more than {capacity} in a batch. How many batches will it take?", "Divide {units} units into batches of up to {capacity}, rounding up to include any incomplete batch.", "Find the number of batches needed to accommodate {units} units when capacity is {capacity} per batch.", "With a {capacity}-unit batch limit, how many whole batches cover {units} units?", "Schedule enough batches for {units} units, allowing at most {capacity} units per batch. How many are needed?", "If each batch fits up to {capacity} units, determine the minimum batch count for {units} units.", "Calculate the full and partial batches needed for {units} units at a maximum batch size of {capacity}."), answers=("{result} batches.", "Batches needed: {result}."), cases=cases),),
)
