from ...schema_types import Decision, Parameter, Schema, Task


ISSUES = {
    "I-101": ("Aster", "Beacon"),
    "I-102": ("Current", "Drift", "Echo"),
    "I-103": ("Folio", "Grove"),
    "I-104": ("Harbor", "Islet", "Juniper"),
}


def cases(rng, count):
    for _ in range(count):
        yield {"issue": rng.choice(tuple(ISSUES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(issue):
    return ", ".join(ISSUES[issue])


SCHEMA = Schema(
    id="publishing_issue_contents",
    tool_names=("get_issue_contents", "list_issue_articles", "lookup_issue_articles", "find_issue_contents", "show_issue_articles", "retrieve_issue_contents", "query_issue_registry", "get_assigned_articles", "list_articles_in_issue", "read_issue_contents"),
    descriptions=("Look up articles assigned to an issue in the sample issue registry.", "List the assigned articles for a named issue.", "Retrieve the articles recorded for an issue in the sample registry.", "Find the contents assigned to the specified issue.", "Show the sample registry's article assignments for an issue.", "Query the issue registry for its assigned articles.", "Return the list of articles belonging to a recorded issue.", "Read an issue's article list from the sample registry.", "Identify articles assigned to the given issue.", "Get the registered article contents of an issue."),
    parameters=(Parameter(names=("issue", "issue_id")),),
    tasks=(Task(id="contents", prompts=("Which articles are assigned to issue {issue} in the sample registry?", "Look up the contents of issue {issue} in the sample issue registry.", "List the articles recorded for issue {issue} in the sample registry.", "What articles does the sample issue registry assign to {issue}?", "Retrieve the registered article contents of issue {issue}.", "Check the sample registry for articles assigned to {issue}.", "Show the article list for issue {issue} from the sample registry.", "Find all articles belonging to issue {issue} in the sample registry.", "Query the issue registry for the contents of {issue}.", "Which article titles are listed under {issue} in the sample issue registry?", "Read the assigned articles for issue {issue} from the registry.", "Give the sample registry's contents for issue {issue}."), answers=("Articles: {result}.", "Assigned articles: {result}."), cases=cases),),
)
