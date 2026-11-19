from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    appliances = ("heater", "fan", "washer", "dryer", "fridge", "oven", "pump")
    for _ in range(count):
        names = rng.sample(appliances, 3)
        costs = rng.sample(range(100, 10001), 3)
        rows = list(zip(names, costs))
        yield {"rows": rows, "options": "; ".join(f"{name}: ${cost // 100}.{cost % 100:02d}" for name, cost in rows)}


def prepare(*, task_id, case):
    appliance, _ = max(case["rows"], key=lambda row: row[1])
    return Decision(fields=case, arguments={"appliance": appliance})


def resolve(appliance):
    return f"Flagged appliance: {appliance}."


SCHEMA = Schema(
    id="energy_largest_appliance_cost",
    tool_names=("flag_highest_cost_appliance", "mark_costliest_device", "record_costly_appliance", "flag_selected_appliance", "mark_selected_device", "acknowledge_appliance_flag", "record_appliance_identifier", "flag_energy_cost_device", "confirm_appliance_selection", "mark_appliance_by_name"),
    descriptions=("Flag the specified appliance by name.", "Mark an appliance identifier.", "Record the appliance selected for flagging.", "Flag the supplied appliance.", "Mark the named device.", "Acknowledge the selected appliance.", "Record an appliance identifier for the cost flag.", "Confirm which appliance is flagged.", "Mark the provided appliance name.", "Report the appliance to flag."),
    parameters=(Parameter(names=("appliance", "device")),),
    tasks=(Task(id="largest", prompts=("Flag the appliance with the largest electricity cost: {options}.", "Mark the appliance with the highest listed energy cost: {options}.", "Which appliance has the highest electricity cost? Flag it: {options}.", "From {options}, flag the appliance with the greatest energy cost.", "Compare appliance electricity costs {options} and mark the most expensive one.", "Identify and flag the costliest appliance by electricity cost: {options}.", "These are appliance energy costs: {options}. Mark the appliance with the largest cost.", "Flag the device with the maximum listed electricity cost among {options}.", "Choose and mark the appliance incurring the highest electricity cost: {options}.", "Which appliance costs the most in electricity? Mark it using {options}.", "Flag the highest-cost appliance based on these energy costs: {options}.", "Review {options} and mark the appliance with the largest electricity expense."), answers=("{result}", "Done. {result}"), cases=cases),),
)
