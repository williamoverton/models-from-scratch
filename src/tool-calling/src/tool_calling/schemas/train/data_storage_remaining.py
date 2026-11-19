from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        capacity = rng.randint(100, 10000)
        yield {"capacity": str(capacity), "used": str(rng.randint(0, capacity))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(capacity, used):
    return f"{Decimal(capacity) - Decimal(used)} GB"


SCHEMA = Schema(
    id="data_storage_capacity_remaining",
    tool_names=('calculate_storage_remaining', 'subtract_storage_used', 'compute_storage_remaining', 'calculate_free_storage', 'find_unused_capacity', 'subtract_used_capacity', 'get_storage_headroom', 'compute_available_gb', 'remaining_storage_gb', 'calculate_unused_storage'),
    descriptions=('Subtract used storage from capacity in GB.', 'Calculate unused storage capacity.', 'Compute capacity minus used storage in GB.', 'Calculate free capacity by subtracting used GB.', 'Find unused storage in GB from capacity and used amounts.', 'Subtract used storage from total capacity in GB.', 'Calculate storage headroom as capacity minus used, in GB.', 'Compute available GB from capacity and usage.', 'Return remaining storage in GB after subtracting usage.', 'Calculate unused GB from the given capacity and used storage.'),
    parameters=(Parameter(names=("capacity", "capacity_gb")), Parameter(names=("used", "used_gb"))),
    tasks=(Task(id="remaining", prompts=("Storage capacity is {capacity} GB and {used} GB is used. Calculate remaining capacity as capacity minus used.", "How much of {capacity} GB remains after {used} GB is used? Subtract used from capacity.", "Find the free space in GB: capacity {capacity} GB, used {used} GB; subtract used from capacity.", "With {capacity} GB total and {used} GB consumed, calculate capacity minus used in GB.", "Compute the remaining GB by subtracting {used} GB used from {capacity} GB capacity.", "How many GB are available if {used} GB of {capacity} GB is used? Use capacity minus used.", "Subtract {used} GB of usage from the {capacity} GB capacity and report the remainder in GB.", "A storage system has {capacity} GB capacity and {used} GB used. What is capacity minus used in GB?", "Determine unused capacity in GB for {capacity} GB total and {used} GB used by subtraction.", "Calculate free storage in GB as {capacity} GB minus {used} GB.", "What is the remaining capacity in GB when {used} GB is subtracted from {capacity} GB?", "Report storage headroom in GB: {capacity} GB capacity less {used} GB used."), answers=("Remaining: {result}.", "{result} remains."), cases=cases),),
)
