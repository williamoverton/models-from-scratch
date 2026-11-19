from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"area": str(rng.randint(5, 250)), "rate": str(rng.randint(2, 20))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(area, rate):
    return str(int(area) * int(rate))


SCHEMA = Schema(
    id="agriculture_irrigation_volume",
    tool_names=("calculate_irrigation_volume", "estimate_field_water", "compute_irrigation_liters", "find_field_water_volume", "calculate_watering_requirement", "derive_irrigation_water", "compute_area_water_product", "estimate_irrigation_liters", "determine_field_water_need", "calculate_field_application_volume"),
    descriptions=("Multiply field area in square meters by water rate in liters per square meter.", "Calculate total irrigation water from area and application rate.", "Compute liters of water as field area times application rate.", "Find the water volume required for the given area and rate.", "Determine irrigation liters from square meters and liters per square meter.", "Multiply the field size by its water application rate.", "Calculate total field watering volume in liters.", "Apply the per-square-meter water rate to the whole field.", "Derive irrigation volume by multiplying area and rate.", "Compute the total liters needed for an irrigation application."),
    parameters=(Parameter(names=("area", "area_m2")), Parameter(names=("rate", "liters_per_m2"))),
    tasks=(Task(id="volume", prompts=(
        'A field covers {area} square meters. Apply {rate} liters per square meter. How many liters are needed?',
        'What volume of water in liters is required for {area} m² at {rate} L/m²?',
        'Irrigate {area} square meters at a uniform rate of {rate} liters per square meter. Give the total water volume in liters.',
        'How many liters will cover a field of {area} m² when each square meter receives {rate} liters?',
        'The application rate is {rate} L/m² across {area} m². Calculate the total irrigation requirement in liters.',
        'For a {area}-square-meter field, plan an application of {rate} liters per square meter; determine the full volume in liters.',
        'Water is applied at {rate} liters per square meter. If the field occupies {area} square meters, what is the total number of liters?',
        'Find the irrigation volume in liters for {area} m² of land receiving {rate} L/m².',
        'A field needs {rate} liters on every square meter, and its area is {area} square meters. Compute the overall liters needed.',
        'Given an area of {area} square meters and a watering rate of {rate} liters per square meter, calculate the liters required for the whole field.',
        'Size the water supply in liters: the irrigated area is {area} m² and the intended dose is {rate} L/m².',
        'Across all {area} square meters, apply {rate} liters to each square meter. What total irrigation volume in liters does that require?',
    ), answers=("The field needs {result} liters.", "Required water: {result} liters."), cases=cases),),
)
