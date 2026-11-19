from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"INV-{number}" for number in range(100, 200)], 3)
        unpaid = rng.randrange(3)
        yield {"invoices": ", ".join(f"{invoice}={'unpaid' if index == unpaid else 'paid'}" for index, invoice in enumerate(ids))}


def prepare(*, task_id, case):
    invoices = (entry.split("=") for entry in case["invoices"].split(", "))
    invoice = next(invoice for invoice, status in invoices if status == "unpaid")
    return Decision(fields=case, arguments={"invoice": invoice})


def resolve(invoice):
    return f"Reminder recorded for invoice {invoice}."


SCHEMA = Schema(
    id="finance_remind_unpaid_invoice",
    tool_names=("remind_invoice", "record_invoice_reminder", "log_invoice_reminder", "create_invoice_reminder", "record_reminder_for_invoice", "note_invoice_reminder", "register_invoice_reminder", "mark_invoice_reminder", "save_invoice_reminder", "record_invoice_reminder_by_id"),
    descriptions=("Record a reminder for the specified invoice.", "Record an invoice reminder by ID.", "Log a reminder for the given invoice identifier.", "Record that a reminder was made for an invoice.", "Create a reminder record for the supplied invoice ID.", "Register an invoice reminder using its identifier.", "Note a reminder for the specified invoice.", "Save a reminder record for an invoice by ID.", "Return confirmation that the named invoice's reminder was recorded.", "Record an invoice reminder for the provided invoice."),
    parameters=(Parameter(names=("invoice", "invoice_id")),),
    tasks=(Task(id="remind", prompts=("Invoice payment statuses: {invoices}. Record a reminder for the unpaid invoice.", "From {invoices}, choose the invoice still unpaid and record its reminder.", "Find the unpaid invoice in {invoices} and record a reminder for it.", "Review these invoice statuses and record a reminder for the unpaid one: {invoices}.", "Which invoice in {invoices} remains unpaid? Record its reminder.", "Record an invoice reminder for the entry marked unpaid: {invoices}.", "From the following statuses, select the unpaid invoice and log a reminder: {invoices}.", "Identify the unpaid invoice among {invoices} and record a reminder.", "Please record a reminder for whichever invoice is unpaid in {invoices}.", "Use {invoices} to locate the unpaid invoice and register its reminder.", "Log a reminder for the invoice with unpaid status in {invoices}.", "Check {invoices} and record a reminder for the invoice that has not been paid."), answers=("{result}", "{result}"), cases=cases),),
)
