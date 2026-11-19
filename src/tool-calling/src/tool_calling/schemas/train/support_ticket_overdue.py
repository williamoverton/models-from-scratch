from datetime import datetime, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        now = datetime(2026, 1, 1) + timedelta(minutes=rng.randrange(365 * 24 * 60))
        ids = rng.sample(range(100, 1000), 3)
        offsets = [rng.choice((-1440, -60, -1)), 0, rng.choice((1, 60, 1440))]
        rng.shuffle(offsets)
        tickets = "; ".join(f"T-{ticket}={(now + timedelta(minutes=offset)).isoformat(timespec='minutes')}" for ticket, offset in zip(ids, offsets))
        yield {"tickets": tickets, "current": now.isoformat(timespec="minutes")}


def prepare(*, task_id, case):
    current = datetime.fromisoformat(case["current"])
    entries = [entry.strip().split("=") for entry in case["tickets"].split(";")]
    ticket = next(ticket for ticket, due in entries if datetime.fromisoformat(due) < current)
    return Decision(fields=case, arguments={"ticket": ticket})


def resolve(ticket):
    return f"Selected overdue ticket: {ticket}"


SCHEMA = Schema(
    id="support_ticket_overdue_at_time",
    tool_names=("select_overdue_ticket", "report_overdue_ticket", "return_overdue_ticket", "record_overdue_ticket", "submit_overdue_ticket", "provide_overdue_ticket", "identify_overdue_ticket", "confirm_overdue_ticket", "acknowledge_overdue_ticket", "report_overdue_ticket_id"),
    descriptions=("Report the selected overdue ticket ID.", "Return the ID selected as overdue.", "Record the ticket selected as overdue.", "Submit the selected overdue ticket ID.", "Provide the overdue ticket identifier.", "Confirm the ticket selected as overdue.", "Acknowledge the overdue ticket selection.", "Report which ticket was selected as overdue.", "Return the supplied overdue ticket ID.", "Identify the selected overdue ticket."),
    parameters=(Parameter(names=("ticket", "ticket_id", "selected_ticket")),),
    tasks=(Task(id="overdue", prompts=("At {current}, select the overdue ticket from these ID=due time entries: {tickets}. All times use the same timezone; overdue means strictly before the current time.", "Select the one overdue ticket at {current}: {tickets}. Each entry is ID=due time, all times share a timezone, and a ticket due exactly now is not overdue.", "Which ticket in {tickets} is overdue at {current}? Entries are ID=due time in the same timezone; only times strictly before now count.", "At {current}, find the overdue ticket in {tickets}. Each entry is ID=due time, all times share a timezone, and a due time equal to now is not overdue.", "From {tickets}, select the ticket due strictly before {current}. Entries are ID=due time and all times use the same timezone.", "Identify the overdue ticket at {current} using {tickets}, formatted ID=due time. All times are in one timezone, and overdue excludes due exactly now.", "Which ID is overdue at {current} in {tickets}? The entries are ID=due time, times share a timezone, and due must be strictly earlier than now.", "Select the ticket whose due time is strictly before {current} from {tickets}; entries are ID=due time and all times use the same timezone.", "Given the ID=due time entries {tickets}, select the overdue ticket at {current}. Same timezone throughout; a ticket due exactly now is not overdue.", "Find the overdue ticket from {tickets} at {current}; all times share a timezone, entries are ID=due time, and only strictly earlier due times qualify.", "At time {current}, choose the ticket overdue in {tickets}. Each entry is ID=due time in the same timezone, and overdue means due strictly before now.", "Use {current} and the ID=due time entries {tickets} to select the overdue ticket. Times share a timezone; equality with the current time is not overdue."), answers=("{result}.", "The selection is {result}."), cases=cases),),
)
