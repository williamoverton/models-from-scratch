from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"plant": rng.choice(("fern", "cactus", "tomato")), "count": str(rng.randrange(1, 101))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="garden_water",
    tool_names=('garden_water', 'watering_amount', 'calculate_sample_plant_water', 'estimate_batch_watering', 'compute_sample_water_litres', 'plant_water_requirement', 'sample_watering_quantity', 'get_plant_water_amount', 'calculate_garden_water_litres', 'estimate_plant_batch_water'),
    descriptions=('Calculate litres of water for identical plants using fixed sample per-plant amounts.', 'Estimate water needed for a batch of plants from sample amounts.', 'Compute sample water litres for a count of one plant type.', 'Calculate a batch’s water requirement using the sample amount for its plant type.', 'Return sample watering litres for the given plant type and count.', 'Find the water needed for identical plants using fixed sample quantities.', 'Estimate litres for a plant batch using the sample per-plant amount.', 'Compute the sample watering quantity from plant type and count.', 'Determine sample water litres by multiplying a plant count by its fixed per-plant amount.', 'Get the sample amount of water in litres for the specified number of plants.'),
    parameters=(
        Parameter(names=("plant", "plant_type")),
        Parameter(names=("count", "plant_count")),
    ),
    tasks=(Task(id="water", prompts=("How many litres of water do {count} {plant} plants need using the sample amounts?", "Estimate water for {count} {plant} plants from the sample amounts.", 'Calculate sample water needs in litres for {count} {plant} plants.', 'Using sample per-plant amounts, how many litres do {count} {plant} plants require?', 'For a batch of {count} {plant} plants, find the sample watering quantity in litres.', 'Estimate litres needed to water {count} {plant} plants using the sample amounts.', 'What is the sample total water requirement in litres for {count} plants of type {plant}?', 'A batch contains {count} {plant} plants; compute its water in litres from sample amounts.', 'Determine the litres of sample water for {count} identical {plant} plants.', 'Using the sample watering rates, express the water for {count} {plant} plants in litres.', 'How much water in litres would {count} {plant} plants need under the sample amounts?', 'Find the total sample watering litres for a group of {count} {plant} plants.'), answers=("They need {result} litres.", "Use {result} litres of water."), cases=cases),),
)


def resolve(plant, count):
    millilitres = {"fern": 250, "cactus": 100, "tomato": 500}[plant] * int(count)
    return f"{millilitres // 1000}.{millilitres % 1000:03d}"
