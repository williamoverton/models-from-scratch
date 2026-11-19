from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        material = rng.randint(5, 50) * 10
        rate = rng.choice((50, 60, 70, 80, 90))
        yield {"material": str(material), "rate": str(rate)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(material, rate):
    return str(int(material) * int(rate) // 100)


SCHEMA = Schema(
    id="manufacturing_material_yield",
    tool_names=("calculate_material_yield", "compute_usable_material", "calculate_usable_yield", "estimate_retained_material", "compute_material_output", "calculate_yield_quantity", "determine_usable_output", "compute_retained_quantity", "calculate_process_yield", "find_usable_material_quantity"),
    descriptions=("Calculate usable material from input quantity and yield percentage.", "Multiply input material by the yield rate.", "Compute the retained quantity from material input and percentage yield.", "Determine usable output for a given input amount and yield percent.", "Calculate material remaining after applying a process yield rate.", "Find the usable material quantity by applying the percentage to the input.", "Compute output material from the specified input units and yield percentage.", "Apply the yield rate to an input quantity to find usable material.", "Determine how much input material is retained at the given yield percentage.", "Calculate the usable quantity produced from material input at a stated yield."),
    parameters=(Parameter(names=("material", "input_units")), Parameter(names=("rate", "yield_percent"))),
    tasks=(Task(id="yield", prompts=("A process retains {rate}% of {material} kg of input material. How many kg are usable?", "Calculate usable output in kg from {material} kg input at {rate}% yield.", "How much usable material remains from {material} kg at a yield of {rate}%?", "For an input of {material} kg, find the output in kg when the process retains {rate}%.", "Apply a {rate}% yield to {material} kg of material. What is the usable quantity?", "A manufacturing run starts with {material} kg and yields {rate}%. How many kilograms are usable?", "What is the retained mass in kg if {rate}% of the {material} kg input is usable?", "Compute the usable kg produced from {material} kg of input with a {rate}% yield.", "Of {material} kg entering a process, {rate}% is retained. Give the usable amount in kg.", "Please work out the material yield in kg for {material} kg input and a {rate}% retention rate.", "At {rate}% process yield, how many kg of {material} kg input remain usable?", "Find the kilograms of usable output when {material} kg is processed at {rate}% yield."), answers=("{result} kg.", "Usable material: {result} kg."), cases=cases),),
)
