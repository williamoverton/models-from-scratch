from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"hours": str(rng.randrange(1, 25)), "watts": str(rng.randrange(1, 3001))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="energy_use",
    tool_names=('energy_use', 'calculate_kwh', 'compute_energy_consumption', 'appliance_energy_use', 'watts_hours_to_kwh', 'calculate_appliance_kwh', 'get_energy_consumption', 'compute_kilowatt_hours', 'power_duration_to_kwh', 'calculate_electricity_use'),
    descriptions=('Calculate kilowatt-hours from appliance watts and hours of use.', 'Find energy consumption in kWh for a power rating and duration.', 'Compute appliance energy in kWh from watts and hours.', 'Convert a power rating in watts and duration in hours to kilowatt-hours.', 'Calculate electricity consumption from watts multiplied by hours, in kWh.', 'Return the energy used in kilowatt-hours for a wattage and duration.', 'Find the kWh consumed by an appliance at the given watts over the given hours.', 'Compute kilowatt-hours for a specified power in watts and time in hours.', 'Determine energy usage in kWh from the supplied wattage and operating hours.', 'Get energy consumption in kilowatt-hours for the given hours and watts.'),
    parameters=(
        Parameter(names=("hours", "duration_hours")),
        Parameter(names=("watts", "power_watts")),
    ),
    tasks=(Task(id="consumption", prompts=("How many kWh does a {watts} watt appliance use in {hours} hours?", "Calculate energy for {hours} hours at {watts} watts.", 'Compute the kWh consumed by a {watts}-watt appliance running for {hours} hours.', 'An appliance draws {watts} watts for {hours} hours; give its energy use in kWh.', 'Convert {hours} hours at {watts} watts into kilowatt-hours.', 'What energy in kWh results from running {watts} watts for {hours} hours?', 'Find the electricity consumption in kWh for {watts} watts over {hours} hours.', 'For {hours} hours of operation at {watts} watts, determine kWh used.', 'Express in kilowatt-hours the energy of a {watts}-watt device used for {hours} hours.', 'A device operates {hours} hours at {watts} watts. How many kWh is that?', 'Work out kWh for an appliance rated {watts} watts and used for {hours} hours.', 'Calculate kilowatt-hours given power of {watts} watts and runtime of {hours} hours.'), answers=("It uses {result} kWh.", "The energy consumption is {result} kWh."), cases=cases),),
)


def resolve(hours, watts):
    watt_hours = int(hours) * int(watts)
    return f"{watt_hours // 1000}.{watt_hours % 1000:03d}"
