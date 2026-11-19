from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 1000), 3)
        statuses = ['unassigned', 'assigned to Accounts', 'assigned to Technical Support']
        entries = list(zip(ids, statuses))
        rng.shuffle(entries)
        yield {'tickets': '; '.join(f'T-{ident}: {status}' for ident, status in entries)}


def prepare(*, task_id, case):
    entries = [entry.split(': ') for entry in case['tickets'].split('; ')]
    ticket = next(ident for ident, status in entries if status == 'unassigned')
    return Decision(fields=case, arguments={'ticket': ticket})


def resolve(ticket):
    return f'Assigned {ticket} to Billing'


SCHEMA = Schema(
    id='support_assign_unassigned_to_billing',
    tool_names=('assign_ticket_to_billing', 'route_ticket_to_billing', 'send_ticket_to_billing', 'assign_billing_ticket', 'direct_ticket_to_billing', 'allocate_ticket_to_billing', 'transfer_ticket_to_billing', 'place_ticket_with_billing', 'submit_ticket_to_billing', 'set_ticket_billing_assignment'),
    descriptions=('Assign the supplied ticket ID to Billing.', 'Route a ticket to the Billing team.', 'Send the selected ticket to Billing.', 'Allocate the supplied ticket to Billing.', 'Direct the ticket to the Billing team.', 'Assign the specified ticket to Billing.', 'Place the ticket with Billing.', 'Set the ticket assignment to Billing.', 'Route the supplied ticket ID to Billing.', 'Assign a support ticket to the Billing team.'),
    parameters=(Parameter(names=('ticket', 'ticket_id')),),
    tasks=(Task(id='assign', prompts=('Assign the unassigned ticket to Billing: {tickets}.', 'From {tickets}, route the ticket without an assigned team to Billing.', 'Which ticket in {tickets} has no assigned team? Assign it to Billing.', 'Send the unassigned ticket from {tickets} to the Billing team.', 'Review {tickets} and assign the ticket with no team to Billing.', 'Among {tickets}, find the ticket lacking an assignment and route it to Billing.', 'Please assign the ticket without an assigned team in {tickets} to Billing.', 'Use {tickets} to identify the unassigned ticket, then send it to Billing.', 'Billing should receive the unassigned ticket in this list: {tickets}. Assign it.', 'For {tickets}, route the ticket that has no assigned team to Billing.', 'Find the unassigned entry in {tickets} and assign its ticket to Billing.', 'Assign Billing to the ticket with no team in {tickets}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
