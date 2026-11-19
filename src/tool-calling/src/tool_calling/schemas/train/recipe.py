from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"ingredient": rng.choice(("rice", "beans", "tomatoes")), "servings": str(rng.randrange(1, 101))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="recipe_scale",
    tool_names=("scale_ingredient", "recipe_amount", "calculate_ingredient_grams", "scale_recipe_component", "get_scaled_ingredient_amount", "calculate_recipe_ingredient", "find_ingredient_amount", "get_recipe_grams", "compute_ingredient_quantity", "scale_sample_recipe_ingredient"),
    descriptions=("Calculate grams of an ingredient in a sample recipe scaled from two servings.", "Look up and scale an ingredient amount for a sample recipe.", "Compute the sample recipe ingredient's grams for the requested servings.", "Scale a sample recipe component from its two-serving amount.", "Get the amount of a sample recipe ingredient in grams for a serving count.", "Calculate the grams of a named ingredient for the specified portions.", "Find the scaled ingredient quantity in the sample recipe.", "Determine the sample recipe's ingredient weight for the requested servings.", "Return the ingredient grams after scaling the two-serving recipe.", "Calculate a sample recipe component's weight for the given number of servings."),
    parameters=(
        Parameter(names=("ingredient", "component")),
        Parameter(names=("servings", "portions")),
    ),
    tasks=(Task(id="scale", prompts=("How many grams of {ingredient} are needed for {servings} servings of the sample recipe?", "Scale the sample recipe's {ingredient} to {servings} servings.", 'Calculate {ingredient} grams for {servings} servings of the sample recipe.', 'For {servings} portions of the sample recipe, how much {ingredient} in grams?', 'Find the sample recipe’s {ingredient} weight for {servings} servings.', 'What is the scaled amount of {ingredient} in grams for {servings} sample recipe servings?', 'Determine grams of {ingredient} for a {servings}-serving sample recipe.', 'I need {servings} servings of the sample recipe; calculate the {ingredient} in grams.', 'How much {ingredient}, by weight, goes into {servings} servings of the sample recipe?', 'Give the grams of {ingredient} required to make the sample recipe for {servings}.', 'Work out the sample recipe quantity of {ingredient} in grams for {servings} portions.', 'For a sample recipe scaled to {servings} servings, report the {ingredient} grams.'), answers=("Use {result} grams of {ingredient}.", "For {servings} servings, use {result} grams."), cases=cases),),
)


def resolve(ingredient, servings):
    grams_for_two = {"rice": 100, "beans": 150, "tomatoes": 200}
    return str(grams_for_two[ingredient] * int(servings) // 2)
