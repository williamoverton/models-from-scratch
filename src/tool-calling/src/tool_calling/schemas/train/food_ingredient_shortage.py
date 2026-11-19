from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    ingredients = ("rice", "beans", "flour", "tomatoes", "onions", "lentils", "carrots")
    for _ in range(count):
        names = rng.sample(ingredients, 3)
        shortage = rng.randrange(3)
        rows = []
        for i, name in enumerate(names):
            required = rng.randint(3, 20)
            available = rng.randrange(required) if i == shortage else rng.randint(required, required + 10)
            rows.append((name, required, available))
        yield {"rows": rows, "options": "; ".join(f"{name}: need {need} units, have {have} units" for name, need, have in rows)}


def prepare(*, task_id, case):
    name = next(name for name, need, have in case["rows"] if have < need)
    return Decision(fields=case, arguments={"ingredient": name})


def resolve(ingredient):
    return f"Flagged ingredient: {ingredient}."


SCHEMA = Schema(
    id="food_ingredient_shortage",
    tool_names=('report_flagged_ingredient', 'acknowledge_flagged_ingredient', 'report_ingredient_flag', 'confirm_ingredient_flag', 'identify_flagged_ingredient', 'acknowledge_ingredient_marker', 'return_flagged_ingredient', 'report_specified_ingredient_flag', 'confirm_flagged_item', 'report_shortage_ingredient'),
    descriptions=('Report the specified ingredient as flagged.', 'Acknowledge the supplied ingredient flag.', 'Return the given ingredient as the flagged item.', 'Confirm the ingredient identifier provided for flagging.', 'Report which ingredient was supplied to be flagged.', 'Acknowledge a flag for the named ingredient.', 'Identify the ingredient supplied as the flagged item.', 'Return a confirmation naming the flagged ingredient.', 'Report the provided ingredient in a flag acknowledgment.', 'Confirm the named ingredient as flagged without assessing stock.'),
    parameters=(Parameter(names=("ingredient", "item")),),
    tasks=(Task(id="shortage", prompts=("Flag the ingredient whose available units are less than required: {options}.", "Which ingredient needs restocking? Flag the one with fewer units on hand than needed: {options}.", "Compare required and available units; flag the ingredient in shortage: {options}.", "From {options}, flag the ingredient with less stock than needed.", "Which ingredient has available units below its requirement? Flag it: {options}.", "Flag the understocked ingredient based on these needs and inventories: {options}.", "Review {options} and flag the ingredient whose supply falls short of demand.", "Identify and flag the ingredient where units on hand are fewer than units required: {options}.", "Find the ingredient needing more units and flag it: {options}.", "Use {options} to flag the ingredient with an insufficient available quantity.", "Which listed ingredient has a stock shortfall? Flag it using {options}.", "Flag the ingredient for which the available count is below the needed count: {options}."), answers=("{result}", "Done. {result}"), cases=cases),),
)
