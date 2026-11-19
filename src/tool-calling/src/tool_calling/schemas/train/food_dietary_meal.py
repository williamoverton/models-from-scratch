from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    meals = ("garden bowl", "lentil soup", "rice salad", "tofu plate", "bean stew", "vegetable wrap", "corn skillet")
    allergens = ("dairy", "gluten", "nuts", "eggs")
    for _ in range(count):
        names = rng.sample(meals, 3)
        restrictions = rng.sample(allergens, 2)
        safe = rng.randrange(3)
        rows = []
        for i, name in enumerate(names):
            contents = rng.sample([a for a in allergens if a not in restrictions], rng.randint(0, 2)) if i == safe else rng.sample(restrictions, rng.randint(1, 2))
            rows.append((name, contents))
        options = "; ".join(f"{name}: contains {', '.join(contents) if contents else 'none of dairy, gluten, nuts, or eggs'}" for name, contents in rows)
        yield {"rows": rows, "restrictions": ", ".join(restrictions), "excluded": restrictions, "options": options}


def prepare(*, task_id, case):
    meal = next(name for name, contents in case["rows"] if not set(contents).intersection(case["excluded"]))
    return Decision(fields=case, arguments={"meal": meal})


def resolve(meal):
    return f"Selected meal: {meal}."


SCHEMA = Schema(
    id="food_dietary_meal",
    tool_names=('report_selected_meal', 'acknowledge_chosen_meal', 'confirm_meal_choice', 'report_meal_choice', 'identify_selected_dish', 'acknowledge_selected_dish', 'return_chosen_meal', 'report_dish_selection', 'confirm_chosen_dish', 'record_meal_choice'),
    descriptions=('Report the selected meal by name.', 'Acknowledge the supplied chosen meal.', 'Return a confirmation naming the selected dish.', 'Report the meal identifier supplied as the choice.', 'Confirm the specified meal selection.', 'Acknowledge a previously chosen meal by name.', 'Return the provided dish as the selected meal.', 'Identify the meal supplied as the selection.', 'Report the given meal choice.', 'Confirm the selected dish using its supplied name.'),
    parameters=(Parameter(names=("meal", "dish")),),
    tasks=(Task(id="diet", prompts=("Select the meal containing none of these restricted ingredients: {restrictions}. Menu: {options}.", "Choose the meal suitable for avoiding {restrictions}; listed contents are exhaustive for these restrictions. {options}.", "Pick the meal that contains none of {restrictions} from this menu: {options}.", "Using the listed contents, select the dish that avoids {restrictions}: {options}.", "Which meal is free of the restricted ingredients {restrictions}? Menu: {options}.", "Choose the option with no {restrictions} among these listed contents: {options}.", "From {options}, select the meal whose contents exclude {restrictions}.", "Find the meal suitable for someone avoiding {restrictions}; the menu lists its contents: {options}.", "Compare the listed meal contents against {restrictions} and choose one containing neither restricted ingredient: {options}.", "Select the dish without any of the restrictions {restrictions}, based on {options}.", "Which option avoids all of {restrictions}? Choose from {options}.", "Review {options} and select the meal with none of the restricted ingredients {restrictions}."), answers=("{result}", "Choice recorded. {result}"), cases=cases),),
)
