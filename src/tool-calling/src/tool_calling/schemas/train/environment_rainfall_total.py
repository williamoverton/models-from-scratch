from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        a, b, c = (rng.randint(0, 40) for _ in range(3))
        yield {"a": a, "b": b, "c": c}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(a, b, c):
    return f"{int(a) + int(b) + int(c)} mm"


SCHEMA = Schema(
    id="environment_rainfall_total",
    tool_names=("sum_rainfall", "calculate_rainfall_total", "add_daily_rainfall", "total_three_rain_readings", "sum_daily_precipitation", "compute_rainfall_sum", "add_three_rainfall_amounts", "calculate_three_day_rainfall", "aggregate_daily_rainfall", "find_total_rainfall"),
    descriptions=("Add three rainfall readings in millimeters.", "Calculate total rainfall from three daily readings.", "Sum three daily rainfall amounts in mm.", "Compute the combined rainfall of three days.", "Add the supplied three precipitation readings.", "Find total rainfall in millimeters from three values.", "Combine three daily rain measurements by addition.", "Calculate the sum of three rainfall amounts.", "Total the provided daily rainfall readings.", "Determine the three-day rainfall total in mm."),
    parameters=(Parameter(names=("a", "day_one")), Parameter(names=("b", "day_two")), Parameter(names=("c", "day_three"))),
    tasks=(Task(id="total", prompts=("Rainfall over three days was {a}, {b}, and {c} mm. Add the readings.", "Calculate total rainfall in mm from daily amounts {a}, {b}, and {c}.", "What is the combined rainfall in mm for days with {a}, {b}, and {c} mm?", "Add three daily rain measurements: {a} mm, {b} mm, and {c} mm.", "A rain gauge recorded {a}, {b}, and {c} mm on three days. What is the total?", "Find the three-day rainfall total in millimeters given {a}, {b}, and {c}.", "Sum the daily precipitation readings of {a}, {b}, and {c} mm.", "How many millimeters of rain fell altogether if the daily amounts were {a}, {b}, and {c}?", "Combine rainfall of {a} mm, {b} mm, and {c} mm into a total.", "The three daily rainfall figures are {a}, {b}, and {c} mm. Calculate their sum.", "Report total rainfall in mm across three days with readings {a}, {b}, and {c}.", "What do {a} mm, {b} mm, and {c} mm of daily rainfall add up to?"), answers=("Total: {result}.", "{result} total."), cases=cases),),
)
