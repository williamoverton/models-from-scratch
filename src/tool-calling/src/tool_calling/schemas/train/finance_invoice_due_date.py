from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        invoice_date = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        yield {"invoice_date": invoice_date.isoformat(), "terms_days": str(rng.choice((7, 14, 30, 45, 60, 90)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(invoice_date, terms_days):
    due = date.fromisoformat(invoice_date) + timedelta(days=int(terms_days))
    return due.isoformat()


SCHEMA = Schema(
    id="finance_invoice_due_date",
    tool_names=("calculate_invoice_due_date", "add_invoice_terms", "compute_invoice_due_date", "find_invoice_due_date", "get_invoice_payment_due_date", "apply_invoice_payment_terms", "calculate_payment_deadline", "add_payment_days_to_invoice_date", "resolve_invoice_due_date", "compute_due_date_from_terms"),
    descriptions=("Calculate the due date by adding calendar-day terms to an invoice date.", "Add payment terms in calendar days to an invoice date.", "Compute an invoice's due date from its date and terms in days.", "Find the payment due date by adding the stated calendar days.", "Determine the invoice deadline using calendar-day payment terms.", "Add the payment-days value to the invoice date.", "Return the ISO date obtained by adding the invoice terms.", "Calculate when payment is due based on the invoice date and number of days.", "Resolve the invoice due date using the supplied calendar-day terms.", "Find the date a given number of calendar days after the invoice date."),
    parameters=(Parameter(names=("invoice_date", "date")), Parameter(names=("terms_days", "payment_days"))),
    tasks=(Task(id="due", prompts=("An invoice is dated {invoice_date} with net {terms_days} calendar-day terms. What is its due date?", "Add {terms_days} calendar days to the invoice date {invoice_date}; what date is payment due?", "Calculate the due date for an invoice dated {invoice_date} with {terms_days} calendar days of payment terms.", "When is payment due if the invoice date is {invoice_date} and the terms are net {terms_days} calendar days?", "Find the date {terms_days} calendar days after the invoice date {invoice_date}.", "An invoice from {invoice_date} has {terms_days}-calendar-day terms. Give its due date.", "Determine the payment deadline by adding {terms_days} calendar days to {invoice_date}.", "What due date results from {terms_days} calendar days of terms on an invoice dated {invoice_date}?", "For the invoice dated {invoice_date}, apply {terms_days} calendar-day terms and report the due date.", "The invoice date is {invoice_date}; payment is due {terms_days} calendar days later. What is the date?", "Compute the invoice deadline for {invoice_date} plus {terms_days} calendar days.", "With net {terms_days} calendar-day terms starting on invoice date {invoice_date}, when is the invoice due?"), answers=("The due date is {result}.", "Payment is due {result}."), cases=cases),),
)
