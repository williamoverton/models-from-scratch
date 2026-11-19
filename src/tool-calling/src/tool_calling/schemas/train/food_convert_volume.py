from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


FACTORS = {"milliliters": Decimal("1"), "liters": Decimal("1000"), "teaspoons": Decimal("5"), "tablespoons": Decimal("15")}


def cases(rng, count):
    for _ in range(count):
        source, target = rng.sample(tuple(FACTORS), 2)
        yield {"amount": str(rng.randrange(1, 101)), "source_unit": source, "target_unit": target}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(amount, source_unit, target_unit):
    value = Decimal(amount) * FACTORS[source_unit] / FACTORS[target_unit]
    return f"{value.quantize(Decimal('0.01')):.2f} {target_unit}"


SCHEMA = Schema(
    id="food_convert_volume_units",
    tool_names=('convert_recipe_volume', 'translate_volume_units', 'convert_cooking_volume', 'calculate_recipe_volume_conversion', 'change_recipe_volume_units', 'translate_cooking_volume', 'convert_metric_recipe_measurement', 'compute_recipe_volume_equivalent', 'express_recipe_volume_units', 'convert_specified_volume'),
    descriptions=('Convert volume using 1 liter = 1000 mL, 1 teaspoon = 5 mL, and 1 tablespoon = 15 mL; round to two decimals.', 'Convert recipe volume using the specified metric equivalents and two decimal places.', 'Express a volume in the requested unit using 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon, rounded to two decimals.', 'Convert between milliliters, liters, teaspoons and tablespoons using the given metric factors and two decimal places.', 'Calculate a recipe volume in another supported unit with 1000 mL/L, 5 mL/tsp and 15 mL/tbsp, rounded to two decimals.', 'Translate a volume between supported units using the specified milliliter equivalents, rounded to two decimals.', 'Return a two-decimal conversion using 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon.', 'Change recipe volume units using the fixed metric equivalents and round to two decimal places.', 'Calculate the target volume from the source amount using the fixed liter, teaspoon and tablespoon factors, to two decimals.', 'Convert the supplied recipe volume with 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon; round to hundredths.'),
    parameters=(Parameter(names=("amount", "quantity")), Parameter(names=("source_unit", "from_unit")), Parameter(names=("target_unit", "to_unit"))),
    tasks=(Task(id="convert", prompts=("Convert {amount} {source_unit} to {target_unit}. Use 1 liter = 1000 mL, 1 teaspoon = 5 mL and 1 tablespoon = 15 mL; round to two decimals.", "How many {target_unit} are in {amount} {source_unit}? Use 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon, rounded to two decimals.", "Express {amount} {source_unit} in {target_unit}, using 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon; round to two decimals.", "Change {amount} {source_unit} into {target_unit}. Assume 1 liter = 1000 mL, 1 teaspoon = 5 mL, 1 tablespoon = 15 mL and give two decimal places.", "What is {amount} {source_unit} in {target_unit}? Use 1 L = 1000 mL, 1 tsp = 5 mL, 1 tbsp = 15 mL; round to two decimals.", "Calculate {target_unit} equivalent to {amount} {source_unit}, using 1000 mL/L, 5 mL/teaspoon and 15 mL/tablespoon, rounded to two decimals.", "Convert the recipe volume {amount} {source_unit} to {target_unit}; use 1000 mL per liter, 5 mL per teaspoon, 15 mL per tablespoon and two decimal places.", "Using 1 liter as 1000 mL, 1 teaspoon as 5 mL and 1 tablespoon as 15 mL, convert {amount} {source_unit} to {target_unit} and round to two decimals.", "Please translate {amount} {source_unit} into {target_unit}. Use 1000 mL/L, 5 mL/tsp and 15 mL/tbsp; round to two decimals.", "Find the volume in {target_unit} for {amount} {source_unit}, taking a liter as 1000 mL, teaspoon as 5 mL and tablespoon as 15 mL; round to two decimals.", "Using 1000 mL per liter, 5 mL per teaspoon and 15 mL per tablespoon, how many {target_unit} equal {amount} {source_unit}? Round to two decimals.", "Convert {amount} {source_unit} into {target_unit} with 1 L = 1000 mL, 1 tsp = 5 mL and 1 tbsp = 15 mL, reporting two decimal places."), answers=("That is {result}.", "The converted volume is {result}."), cases=cases),),
)
