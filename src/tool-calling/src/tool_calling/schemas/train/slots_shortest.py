from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        durations = rng.sample(range(10, 100, 5), 3)
        names = rng.sample(("consultation", "checkup", "follow-up", "screening", "assessment", "therapy"), 3)
        entries = list(zip(names, durations))
        rng.shuffle(entries)
        yield {"options": "; ".join(f"{name}: {minutes} minutes" for name, minutes in entries)}


def prepare(*, task_id, case):
    options = [item.split(": ") for item in case["options"].split("; ")]
    name, _ = min(options, key=lambda item: int(item[1].split()[0]))
    return Decision(fields=case, arguments={"appointment": name})


SCHEMA = Schema(
    id="schedule_shortest_appointment",
    tool_names=("select_shortest_appointment", "choose_brief_visit", "record_appointment_choice", "acknowledge_selected_visit", "report_selected_appointment", "confirm_visit_selection", "register_appointment_type", "submit_visit_choice", "identify_selected_visit", "select_appointment_type"),
    descriptions=("Acknowledge the selected appointment.", "Select an appointment type.", "Return the supplied appointment type as selected.", "Acknowledge the chosen visit type.", "Record the specified appointment as the selection.", "Report the provided appointment type as selected.", "Confirm the supplied visit type as the choice.", "Identify the selected appointment by its name.", "Return an acknowledgement of the appointment choice.", "Register the specified appointment type as selected."),
    parameters=(Parameter(names=("appointment", "visit_type")),),
    tasks=(Task(id="shortest", prompts=("Appointment options: {options}. Select the shortest.", "Choose the appointment with the least duration from {options}.", "Select the briefest appointment among {options}.", "Which visit in {options} takes the fewest minutes? Select it.", "Pick the minimum-duration appointment from {options}.", "Compare {options} and select the shortest visit.", "From {options}, choose the appointment that lasts the least time.", "Identify and select the quickest appointment: {options}.", "Select the appointment with the smallest duration in {options}.", "Which of {options} is shortest? Choose that appointment.", "Please select the least lengthy visit from {options}.", "Choose the appointment requiring the fewest minutes: {options}."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(appointment):
    return f"Selected {appointment}."
