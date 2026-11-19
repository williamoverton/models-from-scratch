from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"area": str(rng.randint(50, 2000)), "rate": str(rng.randint(50, 500))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(area, rate):
    hours = Decimal(area) / Decimal(rate)
    return f"{hours.quantize(Decimal('0.01'))} hours"


SCHEMA = Schema(
    id="facilities_cleaning_estimate",
    tool_names=("estimate_cleaning_time", "calculate_cleaning_duration", "compute_cleaning_hours", "get_cleaning_time_estimate", "estimate_area_cleaning_hours", "calculate_area_cleaning_time", "derive_cleaning_duration", "find_cleaning_hours", "measure_estimated_cleaning_time", "compute_area_cleaning_duration"),
    descriptions=("Estimate hours as area divided by the cleaning rate, rounded to two decimal places.", "Calculate cleaning duration from area and hourly cleaning rate.", "Divide area by the hourly cleaning rate and round hours to two decimal places using half-even rounding.", "Compute estimated cleaning hours from area and rate with half-even rounding to two decimals.", "Return the estimated duration in hours for an area at the given hourly rate.", "Calculate area divided by rate as hours, rounded half-even to hundredths.", "Estimate how long cleaning takes using area and area cleaned per hour.", "Find the cleaning duration by dividing the area by its hourly cleaning rate.", "Express the area-to-rate cleaning estimate in hours to two decimal places.", "Determine estimated cleaning time in hours, rounding the quotient to two decimal places."),
    parameters=(Parameter(names=("area", "square_metres")), Parameter(names=("rate", "square_metres_per_hour"))),
    tasks=(Task(id="estimate", prompts=("Cleaning covers {area} square metres at {rate} square metres per hour. Estimate the hours needed, rounded to two decimal places using half-even rounding.", "At a rate of {rate} square metres per hour, how many hours are needed for {area} square metres? Round to two decimal places using half-even rounding.", "Estimate cleaning hours for {area} square metres at {rate} square metres per hour, rounding to two decimal places half-even.", "How long in hours to clean {area} square metres at {rate} square metres per hour? Round to hundredths using half-even rounding.", "Calculate the cleaning time for {area} square metres at an hourly rate of {rate} square metres, with half-even rounding to two decimal places.", "For an area of {area} square metres and a cleaning rate of {rate} square metres per hour, estimate hours to two decimals using half-even rounding.", "Divide {area} square metres by {rate} square metres per hour to estimate hours; round half-even to two decimal places.", "What is the estimated duration in hours for cleaning {area} square metres at {rate} square metres per hour? Use two decimal places and half-even rounding.", "A cleaner covers {rate} square metres per hour. Estimate hours for {area} square metres, rounded half-even to two decimal places.", "Estimate the number of hours needed to clean {area} square metres at {rate} square metres per hour. Round half-even to hundredths.", "Cleaning rate: {rate} square metres per hour; area: {area} square metres. Give the time in hours rounded to two decimals using half-even rounding.", "Work out cleaning hours for {area} square metres at {rate} square metres per hour, applying half-even rounding to two decimal places."), answers=("Estimated cleaning time: {result}.", "The estimate is {result}."), cases=cases),),
)
