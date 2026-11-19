from ...schema_types import Decision, Parameter, Schema, Task


STATUSES = {"T-101": "open", "T-102": "pending", "T-103": "resolved", "T-104": "closed", "T-105": "open", "T-106": "pending", "T-107": "resolved", "T-108": "closed"}


def cases(rng, count):
    for _ in range(count):
        yield {"ticket": rng.choice(tuple(STATUSES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(ticket):
    return f"{ticket}: {STATUSES[ticket]}"


SCHEMA = Schema(
    id="support_ticket_status_lookup",
    tool_names=("get_ticket_status", "lookup_support_status", "find_ticket_status", "get_support_ticket_status", "lookup_ticket_status", "retrieve_ticket_status", "read_support_ticket_status", "find_support_status", "get_sample_ticket_status", "lookup_sample_ticket_status"),
    descriptions=("Look up the status of a ticket in the sample support registry.", "Find a sample support ticket's current status by its ID.", "Retrieve the status of a sample support ticket.", "Get a ticket's status from the sample registry.", "Find the status associated with a sample ticket ID.", "Read a sample support ticket's status.", "Return the status recorded for a sample ticket.", "Look up a ticket's current status in the sample registry.", "Identify the status of a sample ticket by ID.", "Get the sample registry status for the supplied ticket."),
    parameters=(Parameter(names=("ticket", "ticket_id", "case_number")),),
    tasks=(Task(id="status", prompts=("What is the status of support ticket {ticket}?", "Look up the current status for ticket {ticket}.", "Check the current status of support ticket {ticket}.", "How is ticket {ticket} currently listed?", "Find the status of ticket {ticket} in the support registry.", "Please retrieve the current status for support ticket {ticket}.", "What's the present status of {ticket}?", "Can you check ticket {ticket}'s support status?", "Look up the status recorded for support ticket {ticket}.", "Tell me the current status of ticket {ticket}.", "Find out what status ticket {ticket} has now.", "Which status is currently recorded for support ticket {ticket}?"), answers=("The ticket status is {result}.", "The support registry reports {result}."), cases=cases),),
)
