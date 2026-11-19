from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    recipes = ("noodle bowl", "bean salad", "tomato soup", "egg wrap", "rice skillet", "lentil stew", "tofu stir-fry")
    for _ in range(count):
        names = rng.sample(recipes, 3)
        times = rng.sample(range(5, 61), 3)
        yield {"options": "; ".join(f"{name}: {time} minutes" for name, time in zip(names, times)), "choices": list(zip(names, times))}


def prepare(*, task_id, case):
    recipe, _ = min(case["choices"], key=lambda choice: choice[1])
    return Decision(fields=case, arguments={"recipe": recipe})


def resolve(recipe):
    return f"Selected recipe: {recipe}."


SCHEMA = Schema(
    id="food_select_shortest_prep",
    tool_names=('report_selected_recipe', 'acknowledge_chosen_recipe', 'confirm_recipe_choice', 'report_recipe_choice', 'identify_selected_recipe', 'acknowledge_selected_recipe', 'return_chosen_recipe', 'report_recipe_selection', 'confirm_chosen_recipe', 'acknowledge_recipe_choice'),
    descriptions=('Report the selected recipe identifier.', 'Acknowledge the chosen preparation option.', 'Return a confirmation naming the selected recipe.', 'Report the recipe identifier supplied as the choice.', 'Confirm the specified recipe selection.', 'Acknowledge a previously chosen recipe by name.', 'Return the provided recipe as the selection.', 'Identify the recipe supplied as the selected option.', 'Report the given recipe choice.', 'Confirm the chosen recipe without comparing preparation times.'),
    parameters=(Parameter(names=("recipe", "dish")),),
    tasks=(Task(id="shortest", prompts=("Which recipe has the shortest prep time? {options}.", "Choose the fastest to prepare from these options: {options}.", "Select the recipe with the least preparation time: {options}.", "From {options}, pick the quickest recipe to prepare.", "Compare the preparation times and choose the shortest: {options}.", "Which dish takes the fewest minutes to prepare? {options}.", "Choose the minimum prep-time recipe among {options}.", "Identify the fastest preparation option: {options}.", "Pick the recipe that requires the least prep time from {options}.", "Which of these recipes is quickest to prep: {options}?", "Select the dish with the lowest listed preparation time: {options}.", "Review {options} and choose the recipe with the shortest preparation time."), answers=("{result}", "The choice is confirmed. {result}"), cases=cases),),
)
