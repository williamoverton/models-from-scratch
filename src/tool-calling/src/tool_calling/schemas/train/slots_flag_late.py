from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        cutoff = rng.randrange(11, 16) * 60
        times = rng.sample(range(cutoff - 180, cutoff + 1, 30), 2) + [cutoff + rng.randrange(1, 7) * 30]
        names = rng.sample(("Avery", "Blair", "Casey", "Devon", "Emery", "Frankie"), 3)
        entries = list(zip(names, times))
        rng.shuffle(entries)
        yield {"cutoff": f"{cutoff // 60:02d}:{cutoff % 60:02d}", "appointments": "; ".join(f"{name} {t // 60:02d}:{t % 60:02d}" for name, t in entries)}


def prepare(*, task_id, case):
    name, _ = next(item.split() for item in case["appointments"].split("; ") if item.split()[1] > case["cutoff"])
    return Decision(fields=case, arguments={"appointment": name})


SCHEMA = Schema(
    id="schedule_flag_after_cutoff",
    tool_names=("flag_late_appointment", "mark_after_cutoff", "flag_named_appointment", "record_appointment_flag", "acknowledge_flagged_appointment", "mark_named_appointment", "report_flagged_visit", "submit_appointment_for_review", "flag_selected_visit", "identify_appointment_for_review"),
    descriptions=("Acknowledge the appointment selected for flagging.", "Mark a specified appointment for review.", "Flag the supplied appointment name.", "Return an acknowledgement for the named appointment flag.", "Record the specified appointment as flagged.", "Identify the named appointment selected for review.", "Mark the provided appointment name for flagging.", "Report the appointment supplied for review.", "Acknowledge the selected appointment by name.", "Return the named appointment as flagged."),
    parameters=(Parameter(names=("appointment", "name")),),
    tasks=(Task(id="flag", prompts=("Appointments: {appointments}. Flag the one starting strictly after {cutoff}.", "Which appointment in {appointments} starts later than {cutoff}? Flag it; a start exactly at the cutoff does not qualify.", "Flag the appointment in {appointments} whose start exceeds {cutoff}; equality does not count.", "From {appointments}, flag the visit strictly later than {cutoff}.", "Identify and flag the appointment starting after, not at, {cutoff}: {appointments}.", "Review {appointments} and flag the one with a start time greater than {cutoff}.", "Which entry in {appointments} begins strictly after {cutoff}? Flag it.", "Flag the named appointment beyond the {cutoff} cutoff in {appointments}; exclude equal times.", "In {appointments}, mark the appointment whose start is later than {cutoff}, not equal.", "Find the appointment in {appointments} that starts strictly subsequent to {cutoff}, and flag it.", "Please flag the visit starting after {cutoff} among {appointments}; the boundary is excluded.", "Among {appointments}, flag the one that begins strictly past {cutoff}."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(appointment):
    return f"Flagged {appointment}."
