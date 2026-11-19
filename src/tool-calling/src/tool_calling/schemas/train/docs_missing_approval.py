from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        flags = ["approved", "approved", "missing"]
        rng.shuffle(flags)
        entries = list(zip(ids, flags))
        rng.shuffle(entries)
        yield {"approvals": "; ".join(f"D-{doc}={flag}" for doc, flag in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=") for entry in case["approvals"].split(";")]
    document = next(doc for doc, flag in entries if flag == "missing")
    return Decision(fields=case, arguments={"document": document})


def resolve(document):
    return f"Flagged document: {document}"


SCHEMA = Schema(
    id="docs_missing_approval_flag",
    tool_names=('flag_document', 'mark_document_for_review', 'flag_document_for_review', 'mark_document_review', 'record_document_flag', 'submit_document_flag', 'request_document_review', 'flag_document_id', 'register_document_flag', 'add_document_review_flag'),
    descriptions=('Flag the specified document for review.', 'Mark a document identifier for review.', 'Flag the supplied document ID for review.', 'Mark the specified document for review.', 'Record a review flag for the supplied document.', 'Submit the selected document identifier as flagged.', 'Request review of the given document ID.', 'Flag the specified document identifier for review.', 'Register a review flag for a document.', 'Add a review flag for the given document ID.'),
    parameters=(Parameter(names=("document", "document_id")),),
    tasks=(Task(id="flag", prompts=("Flag the document whose approval is missing. Entries are document ID=approval status: {approvals}.", "From {approvals}, flag the one document with a missing approval; the values are ID=approval status.", "Flag the document marked with a missing approval in {approvals} (document ID=approval status).", "Which document lacks approval? Flag it using these ID=approval status entries: {approvals}.", "Review {approvals}, where each entry is document ID=approval status, and flag the one missing approval.", "Find and flag the document whose approval status is missing; ID=status records: {approvals}.", "Using {approvals} as document ID=approval status pairs, flag the document without approval.", "Please flag the document with missing approval from the ID=approval status list {approvals}.", "The approval report is {approvals} (document ID=approval status). Flag the document missing approval.", "Identify the document lacking approval in {approvals} (ID=approval status) and flag it.", "From these document ID=approval status values, flag the one with missing approval: {approvals}.", "Check {approvals}, a document ID=approval status report, and flag the document whose approval is missing."), answers=("{result}.", "Review recorded for {result}."), cases=cases),),
)
