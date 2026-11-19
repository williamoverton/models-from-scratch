from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        times = sorted(rng.sample(range(8 * 60, 18 * 60, 30), 4))
        cutoff = rng.randrange(times[0], times[-1])
        values = [f"{t // 60:02d}:{t % 60:02d}" for t in times]
        rng.shuffle(values)
        yield {"slots": ", ".join(values), "cutoff": f"{cutoff // 60:02d}:{cutoff % 60:02d}"}


def prepare(*, task_id, case):
    slot = min(t for t in case["slots"].split(", ") if t > case["cutoff"])
    return Decision(fields=case, arguments={"slot": slot})


SCHEMA = Schema(
    id="schedule_book_after",
    tool_names=("select_booking_slot", "request_appointment", "request_booking_time", "record_booking_request", "submit_appointment_request", "acknowledge_booking_slot", "request_selected_slot", "record_requested_appointment", "submit_booking_slot", "report_requested_time"),
    descriptions=("Record the selected appointment time in a booking request.", "Acknowledge an appointment time requested for booking.", "Return an acknowledgement of the supplied booking time.", "Request an appointment at the specified slot time.", "Record a request for the selected appointment time.", "Acknowledge the provided time as a booking request.", "Submit the specified appointment time as requested.", "Report the time requested for an appointment.", "Identify the selected slot as the requested booking time.", "Return the supplied slot time as a booking request."),
    parameters=(Parameter(names=("slot", "time")),),
    tasks=(Task(id="book", prompts=("The open slots are {slots}. Request the earliest slot strictly after {cutoff}.", "From {slots}, choose and request the earliest open appointment later than {cutoff}; equal times do not count.", "Request the first available time after {cutoff}, excluding the cutoff itself, from {slots}.", "Among {slots}, request the earliest time greater than {cutoff}.", "Choose and request the soonest slot strictly later than {cutoff}: {slots}.", "Using {slots}, request the first slot beyond {cutoff}, not at it.", "Which of {slots} is earliest after {cutoff}? Request it; equality is excluded.", "Request the minimum available time in {slots} that exceeds {cutoff}.", "Find and request the earliest appointment after {cutoff} in {slots}; the cutoff does not qualify.", "The choices are {slots}; request the earliest one later than, not equal to, {cutoff}.", "From the available times {slots}, request the first strictly subsequent to {cutoff}.", "Please request the earliest slot in {slots} occurring strictly after {cutoff}."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(slot):
    return f"Booking requested for {slot}."
