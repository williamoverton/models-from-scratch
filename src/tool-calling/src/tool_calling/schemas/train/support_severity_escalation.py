from ...schema_types import Decision, Parameter, Schema, Task


TEAM_BY_SEVERITY = {'critical': 'Incident Response', 'high': 'Tier 2', 'medium': 'Support', 'low': 'Service Desk'}


def cases(rng, count):
    for ticket in rng.sample(range(100000, 1000000), count):
        yield {'severity': rng.choice(tuple(TEAM_BY_SEVERITY)), 'ticket': f'T-{ticket}'}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={'team': TEAM_BY_SEVERITY[case['severity']]})


def resolve(team):
    return f'Escalated to team: {team}'


SCHEMA = Schema(
    id='support_escalate_by_severity',
    tool_names=('escalate_to_team', 'route_escalation', 'record_escalation_team', 'select_escalation_team', 'report_escalation_team', 'acknowledge_escalation_team', 'submit_escalation_team', 'confirm_escalation_team', 'provide_escalation_team', 'return_escalation_team'),
    descriptions=('Escalate to the supplied team.', 'Route the escalation to a team.', 'Record the selected escalation team.', 'Report the supplied team for escalation.', 'Acknowledge the chosen escalation team.', 'Return the selected escalation team.', 'Submit the team selected for escalation.', 'Confirm the supplied escalation team.', 'Provide the team for the escalation.', 'Identify the team selected for escalation.'),
    parameters=(Parameter(names=('team', 'team_name')),),
    tasks=(Task(id='escalation', prompts=('Escalate ticket {ticket}, a {severity} severity issue, according to this rule: critical -> Incident Response; high -> Tier 2; medium -> Support; low -> Service Desk. Select the team.', 'For ticket {ticket} with severity {severity}, route the escalation using critical=Incident Response, high=Tier 2, medium=Support, low=Service Desk.', 'Which team should receive ticket {ticket} at {severity} severity? Use critical -> Incident Response, high -> Tier 2, medium -> Support, low -> Service Desk.', 'Select the escalation team for {ticket}, severity {severity}: critical goes to Incident Response, high to Tier 2, medium to Support, low to Service Desk.', 'Route ticket {ticket} ({severity}) according to critical=Incident Response, high=Tier 2, medium=Support, low=Service Desk.', 'Ticket {ticket} has {severity} severity. Escalate it to the team defined by critical: Incident Response; high: Tier 2; medium: Support; low: Service Desk.', 'Determine the escalation team for {ticket} at severity {severity}, using critical -> Incident Response, high -> Tier 2, medium -> Support, low -> Service Desk.', 'Apply the severity routing rule to ticket {ticket} ({severity}): critical to Incident Response, high to Tier 2, medium to Support, low to Service Desk.', 'Where should ticket {ticket} be escalated for {severity} severity? The mapping is critical=Incident Response, high=Tier 2, medium=Support, low=Service Desk.', 'Choose a team for escalating {ticket}, severity {severity}. Critical maps to Incident Response, high to Tier 2, medium to Support, and low to Service Desk.', 'Escalate {ticket} at {severity} severity using this mapping: critical -> Incident Response; high -> Tier 2; medium -> Support; low -> Service Desk.', 'For issue {ticket} rated {severity}, select the escalation team: critical=Incident Response, high=Tier 2, medium=Support, low=Service Desk.'), answers=('{result}.', '{result}.'), cases=cases),),
)
