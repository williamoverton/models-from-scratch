from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"length": str(rng.randint(100, 1200)), "spacing": str(rng.choice((10, 15, 20, 25, 30, 40, 50)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(length, spacing):
    return str(int(length) // int(spacing) + 1)


SCHEMA = Schema(
    id="agriculture_seed_spacing",
    tool_names=("count_row_plants", "calculate_seed_positions", "count_planting_positions", "compute_row_plant_count", "find_plants_per_row", "calculate_row_spacing_count", "count_inclusive_row_positions", "estimate_row_plant_capacity", "derive_seed_position_count", "compute_planting_row_capacity"),
    descriptions=("Count planting positions starting at zero and spaced evenly through the inclusive row endpoint.", "Compute floor(row length / spacing) plus one for an inclusive row.", "Count positions at zero and each spacing interval up to the row length.", "Calculate how many plants fit when both row endpoints are eligible.", "Find the number of evenly spaced planting positions including the start.", "Divide row length by spacing, round down, and add the initial plant.", "Count row positions through the endpoint when an interval lands on it.", "Determine inclusive planting capacity from row length and spacing.", "Compute the number of positions beginning at zero and not exceeding the row length.", "Return the floor of length divided by spacing plus one."),
    parameters=(Parameter(names=("length", "row_length_cm")), Parameter(names=("spacing", "spacing_cm"))),
    tasks=(Task(id="count", prompts=(
        'A row is {length} cm long. Plant at 0 cm and every {spacing} cm after that, including the far endpoint if a position lands there. How many plants fit?',
        'Count plants in a {length} cm row at {spacing} cm intervals: start at 0 and include any position exactly at the far end.',
        'Starting with a plant at zero, place the rest {spacing} cm apart along {length} cm. Count every position no farther than the endpoint, including it if reached exactly.',
        'How many planting spots lie on a {length} cm row when the first is at 0 cm and successive spots are {spacing} cm apart? Include the endpoint if an interval lands there.',
        'A grower marks 0 cm, then advances by {spacing} cm until the next mark would pass the end of a {length} cm row. Count the marks, including one on the endpoint.',
        'Determine the number of plants for a row of length {length} cm: begin at 0, space them {spacing} cm apart, and include a plant exactly at the far end.',
        'With {spacing} cm between plants and {length} cm available, how many positions are there from 0 cm through the far endpoint if it coincides with a position?',
        'Count the positions at 0, {spacing}, and subsequent {spacing} cm intervals up to {length} cm; include the far endpoint when a position lands on it.',
        'For a {length} cm planting row, put the first seed at 0 cm and each following seed {spacing} cm later. How many seeds fit, counting an exact endpoint placement?',
        'The row ends at {length} cm. Starting at 0 cm, place plants every {spacing} cm without going past the end; a position exactly at the end counts. Give the plant count.',
        'Find the inclusive capacity of a {length} cm row with {spacing} cm spacing: count the initial position at zero and any position exactly at the far endpoint.',
        'A seed can go at 0 cm and at each {spacing} cm step thereafter, including the {length} cm endpoint if reached exactly. How many positions does the row hold?',
    ), answers=("{result} plants fit.", "The row holds {result} plants."), cases=cases),),
)
