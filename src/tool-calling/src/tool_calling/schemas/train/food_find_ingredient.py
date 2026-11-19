from ...schema_types import Decision, Parameter, Schema, Task


RECIPES = {
    "chickpeas": "spiced stew",
    "spinach": "garden soup",
    "mushrooms": "herb skillet",
    "lentils": "country bake",
    "carrots": "market salad",
    "tofu": "rice bowl",
}


def cases(rng, count):
    for _ in range(count):
        yield {"ingredient": rng.choice(tuple(RECIPES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"ingredient": case["ingredient"]})


def resolve(ingredient):
    return f"{RECIPES[ingredient]} contains {ingredient}."


SCHEMA = Schema(
    id="food_find_recipe_ingredient",
    tool_names=('find_sample_recipe', 'lookup_recipe_by_ingredient', 'find_sample_dish_by_ingredient', 'query_sample_recipe_ingredient', 'get_sample_recipe_for_ingredient', 'lookup_sample_ingredient_recipe', 'match_sample_recipe_ingredient', 'find_sample_dish_with_ingredient', 'retrieve_sample_recipe_match', 'report_sample_ingredient_recipe'),
    descriptions=('Look up the recipe containing an ingredient in the fixed sample recipe collection.', 'Find a matching dish in the sample recipe catalog by ingredient.', 'Return the fixed sample recipe associated with the given ingredient.', 'Look up which sample dish contains the specified ingredient.', 'Find an ingredient’s associated dish in the fixed sample catalog.', 'Report the sample recipe mapped to the given ingredient.', 'Retrieve the matching recipe for an ingredient from the sample collection.', 'Identify the sample dish associated with the supplied ingredient.', 'Query the fixed sample ingredient-to-recipe mapping.', 'Find the sample collection recipe that lists the given ingredient.'),
    parameters=(Parameter(names=("ingredient", "component")),),
    tasks=(Task(id="find", prompts=("Which recipe in the sample collection contains {ingredient}?", "Find a sample recipe with {ingredient}.", "Look up the sample dish containing {ingredient}.", "In the sample recipe collection, which dish uses {ingredient}?", "Identify the recipe associated with {ingredient} in the sample catalog.", "Which sample recipe lists {ingredient} as an ingredient?", "Find the dish with {ingredient} in the sample collection.", "What is the sample recipe match for {ingredient}?", "Search the sample recipes for one containing {ingredient}.", "Name the sample dish that includes {ingredient}.", "From the fixed sample collection, retrieve the recipe for {ingredient}.", "Can you find which sample recipe contains {ingredient}?"), answers=("{result}", "The match is: {result}"), cases=cases),),
)
