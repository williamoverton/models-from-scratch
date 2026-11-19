from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"servings_per_batch": str(rng.randrange(2, 21)), "batches": str(rng.randrange(1, 16))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(servings_per_batch, batches):
    return str(int(servings_per_batch) * int(batches))


SCHEMA = Schema(
    id="food_servings_per_batch_and_batches",
    tool_names=('calculate_batch_servings', 'total_recipe_batch_servings', 'multiply_batch_yield', 'compute_serving_yield', 'count_total_batch_servings', 'derive_batch_portions', 'calculate_complete_batch_yield', 'get_batch_serving_total', 'compute_recipe_portions', 'sum_equal_batch_servings'),
    descriptions=('Multiply servings per batch by the number of complete batches.', 'Calculate total portions from a batch yield and batch count.', 'Compute the total servings produced by complete batches of equal yield.', 'Find the combined serving yield using the servings per batch and number of batches.', 'Determine how many portions all complete batches make.', 'Multiply a recipe batch serving yield by the batch count.', 'Calculate the serving count across identical complete batches.', 'Work out the total portions from the number of batches and portions per batch.', 'Compute the aggregate recipe yield in servings for the given batches.', 'Return the product of the batch count and servings per batch.'),
    parameters=(Parameter(names=("servings_per_batch", "batch_yield")), Parameter(names=("batches", "batch_count"))),
    tasks=(Task(id="total", prompts=("A recipe makes {servings_per_batch} servings per batch. How many servings do {batches} complete batches make?", "For {batches} batches at {servings_per_batch} servings each, what is the total serving count?", "How many servings result from {batches} complete batches yielding {servings_per_batch} servings each?", "Calculate the total yield of {batches} batches with {servings_per_batch} servings per batch.", "Each complete batch makes {servings_per_batch} servings. What do {batches} batches make altogether?", "Multiply {servings_per_batch} servings per batch by {batches} complete batches. What is the total?", "What is the combined serving count for {batches} batches if each yields {servings_per_batch}?", "With {servings_per_batch} servings in each batch, how many servings are in {batches} complete batches?", "Find the total portions from {batches} complete batches of {servings_per_batch} servings apiece.", "A batch yields {servings_per_batch} servings; determine the yield of {batches} full batches.", "If I prepare {batches} complete batches at {servings_per_batch} servings each, how many servings will I have?", "Compute the aggregate servings for {batches} batches producing {servings_per_batch} per batch."), answers=("Together they make {result} servings.", "The total is {result} servings."), cases=cases),),
)
