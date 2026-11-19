from ...schema_types import Decision, Parameter, Schema, Task


TEAMS = {"T-201": "Billing", "T-202": "Accounts", "T-203": "Technical Support", "T-204": "Fulfillment", "T-205": "Billing", "T-206": "Accounts", "T-207": "Technical Support", "T-208": "Fulfillment"}


def cases(rng, count):
    for _ in range(count):
        yield {"ticket": rng.choice(tuple(TEAMS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(ticket):
    return f"{ticket}: {TEAMS[ticket]}"


SCHEMA = Schema(
    id="support_assigned_team_lookup",
    tool_names=("get_ticket_team", "lookup_assignment", "find_ticket_team", "get_assigned_team", "lookup_ticket_team", "retrieve_ticket_assignment", "find_support_assignment", "get_support_ticket_team", "lookup_assigned_support_team", "read_ticket_team"),
    descriptions=("Look up the assigned team for a ticket in the sample support registry.", "Find the team assigned to a sample support ticket ID.", "Retrieve a sample ticket's assigned team.", "Get the team assignment for a sample ticket.", "Find a ticket's assigned support team in the sample registry.", "Read the sample support registry assignment by ticket ID.", "Return the team associated with a sample ticket.", "Look up a sample support ticket's team.", "Identify the assigned team for a sample ticket ID.", "Get a ticket's team from the sample support registry."),
    parameters=(Parameter(names=("ticket", "ticket_id", "case_number")),),
    tasks=(Task(id="team", prompts=("Which team is assigned to ticket {ticket}?", "Look up the assigned support team for {ticket}.", "Find the support team assigned to ticket {ticket}.", "Who is the assigned team for ticket {ticket}?", "Check which support team owns ticket {ticket}.", "Please retrieve the team assignment for {ticket}.", "What team is assigned to support ticket {ticket}?", "Look up the team handling ticket {ticket}.", "Identify the assigned support team for ticket {ticket}.", "Can you check the team assignment on {ticket}?", "Which support team is currently assigned to {ticket}?", "Find the recorded team assignment for ticket {ticket}."), answers=("The assignment is {result}.", "The support registry reports {result}."), cases=cases),),
)
