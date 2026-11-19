from ...schema_types import Decision, Parameter, Schema, Task


REQUIRED = ("application", "site plan", "fee receipt")


def cases(rng, count):
    for _ in range(count):
        submitted = [item for item in REQUIRED if rng.choice((True, False))]
        rng.shuffle(submitted)
        yield {"submitted": ", ".join(submitted) if submitted else "none"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(submitted):
    present = set(submitted.split(", "))
    missing = [item for item in REQUIRED if item not in present]
    return "complete" if not missing else "incomplete; missing " + ", ".join(missing)


SCHEMA = Schema(
    id="civic_permit_completeness",
    tool_names=("check_permit_completeness", "find_missing_permit_documents", "assess_permit_submission", "check_required_permit_items", "evaluate_permit_document_set", "identify_missing_permit_items", "compare_permit_documents", "determine_permit_completeness", "review_permit_submission", "list_missing_required_documents"),
    descriptions=("Check submitted documents against the required application, site plan, and fee receipt.", "Report permit completeness and missing required documents.", "Compare the submitted list to application, site plan, and fee receipt in that order.", "Return complete or incomplete and list missing required documents in required order.", "Assess a permit submission against the three fixed required items.", "Identify missing permit documents in application, site plan, fee receipt order.", "Check whether all three required permit documents were submitted.", "Report completeness and any omissions using the fixed required-document order.", "Evaluate the submitted permit items against the specified required set.", "Find missing application, site plan, and fee receipt documents in that order."),
    parameters=(Parameter(names=("submitted", "submitted_documents")),),
    tasks=(Task(id="check", prompts=('A permit requires application, site plan, and fee receipt. Submitted: {submitted}. Is it complete? List missing items in that order.', 'Required documents: application, site plan, fee receipt. Submitted: {submitted}. Report complete or incomplete and any missing documents in required-list order.', 'Review the submission {submitted} against the required application, site plan, and fee receipt. State whether it is complete and list omissions in that order.', 'Does {submitted} satisfy all permit requirements? The required items are application, site plan, fee receipt; report complete or incomplete and list missing items in that order.', 'For a permit with submitted documents {submitted}, compare against application, site plan, then fee receipt. Give completeness and any missing items in that sequence.', 'The permit checklist is application, site plan, fee receipt. Given {submitted}, identify whether the package is complete; list anything missing in checklist order.', 'Submitted: {submitted}. A complete package contains an application, a site plan, and a fee receipt. Report complete or incomplete and any missing items in that order.', 'Check {submitted} for completeness. Require application, site plan, and fee receipt, and order any missing documents as just listed.', 'Which required permit documents are absent from {submitted}? The required order is application, site plan, fee receipt; also state whether the submission is complete or incomplete.', 'Compare the received set ({submitted}) with the permit requirements: application, site plan, fee receipt. Return completeness and missing documents in requirement order.', 'An application, site plan, and fee receipt are mandatory, in that order for reporting. The submission is {submitted}; assess completeness and list omissions.', 'Assess the permit package containing {submitted}. It must have application, site plan, and fee receipt; state complete or incomplete and list missing items in that order.', 'From {submitted}, determine whether the permit file is complete. Required items, and the order for listing omissions, are application, site plan, fee receipt.', 'Use the ordered checklist application, site plan, fee receipt to review {submitted}. Return complete or incomplete and any missing items in checklist order.'), answers=("The permit is {result}.", "Result: {result}."), cases=cases),)
)
