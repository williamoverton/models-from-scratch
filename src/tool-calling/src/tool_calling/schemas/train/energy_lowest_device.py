from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    devices = ("heater", "fan", "washer", "dryer", "fridge", "oven", "pump")
    for _ in range(count):
        rows = list(zip(rng.sample(devices, 3), rng.sample(range(1, 101), 3)))
        yield {"rows": rows, "options": "; ".join(f"{device}: {usage} kWh" for device, usage in rows)}


def prepare(*, task_id, case):
    device, _ = min(case["rows"], key=lambda row: row[1])
    return Decision(fields=case, arguments={"device": device})


def resolve(device):
    return f"Selected device: {device}."


SCHEMA = Schema(
    id="energy_lowest_device_usage",
    tool_names=("select_lowest_usage_device", "choose_least_consuming_device", "record_selected_device", "confirm_device_choice", "select_energy_device", "acknowledge_device_selection", "record_appliance_choice", "choose_device_by_name", "report_selected_device", "confirm_appliance_identifier"),
    descriptions=("Select a device by its identifier.", "Record the selected device.", "Confirm the supplied device choice.", "Acknowledge the named appliance selection.", "Record the device chosen for its usage.", "Select the supplied appliance identifier.", "Report the selected energy device.", "Confirm which device was chosen.", "Record the provided device name.", "Acknowledge a device choice."),
    parameters=(Parameter(names=("device", "appliance")),),
    tasks=(Task(id="lowest", prompts=("Select the device with the lowest electricity usage: {options}.", "Choose the device that used the fewest kWh: {options}.", "Which device consumed the least electricity? {options}.", "From {options}, select the appliance with the smallest kWh usage.", "Pick the lowest-usage device from these electricity readings: {options}.", "Compare the devices' kWh usage and choose the least consuming one: {options}.", "Identify the device with minimum electricity consumption among {options}.", "Device usage is {options}. Select the one using the fewest kWh.", "Which of these devices used the least energy? {options}.", "Choose the appliance with the lowest listed electricity use: {options}.", "Find the smallest kWh reading and select its device: {options}.", "Select the least electricity-consuming device using these values: {options}."), answers=("{result}", "Choice recorded. {result}"), cases=cases),),
)
