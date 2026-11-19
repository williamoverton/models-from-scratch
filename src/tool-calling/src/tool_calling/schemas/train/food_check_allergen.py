from ...schema_types import Decision, Parameter, Schema, Task


RECIPES = {
    "R1": ("milk", "wheat", "eggs"),
    "R2": ("rice", "soy", "carrots"),
    "R3": ("peanuts", "tomatoes", "wheat"),
    "R4": ("eggs", "rice", "soy"),
}
ALLERGENS = ("milk", "eggs", "wheat", "peanuts", "soy")


def cases(rng, count):
    for _ in range(count):
        yield {"recipe_id": rng.choice(tuple(RECIPES)), "allergen": rng.choice(ALLERGENS)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(recipe_id, allergen):
    present = allergen in RECIPES[recipe_id]
    return f"{allergen} is {'listed' if present else 'not listed'} in recipe {recipe_id}."


SCHEMA = Schema(
    id="food_check_recipe_allergen",
    tool_names=('check_recipe_allergen', 'inspect_recipe_allergen', 'lookup_recipe_allergen', 'check_ingredient_allergen', 'recipe_lists_allergen', 'find_recipe_allergen', 'verify_recipe_allergen_listing', 'inspect_allergen_membership', 'query_recipe_allergen_listing', 'report_recipe_allergen_presence'),
    descriptions=('Check whether a named allergen is listed in a recipe; do not infer cross-contact.', 'Look up exact allergen membership for a recipe.', 'Report whether the specified recipe lists the named allergen as an ingredient.', 'Inspect a recipe ingredient list for exact membership of the given allergen.', 'Determine if the requested allergen appears in the selected recipe listing.', 'Check the named allergen against the specified recipe ingredients, not cross-contact.', 'Return whether the allergen is listed for the supplied recipe ID.', 'Look for the exact allergen in a recipe’s listed ingredients.', 'Report listed or not listed for a recipe and allergen pair.', 'Check the recipe’s recorded ingredients for the specified allergen without inferring contamination.'),
    parameters=(Parameter(names=("recipe_id", "recipe")), Parameter(names=("allergen", "substance"))),
    tasks=(Task(id="check", prompts=("Does recipe {recipe_id} list {allergen} as an ingredient?", "Check recipe {recipe_id} for the allergen {allergen}.", "Is {allergen} listed in recipe {recipe_id}?", "Look up whether recipe {recipe_id} includes {allergen} in its ingredients.", "Check the ingredient listing for {recipe_id}: is {allergen} present?", "For recipe {recipe_id}, report whether {allergen} is listed.", "Does the ingredient list of {recipe_id} contain {allergen}?", "Inspect recipe {recipe_id} for the listed ingredient {allergen}.", "Is {allergen} among the recorded ingredients for recipe {recipe_id}?", "Find out if recipe {recipe_id} lists the allergen {allergen}.", "Check exact ingredient membership of {allergen} in recipe {recipe_id}.", "Does {recipe_id} have {allergen} on its ingredient list?"), answers=("{result}", "Ingredient check: {result}"), cases=cases),),
)
