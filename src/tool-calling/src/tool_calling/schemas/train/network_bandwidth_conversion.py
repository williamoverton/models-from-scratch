from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"mbps": str(rng.randint(1, 10000)), "unit": rng.choice(("Kbps", "Gbps"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(mbps, unit):
    value = Decimal(mbps) * (Decimal(1000) if unit == "Kbps" else Decimal("0.001"))
    return f"{value.normalize():f} {unit}"


SCHEMA = Schema(
    id="network_bandwidth_units_conversion",
    tool_names=("convert_sample_bandwidth", "convert_bandwidth_units", "convert_mbps_rate", "convert_mbps_to_target_unit", "translate_decimal_bitrate", "calculate_bandwidth_conversion", "convert_network_bit_rate", "express_mbps_in_target_unit", "convert_decimal_bandwidth", "compute_mbps_unit_conversion"),
    descriptions=("Convert Mbps to decimal Kbps or Gbps.", "Convert network bit rates using decimal units.", "Express an Mbps rate in the requested Kbps or Gbps unit using decimal factors.", "Convert megabits per second to kilobits or gigabits per second.", "Convert Mbps to Kbps by multiplying by 1000 or to Gbps by dividing by 1000.", "Translate an Mbps bandwidth value to the selected decimal bit-rate unit.", "Calculate a decimal-unit conversion from Mbps to Kbps or Gbps.", "Return the given Mbps rate in the requested Kbps or Gbps unit.", "Change network bandwidth from Mbps to a supported decimal target unit.", "Compute the equivalent decimal Kbps or Gbps for a given Mbps rate."),
    parameters=(Parameter(names=("mbps", "rate_mbps")), Parameter(names=("unit", "target_unit"))),
    tasks=(Task(id="convert", prompts=("Convert {mbps} Mbps to {unit}. Use 1 Mbps = 1000 Kbps and 1000 Mbps = 1 Gbps.", "Express {mbps} Mbps in {unit}, using decimal bit-rate units: 1 Mbps = 1000 Kbps and 1 Gbps = 1000 Mbps.", "How many {unit} is {mbps} Mbps? Use decimal rates: 1 Mbps = 1000 Kbps and 1000 Mbps = 1 Gbps.", "Translate {mbps} Mbps into {unit}; 1 Mbps equals 1000 Kbps and 1000 Mbps equals 1 Gbps.", "Give the equivalent of {mbps} Mbps in {unit}, with 1 Mbps = 1000 Kbps and 1 Gbps = 1000 Mbps.", "Using decimal bandwidth units, convert {mbps} Mbps to {unit}. There are 1000 Kbps per Mbps and 1000 Mbps per Gbps.", "What is {mbps} Mbps expressed as {unit}? Assume 1 Mbps = 1000 Kbps and 1000 Mbps = 1 Gbps.", "Please convert the rate {mbps} Mbps into {unit}, using 1000 Kbps per Mbps and 1000 Mbps per Gbps.", "Calculate {mbps} Mbps in {unit}; use the decimal relationships 1 Mbps = 1000 Kbps and 1 Gbps = 1000 Mbps.", "A connection runs at {mbps} Mbps. Express that in {unit}, with 1 Mbps = 1000 Kbps and 1000 Mbps = 1 Gbps.", "Change {mbps} Mbps to {unit}, treating 1000 Kbps as 1 Mbps and 1000 Mbps as 1 Gbps.", "Find the {unit} equivalent of {mbps} Mbps using decimal factors: 1 Mbps = 1000 Kbps, 1000 Mbps = 1 Gbps."), answers=("{result}.", "{result}."), cases=cases),),
)
