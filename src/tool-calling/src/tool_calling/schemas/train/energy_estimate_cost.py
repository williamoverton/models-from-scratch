from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"usage_kwh": str(rng.randrange(50, 1501)), "rate": f"0.{rng.randrange(8, 40):02d}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(usage_kwh, rate):
    return f"{Decimal(usage_kwh) * Decimal(rate):.2f}"


SCHEMA = Schema(
    id="energy_estimate_usage_cost",
    tool_names=("estimate_electricity_charge", "calculate_usage_cost", "compute_energy_only_charge", "multiply_usage_by_rate", "estimate_kwh_charge", "calculate_energy_charge", "compute_electricity_usage_cost", "price_electricity_consumption", "estimate_consumption_charge", "calculate_kwh_cost"),
    descriptions=("Multiply kWh by the dollar rate per kWh, excluding other charges.", "Estimate the energy-only cost from usage and unit rate.", "Calculate usage times the per-kWh rate without fees or taxes.", "Compute the electricity consumption charge from kWh and rate.", "Find the energy-only price of the supplied consumption.", "Multiply electricity usage by its unit price.", "Determine the usage charge excluding other charges.", "Calculate the cost of kWh at the given dollar rate.", "Estimate an electricity charge without fees or taxes.", "Compute the energy component of a bill from usage and rate."),
    parameters=(Parameter(names=("usage_kwh", "consumption")), Parameter(names=("rate", "dollars_per_kwh"))),
    tasks=(Task(id="estimate", prompts=("Estimate the energy charge for {usage_kwh} kWh at ${rate} per kWh, excluding all other charges.", "What is the cost of {usage_kwh} kWh at ${rate}/kWh? Ignore fees and taxes.", "Calculate the energy-only charge for {usage_kwh} kWh at ${rate} per kWh; exclude all other charges.", "At ${rate} per kWh, how much does {usage_kwh} kWh cost before any other charges?", "Estimate usage cost for {usage_kwh} kWh at ${rate}/kWh, without fees, taxes or other charges.", "Multiply {usage_kwh} kWh by ${rate} per kWh for the energy charge only; exclude other charges.", "What is the electricity usage charge for {usage_kwh} kWh at a rate of ${rate} per kWh, excluding other charges?", "Find the energy-only price of {usage_kwh} kWh at ${rate}/kWh, with no additional charges.", "A customer used {usage_kwh} kWh at ${rate} per kWh. Calculate the charge for usage alone, excluding all other charges.", "Compute the consumption cost for {usage_kwh} kWh at ${rate} per kWh; do not include other charges.", "Estimate the bill's energy component for {usage_kwh} kWh priced at ${rate}/kWh, excluding everything else.", "Ignoring all other charges, calculate the cost of {usage_kwh} kWh at ${rate} per kWh."), answers=("The energy-only cost is ${result}.", "Estimated usage charge: ${result}."), cases=cases),),
)
