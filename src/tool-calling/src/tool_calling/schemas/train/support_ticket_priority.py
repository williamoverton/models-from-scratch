from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        scores = rng.sample(range(1, 100), 3)
        yield {"tickets": "; ".join(f"T-{ticket}={score}" for ticket, score in zip(ids, scores))}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["tickets"].split(";")]
    ticket, _ = max(entries, key=lambda entry: int(entry[1]))
    return Decision(fields=case, arguments={"ticket": ticket})


def resolve(ticket):
    return f"Selected ticket: {ticket}"


SCHEMA = Schema(
    id="support_highest_priority_ticket",
    tool_names=("select_priority_ticket", "report_ticket_selection", "return_priority_ticket", "record_priority_selection", "submit_priority_ticket", "provide_selected_ticket", "confirm_priority_ticket", "acknowledge_ticket_selection", "report_priority_ticket", "return_selected_ticket_id"),
    descriptions=("Report the selected ticket ID.", "Return the ticket ID selected for priority handling.", "Record the ticket selected for priority handling.", "Submit the selected priority ticket ID.", "Provide the selected ticket identifier.", "Confirm the priority ticket selection.", "Acknowledge the selected ticket ID.", "Report the ticket chosen for priority handling.", "Return the supplied priority ticket ID.", "Identify the ticket selected for priority handling."),
    parameters=(Parameter(names=("ticket", "ticket_id", "selected_ticket")),),
    tasks=(Task(id="highest", prompts=("Tickets and priority scores: {tickets}. The highest numeric score has highest priority. Select that ticket.", "Using higher score as higher priority, select the highest-priority ticket from {tickets}.", "Which ticket in {tickets} has the highest numeric priority score? Select it.", "From these ticket scores, {tickets}, pick the highest-priority ticket; larger numbers mean higher priority.", "Select the ticket with the greatest numeric score from {tickets}; higher scores indicate higher priority.", "Rank the tickets in {tickets} by numeric score and select the highest, since a higher score means higher priority.", "Find the top-priority ticket in {tickets}, where priority increases with the numeric score.", "Given {tickets}, identify the ticket whose numeric priority score is highest.", "Which ticket should be selected from {tickets} if the highest numeric score is highest priority?", "Choose the highest-priority entry in {tickets}; priority is determined by the largest numeric score.", "For {tickets}, select the ticket with the largest priority score, treating higher numbers as higher priority.", "Ticket scores are {tickets}. Return the ticket at the highest numeric score, which has highest priority."), answers=("{result}.", "The selection is {result}."), cases=cases),),
)
