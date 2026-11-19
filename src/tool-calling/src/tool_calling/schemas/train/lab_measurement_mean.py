from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        readings = [rng.randint(1, 100) for _ in range(3)]
        yield {"readings": ", ".join(map(str, readings))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(readings):
    values = [Decimal(value) for value in readings.split(", ")]
    return f"{sum(values) / len(values):.2f} mg"


SCHEMA = Schema(
    id="lab_measurement_mean",
    tool_names=("calculate_measurement_mean", "average_lab_readings", "compute_mean_measurement", "calculate_average_reading", "compute_lab_reading_mean", "find_arithmetic_mean_mg", "average_measurements_mg", "calculate_mean_lab_measurement", "compute_average_mg_readings", "find_mean_of_measurements"),
    descriptions=("Calculate the arithmetic mean of comma-separated mg readings, rounded to two decimals using half-even.", "Average mg readings and round to two decimal places using half-even.", "Compute the arithmetic mean of the supplied mg measurements and round half-even to two decimal places.", "Find the average of comma-separated milligram readings, reported to two decimals with half-even rounding.", "Calculate the mean measurement in mg with two-decimal half-even rounding.", "Average the provided laboratory readings in mg using half-even rounding to two places.", "Return the arithmetic average of the measurements in mg, rounded half-even to two decimals.", "Compute the mean of the comma-separated mg values and format it to two decimal places using half-even.", "Determine the average mg reading with half-even rounding to two decimal places.", "Calculate a two-decimal arithmetic mean in mg from the supplied readings, rounding half-even."),
    parameters=(Parameter(names=("readings", "measurements")),),
    tasks=(Task(id="mean", prompts=("Measurements in mg: {readings}. Calculate their arithmetic mean in mg, rounded to two decimal places using half-even.", "Average these mg measurements: {readings}. Report mg to two decimal places, rounding half-even.", "Find the arithmetic average of {readings} mg and express it in mg to two decimal places, using half-even rounding.", "For the mg readings {readings}, what is the mean in mg rounded half-even to two decimals?", "Take the arithmetic mean of these measurements in mg: {readings}. Round half-even and report two decimal places in mg.", "The measurements are {readings} mg. Give their average in mg, rounded to two decimal places by the half-even rule.", "Compute the mean in mg of {readings}, treating the values as mg and rounding half-even to two decimal places.", "What is the two-decimal, half-even-rounded arithmetic mean in mg for these mg measurements: {readings}?", "Average the readings {readings} in mg; express the result in mg with two decimal places and half-even rounding.", "Use half-even rounding to two decimal places for the arithmetic mean of {readings} mg, and report it in mg.", "Calculate the mg average for measurements {readings} mg, rounding the result half-even to two decimal places.", "For readings {readings} measured in mg, return their arithmetic mean in mg to two decimals using half-even rounding."), answers=("Mean: {result}.", "The mean is {result}."), cases=cases),),
)
