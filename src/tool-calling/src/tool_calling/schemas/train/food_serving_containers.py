from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"servings": str(rng.randint(1, 100)), "capacity": str(rng.randint(1, 12))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(servings, capacity):
    servings, capacity = int(servings), int(capacity)
    return str((servings + capacity - 1) // capacity)


SCHEMA = Schema(
    id="food_required_containers",
    tool_names=('calculate_container_count', 'count_serving_containers', 'compute_required_containers', 'calculate_serving_container_count', 'determine_whole_containers', 'find_required_serving_containers', 'compute_packing_container_count', 'calculate_minimum_containers', 'count_containers_for_servings', 'get_serving_container_requirement'),
    descriptions=('Calculate the minimum whole containers needed for servings at a fixed capacity.', 'Divide servings by container capacity and round up.', 'Compute the whole container count needed to hold the specified servings.', 'Find the minimum number of containers for a serving count and per-container capacity.', 'Return the ceiling of servings divided by servings per container.', 'Determine how many whole containers are required at the given capacity.', 'Calculate the number of containers for the servings, rounding up.', 'Compute the smallest whole container count that accommodates all servings.', 'Find the container requirement from servings and capacity, rounded up.', 'Divide the serving count by container capacity and round up to a whole container.'),
    parameters=(Parameter(names=("servings", "serving_count")), Parameter(names=("capacity", "servings_per_container"))),
    tasks=(Task(id="containers", prompts=("How many whole containers are needed for {servings} servings if each holds {capacity} servings? Round up.", "Pack {servings} servings into containers holding {capacity} servings each. Give the minimum number of whole containers.", "What is the minimum whole container count for {servings} servings at {capacity} servings per container?", "Allowing {capacity} servings per container, how many whole containers hold all {servings} servings? Round up.", "Calculate containers for {servings} servings, each holding {capacity}; round up to a whole container.", "We have {servings} servings and containers with capacity {capacity}. How many whole containers are needed?", "Divide {servings} servings into containers of {capacity}, rounding up. How many containers?", "Find the smallest number of whole containers that can hold {servings} servings at {capacity} per container.", "If each container holds {capacity} servings, how many whole containers must I use for {servings} servings?", "Determine the whole-container requirement for {servings} servings with {capacity} servings of capacity each; round up.", "For {servings} servings, how many containers of {capacity} servings are required, including a partially filled one?", "Pack all {servings} servings at {capacity} per container and report the minimum whole containers."), answers=("{result} containers.", "Required containers: {result}."), cases=cases),),
)
