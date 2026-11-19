from ...schema_types import Decision, Parameter, Schema, Task


SEVERITIES = ("low", "medium", "high", "critical")


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"F-{n}" for n in range(100, 200)], 3)
        levels = rng.sample(SEVERITIES, 3)
        yield {"findings": "; ".join(f"{identifier}={level}" for identifier, level in zip(ids, levels))}


def prepare(*, task_id, case):
    findings = [entry.split("=") for entry in case["findings"].split("; ")]
    identifier, _ = max(findings, key=lambda entry: SEVERITIES.index(entry[1]))
    return Decision(fields=case, arguments={"finding": identifier})


def resolve(finding):
    return f"Prioritized finding: {finding}"


SCHEMA = Schema(
    id="security_finding_severity",
    tool_names=("prioritize_finding", "mark_security_finding", "prioritize_security_finding", "flag_finding_for_priority", "mark_finding_by_id", "prioritize_finding_by_id", "set_finding_priority", "mark_finding_as_priority", "prioritize_specified_finding", "select_priority_finding"),
    descriptions=("Prioritize a finding by ID.", "Mark a security finding.", "Prioritize the specified security finding.", "Mark a finding as prioritized.", "Set priority for the identified finding.", "Prioritize the supplied finding.", "Mark the given finding for priority.", "Select a security finding for prioritization.", "Prioritize a finding using its identifier.", "Mark the specified finding as a priority."),
    parameters=(Parameter(names=("finding", "finding_id")),),
    tasks=(Task(id="rank", prompts=("Findings: {findings}. Severity from lowest to highest is low, medium, high, critical. Prioritize the highest-severity finding.", "Prioritize the highest-ranked finding in {findings}; severity order from highest to lowest is critical, high, medium, low.", "Given {findings}, prioritize the most severe; low < medium < high < critical.", "Rank {findings} by severity and prioritize the top one: critical > high > medium > low.", "Select and prioritize the finding with maximum severity in {findings}; order: low, medium, high, critical.", "In {findings}, prioritize the finding ranked highest by critical, high, medium, then low.", "Mark the most severe finding among {findings}; severity rises from low to medium to high to critical.", "Use severity order critical > high > medium > low to prioritize one finding from {findings}.", "Which finding in {findings} has the highest severity? Prioritize it, using low < medium < high < critical.", "Prioritize the top-severity ID in {findings}; critical outranks high, which outranks medium, then low.", "From {findings}, prioritize the greatest severity on the scale low, medium, high, critical.", "Apply the ranking low < medium < high < critical to {findings} and prioritize the highest finding."), answers=("{result}.", "{result}."), cases=cases),),
)
