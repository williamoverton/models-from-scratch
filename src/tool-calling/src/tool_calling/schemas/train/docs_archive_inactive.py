from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        cutoff = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 999), 3)
        offsets = [rng.randint(-60, -1), 0, rng.randint(1, 60)]
        rng.shuffle(offsets)
        entries = list(zip(ids, offsets))
        rng.shuffle(entries)
        yield {"cutoff": cutoff.isoformat(), "documents": "; ".join(f"D-{doc}={(cutoff + timedelta(days=offset)).isoformat()}" for doc, offset in entries)}


def prepare(*, task_id, case):
    cutoff = date.fromisoformat(case["cutoff"])
    entries = [entry.strip().split("=") for entry in case["documents"].split(";")]
    document = next(doc for doc, last in entries if date.fromisoformat(last) < cutoff)
    return Decision(fields=case, arguments={"document": document})


def resolve(document):
    return f"Archive requested for {document}"


SCHEMA = Schema(
    id="docs_archive_inactivity_cutoff",
    tool_names=('archive_document', 'request_document_archive', 'submit_document_archive', 'archive_document_by_id', 'record_archive_request', 'request_archive_by_id', 'submit_archive_request', 'queue_document_archive', 'register_document_archive', 'archive_named_document'),
    descriptions=('Request archival of the specified document.', 'Submit a document ID for archival.', 'Submit the specified document ID for archival.', 'Request archival of a document by ID.', 'Record an archive request for the given document.', 'Request an archive for the supplied document identifier.', 'Submit an archival request for a document.', 'Queue the specified document for archival.', 'Register a document archival request.', 'Request archival of the named document.'),
    parameters=(Parameter(names=("document", "document_id")),),
    tasks=(Task(id="archive", prompts=("Archive the one document last active strictly before {cutoff}. Entries are ID=last active date: {documents}.", "Using {cutoff} as the inactivity cutoff, archive the document whose last active date is earlier than the cutoff (not equal): {documents}. Entries are ID=date.", "From {documents} (ID=last active date), archive the document last active before {cutoff}, excluding equality.", "Find and archive the document whose last active date precedes {cutoff}, not one equal to it; ID=date entries: {documents}.", "The inactivity cutoff is {cutoff}. Archive the document last active strictly earlier from {documents} (ID=date).", "Which document was last active before {cutoff}? Archive it using {documents} (ID=last active date); equality does not qualify.", "Use the ID=last active date entries {documents} to archive the document inactive since strictly before {cutoff}.", "Archive the document with a last active date less than {cutoff}; {documents} lists ID=date and dates equal to the cutoff are excluded.", "Please archive the one document last active earlier than {cutoff}, not on it. Entries are ID=last active date: {documents}.", "Among {documents} (ID=last active date), archive the document whose last activity predates the exclusive cutoff {cutoff}.", "Identify and archive the document last active strictly before {cutoff}, using {documents} as ID=date pairs.", "For the cutoff {cutoff}, archive the document last active before, but not on, that date; {documents} gives ID=last active date."), answers=("{result}.", "{result}."), cases=cases),),
)
