from ...schema_types import Decision, Parameter, Schema, Task


OWNERS = {"D-301": "Avery Chen", "D-302": "Jordan Lee", "D-303": "Morgan Shah", "D-304": "Riley Diaz", "D-305": "Sam Okafor", "D-306": "Taylor Kim", "D-307": "Casey Patel", "D-308": "Alex Silva"}


def cases(rng, count):
    for _ in range(count):
        yield {"document": rng.choice(tuple(OWNERS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(document):
    return f"{document}: {OWNERS[document]}"


SCHEMA = Schema(
    id="docs_owner_by_id",
    tool_names=('get_document_owner', 'lookup_doc_owner', 'find_document_owner', 'get_doc_owner', 'lookup_registered_document_owner', 'query_document_owner', 'retrieve_document_owner', 'find_doc_owner', 'get_owner_by_document', 'lookup_owner_by_document'),
    descriptions=('Look up the owner of a document in the sample document registry.', 'Find the registered owner for a sample document ID.', 'Find the owner of a document in the sample registry.', 'Get the sample registry owner for a document ID.', 'Look up the registered owner of a sample document.', 'Query the sample registry for a document owner.', 'Retrieve the owner associated with a sample document ID.', 'Find a sample document’s registered owner.', 'Get the sample owner record for a document ID.', 'Look up a document ID’s owner in the sample registry.'),
    parameters=(Parameter(names=("document", "document_id", "doc_id")),),
    tasks=(Task(id="owner", prompts=("Who owns document {document}?", "Look up the owner of document {document}.", "Find the registered owner of document {document}.", "Who is listed as the owner of {document} in the document registry?", "Retrieve the owner record for document {document}.", "Which owner is associated with document {document}?", "Please check the document registry for the owner of {document}.", "Identify the owner of document {document}.", "What owner does the registry list for document {document}?", "Get the registered document owner for {document}.", "Can you find who owns the document with ID {document}?", "Consult the sample document registry and return the owner of {document}."), answers=("The owner record is {result}.", "The document registry lists {result}."), cases=cases),),
)
