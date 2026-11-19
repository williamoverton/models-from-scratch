from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        previous = rng.randrange(0, 100000)
        current = previous + rng.randrange(1, 10000)
        yield {"previous": f"{previous / 10:.1f}", "current": f"{current / 10:.1f}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(previous, current):
    return f"{Decimal(current) - Decimal(previous):.1f}"


SCHEMA = Schema(
    id="energy_meter_usage_difference",
    tool_names=("calculate_meter_usage", "subtract_meter_readings", "compute_meter_consumption", "calculate_reading_difference", "derive_kwh_from_readings", "find_meter_usage", "compute_cumulative_usage", "calculate_kwh_difference", "subtract_previous_reading", "measure_usage_between_readings"),
    descriptions=("Subtract the previous meter reading from the current reading.", "Calculate consumption from two cumulative kWh readings.", "Compute current reading minus previous reading in kWh.", "Find electricity usage from earlier and later cumulative readings.", "Determine consumption by subtracting the earlier meter value.", "Calculate the difference between current and previous meter readings.", "Derive kWh used from a pair of cumulative readings.", "Subtract the prior reading from the latest reading.", "Compute meter consumption as the change in the reading.", "Find the kWh difference between two meter readings."),
    parameters=(Parameter(names=("previous", "previous_reading")), Parameter(names=("current", "current_reading"))),
    tasks=(Task(id="difference", prompts=("A cumulative electricity meter previously read {previous} kWh and now reads {current} kWh. How much was used?", "Calculate kWh consumed between the earlier reading {previous} and later reading {current}; there was no reset.", "The cumulative meter went from {previous} to {current} kWh without resetting. Find the electricity used.", "How many kWh were consumed as the meter rose from {previous} to {current}, with no reset?", "Subtract the previous cumulative reading of {previous} kWh from the current {current} kWh. What is usage?", "Calculate electricity consumption from cumulative readings: previous {previous} kWh, current {current} kWh, no reset.", "An electricity meter read {previous} kWh before and {current} kWh now. What is the usage difference?", "Find the kWh used between a previous meter reading of {previous} and a current reading of {current}; the meter did not reset.", "With cumulative meter readings of {previous} kWh earlier and {current} kWh now, how much electricity was used?", "The current reading is {current} kWh and the prior reading was {previous} kWh. Calculate the consumption without a reset.", "Determine meter usage in kWh given an earlier cumulative reading of {previous} and a later one of {current}.", "A cumulative meter changed from {previous} to {current} kWh. Assuming no reset, calculate the consumption."), answers=("Usage: {result} kWh.", "Consumption was {result} kWh."), cases=cases),),
)
