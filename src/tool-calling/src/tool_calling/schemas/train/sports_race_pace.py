from decimal import Decimal, ROUND_HALF_UP

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"minutes": str(rng.randint(15, 180)), "kilometers": str(rng.choice((3, 5, 8, 10, 15, 20)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(minutes, kilometers):
    pace = (Decimal(minutes) / Decimal(kilometers)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"{pace:.2f}"


SCHEMA = Schema(
    id="sports_race_pace",
    tool_names=("calculate_race_pace", "compute_minutes_per_kilometer", "calculate_minutes_per_kilometer", "compute_race_pace", "calculate_average_pace", "compute_average_pace", "derive_race_pace", "determine_running_pace", "calculate_pace_per_kilometer", "compute_kilometer_pace"),
    descriptions=("Divide race minutes by kilometers and round half up to two decimals.", "Compute average pace in minutes per kilometer to two decimals, rounding half up.", "Calculate minutes per kilometer from elapsed minutes and distance, rounded half up to two decimals.", "Find average race pace by dividing minutes by kilometers and rounding half up to two decimal places.", "Return elapsed minutes per kilometer, rounded half up to two decimal places.", "Determine running pace as minutes divided by kilometers, with half-up rounding to two decimals.", "Compute the average minutes needed for each kilometer, rounded half up to two decimals.", "Derive pace from race time and distance in minutes per kilometer, rounding half up to two decimals.", "Calculate the per-kilometer pace using minutes and kilometers, rounded half up to two decimals.", "Divide elapsed minutes by distance in kilometers and return the pace to two decimals with half-up rounding."),
    parameters=(Parameter(names=("minutes", "elapsed_minutes")), Parameter(names=("kilometers", "distance_km"))),
    tasks=(Task(id="pace", prompts=("A runner covers {kilometers} km in {minutes} minutes. Calculate average minutes per km, rounded to two decimals with halves rounded up.", "What is the average pace in minutes per km for {kilometers} km run in {minutes} minutes? Round to two decimals, half up.", "For a {minutes}-minute race over {kilometers} km, work out minutes per kilometer to two decimal places using half-up rounding.", "A race took {minutes} minutes over {kilometers} kilometers. Give the average minutes per kilometer rounded half up to two decimals.", "Divide {minutes} minutes by {kilometers} km to find average pace; round half up to two decimal places.", "Find the runner's pace in minutes per km: distance {kilometers} km, time {minutes} minutes. Use two decimals and round halves up.", "How many minutes per kilometer was the average over {kilometers} km in {minutes} minutes? Round to two decimals, with halves up.", "Please calculate the two-decimal average pace in min/km for {minutes} minutes and {kilometers} km, using half-up rounding.", "With an elapsed time of {minutes} minutes for {kilometers} km, determine average minutes per km, rounding half up to two decimals.", "The runner finishes {kilometers} km in {minutes} minutes. Express the average pace as minutes per km to two decimal places, halves rounded up.", "Calculate min/km for a {kilometers} km run taking {minutes} minutes; round the result to two decimals using half-up rounding."), answers=("Average pace is {result} minutes per km.",), cases=cases),),
)
