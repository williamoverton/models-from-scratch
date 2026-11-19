from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        versions = rng.sample(range(1, 21), 3)
        entries = list(zip(ids, versions))
        rng.shuffle(entries)
        yield {"versions": "; ".join(f"D-{doc}=v{version}" for doc, version in entries)}


def prepare(*, task_id, case):
    entries = [entry.strip().split("=v") for entry in case["versions"].split(";")]
    document = max(entries, key=lambda entry: int(entry[1]))[0]
    return Decision(fields=case, arguments={"document": document})


def resolve(document):
    return f"Selected document: {document}"


SCHEMA = Schema(
    id="docs_highest_version_select",
    tool_names=('report_version_selection', 'identify_document_version', 'report_selected_document', 'record_document_selection', 'return_document_selection', 'identify_selected_document', 'report_document_id', 'return_selected_document', 'select_document_id', 'register_document_selection'),
    descriptions=('Report the selected document ID.', 'Return a selected document identifier without changing the document.', 'Report the supplied selected document ID without changing it.', 'Record the selected document identifier without changing the document.', 'Return the given document selection without modifying the document.', 'Identify the selected document by its supplied ID.', 'Report a selected document identifier without changing the document.', 'Return the supplied selected document ID.', 'Report the specified document as the selection.', 'Register the supplied document selection without modifying it.'),
    parameters=(Parameter(names=("document", "document_id")),),
    tasks=(Task(id="highest", prompts=("Select the document with the highest numeric version from these ID=version entries: {versions}.", "Which document has the greatest version number? Entries are ID=version: {versions}.", "From {versions} (ID=version), select the document with the largest numeric version.", "Identify the document with the highest numeric version in these ID=version pairs: {versions}.", "Choose the greatest version number numerically and report its document ID: {versions} (ID=version).", "Using {versions} as document ID=version entries, select the document with the maximum numeric version.", "Which document should be selected by highest numeric version? The ID=version list is {versions}.", "Select the highest-version document from {versions}; entries are ID=version and versions are numeric.", "Find the largest numeric version in {versions} (ID=version) and select its document.", "Given document ID=version records {versions}, select the one with the greatest numeric version.", "Report the document whose numeric version is highest in {versions}; these are ID=version entries.", "Please select the document with the maximum numeric version from ID=version entries {versions}."), answers=("{result}.", "The selection is {result}."), cases=cases),),
)
