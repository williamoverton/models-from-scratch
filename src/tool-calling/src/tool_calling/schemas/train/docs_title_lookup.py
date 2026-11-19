from ...schema_types import Decision, Parameter, Schema, Task


DOCUMENTS = {"Onboarding Guide": "D-401", "Incident Handbook": "D-402", "Release Checklist": "D-403", "Travel Policy": "D-404", "Security Guide": "D-405", "Style Manual": "D-406", "Support Playbook": "D-407", "Research Notes": "D-408"}


def cases(rng, count):
    for _ in range(count):
        yield {"title": rng.choice(tuple(DOCUMENTS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(title):
    return f"{title}: {DOCUMENTS[title]}"


SCHEMA = Schema(
    id="docs_lookup_by_title",
    tool_names=('find_document', 'lookup_document_title', 'find_document_by_title', 'get_document_id_by_title', 'lookup_exact_title', 'search_document_catalog', 'find_catalog_document', 'lookup_title_id', 'get_catalog_document_id', 'query_document_by_title'),
    descriptions=('Find the document ID for an exact title in the sample document catalog.', 'Look up an exact document title in the sample registry.', 'Find a document ID by exact title in the sample catalog.', 'Get the sample document ID for an exact title.', 'Look up an exact title in the sample document catalog.', 'Search the sample catalog for the exact document title.', 'Find the sample catalog document ID for the supplied exact title.', 'Look up the ID associated with an exact sample title.', 'Get a document ID from the sample catalog by exact title.', 'Query the sample document registry by exact title.'),
    parameters=(Parameter(names=("title", "document_title", "name")),),
    tasks=(Task(id="lookup", prompts=("Find the document titled '{title}'.", "What is the document ID for '{title}'?", "Look up the document ID for the exact title '{title}'.", "Which document in the sample catalog has the title '{title}'?", "Find the catalog record matching the exact title '{title}'.", "Retrieve the document identifier for '{title}'.", "Search the sample document catalog for the exact title '{title}'.", "What document is listed under the title '{title}'?", "Please find the ID of the document titled '{title}'.", "In the document catalog, look up '{title}' by its exact title.", "Identify the document with the exact title '{title}'.", "Return the sample catalog document ID associated with '{title}'."), answers=("The document record is {result}.", "The catalog lists {result}."), cases=cases),),
)
