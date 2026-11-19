from ...schema_types import Decision, Parameter, Schema, Task


TARIFFS = {
    "standard": "0.22",
    "night": "0.12",
    "peak": "0.35",
    "green": "0.26",
    "weekend": "0.18",
}


def cases(rng, count):
    for _ in range(count):
        yield {"tariff": rng.choice(tuple(TARIFFS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"tariff": case["tariff"]})


def resolve(tariff):
    return f"The {tariff} sample tariff rate is ${TARIFFS[tariff]} per kWh."


SCHEMA = Schema(
    id="energy_tariff_rate_lookup",
    tool_names=("lookup_sample_tariff_rate", "get_sample_energy_rate", "find_sample_tariff_price", "retrieve_catalog_kwh_rate", "get_fixed_tariff_rate", "lookup_sample_plan_rate", "read_sample_electricity_rate", "find_catalog_tariff_rate", "retrieve_sample_unit_rate", "get_sample_tariff_price"),
    descriptions=("Look up the dollar-per-kWh rate for a tariff in the fixed sample catalog.", "Find the rate of the specified sample electricity tariff.", "Retrieve the named tariff's per-kWh rate from the sample catalog.", "Read the fixed sample electricity rate for a tariff.", "Find the dollar unit rate for a sample tariff.", "Return the catalog rate per kWh for the given sample plan.", "Look up the named tariff in the fixed sample rates.", "Get the sample catalog's electricity price for the supplied tariff.", "Retrieve a sample tariff's dollar-per-kWh price.", "Report the specified sample tariff's unit rate."),
    parameters=(Parameter(names=("tariff", "plan")),),
    tasks=(Task(id="rate", prompts=("What is the {tariff} rate per kWh in the sample tariff catalog?", "Look up the sample electricity rate for the {tariff} tariff.", "Find the per-kWh price of {tariff} in the sample tariff catalog.", "In the sample electricity catalog, what rate does the {tariff} tariff have?", "Retrieve the sample {tariff} tariff's dollar rate per kWh.", "How much per kWh is the {tariff} plan in the sample catalog?", "Give me the sample catalog electricity rate for {tariff}.", "Please find the {tariff} sample tariff's per-kWh rate.", "What electricity unit price is listed for {tariff} in the sample catalog?", "Look up {tariff} in the sample tariff catalog and report its kWh rate.", "Show the dollar-per-kWh rate for the sample {tariff} tariff.", "From the sample tariff catalog, retrieve the rate for {tariff}."), answers=("{result}", "Lookup result: {result}"), cases=cases),),
)
