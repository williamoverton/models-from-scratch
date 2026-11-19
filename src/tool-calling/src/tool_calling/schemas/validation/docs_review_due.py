from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        today = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 1000), 3)
        offsets = [rng.choice((-30, -1, 0)), rng.choice((1, 2, 30)), rng.choice((3, 10, 60))]
        rng.shuffle(offsets)
        documents = "; ".join(f"D-{doc}={(today + timedelta(days=offset)).isoformat()}" for doc, offset in zip(ids, offsets))
        yield {"documents": documents, "today": today.isoformat()}


def prepare(*, task_id, case):
    today = date.fromisoformat(case["today"])
    entries = [entry.strip().split("=") for entry in case["documents"].split(";")]
    document = next(document for document, due in entries if date.fromisoformat(due) <= today)
    return Decision(fields=case, arguments={"document": document})


def resolve(document):
    return f"Review-due document: {document}"


SCHEMA = Schema(
    id="docs_review_due_flag",
    tool_names=('report_review_due_document', 'acknowledge_due_document', 'return_review_due_id', 'report_selected_review_document', 'show_due_document_id', 'confirm_review_due_document', 'echo_due_document_id', 'report_document_due_flag', 'return_selected_due_document', 'acknowledge_review_flag'),
    descriptions=('Report the supplied document ID as due for review.', 'Return the selected review-due document identifier.', 'Acknowledge the provided document as due for review.', 'Show the selected document ID in a review-due report.', 'Report a review flag for the provided document ID.', 'Return the given document identifier with a review-due label.', 'Confirm the supplied document as the review-due selection.', 'Echo the selected document ID as due for review.', 'Present the given document as the review-due document.', 'Output a review-due label for the supplied document identifier.'),
    parameters=(Parameter(names=("document", "document_id", "selected_document")),),
    tasks=(Task(id="review", prompts=("As of {today}, flag the document due for review from these ID=review date entries: {documents}. A review is due on or after its review date.", "Today is {today}. Select and flag the one document due for review: {documents}. Each entry is ID=review date; the review date itself counts as due.", 'Today is {today}; flag the sole document in {documents} whose ID=review date is today or earlier.', 'From ID=review date entries {documents}, flag the document due as of {today}, including its review date.', 'As of {today}, which document is due for review? Flag it from {documents}, where entries are ID=review date and equality counts.', 'Flag the one review-due ID in {documents}; each entry is ID=review date, and dates on or before {today} are due.', 'The date is {today}. In {documents}, entries map ID to review date; flag the sole one due today or earlier.', 'Select and flag the document due by {today} from {documents} (ID=review date; the date itself counts).', 'Compare the ID=review date entries {documents} with {today}; flag the only document due on or before today.', 'For {today}, flag the unique due document from {documents}, interpreting entries as ID=review date and including today.', 'Which ID should be flagged as review-due on {today}? Use {documents}, formatted ID=review date; the review date is inclusive.', 'Given {documents} as ID=review date pairs, flag the one due by {today}, including a review date equal to today.'), answers=("{result}.", "The review flag is {result}."), cases=cases),),
)
