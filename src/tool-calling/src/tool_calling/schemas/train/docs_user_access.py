from ...schema_types import Decision, Parameter, Schema, Task


ACCESS = {
    "D-101": {"Ava": "editor", "Ben": "viewer", "Cara": "none"},
    "D-102": {"Ava": "none", "Ben": "editor", "Cara": "viewer"},
    "D-103": {"Ava": "viewer", "Ben": "none", "Cara": "editor"},
    "D-104": {"Ava": "editor", "Ben": "editor", "Cara": "viewer"},
}


def cases(rng, count):
    for _ in range(count):
        yield {"document": rng.choice(tuple(ACCESS)), "user": rng.choice(("Ava", "Ben", "Cara"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(document, user):
    return f"{user} on {document}: {ACCESS[document][user]}"


SCHEMA = Schema(
    id="docs_user_access_lookup",
    tool_names=('get_document_access', 'lookup_document_permission', 'find_document_access', 'get_user_document_access', 'lookup_user_permission', 'query_document_access', 'retrieve_document_permission', 'check_sample_document_access', 'find_user_document_permission', 'get_sample_access'),
    descriptions=("Look up a user's access to a document in the sample registry.", 'Retrieve the sample document permission for a specified user.', 'Find a user’s document access in the sample registry.', 'Get the specified user’s access to a sample document.', 'Look up a user’s sample permission on a document.', 'Query the sample registry for a user’s document access.', 'Retrieve a user’s permission for the specified sample document.', 'Check the sample registry access for a document and user.', 'Find the specified user’s sample document permission.', 'Get a user’s sample access for the given document.'),
    parameters=(Parameter(names=("document", "document_id")), Parameter(names=("user", "user_name"))),
    tasks=(Task(id="access", prompts=("What access does {user} have to document {document} in the sample registry?", "Look up {user}'s sample permission for {document}.", "Check the sample registry for {user}'s access to document {document}.", "Which permission does {user} have on {document} in the sample registry?", "Find the sample document access for user {user} and document {document}.", "Look up the permission for {user} on document {document} in the sample registry.", "Does the sample registry list access for {user} to {document}? Report the permission.", "Retrieve {user}'s registered sample access to document {document}.", "For document {document}, what permission is recorded for {user} in the sample registry?", "Consult the sample registry and report {user}'s access to {document}.", "What is the sample permission of user {user} for document {document}?", "Get the access record for {user} on {document} from the sample registry."), answers=("The registry reports {result}.", "Access: {result}."), cases=cases),),
)
