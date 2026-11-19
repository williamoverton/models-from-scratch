from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        due = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        yield {"due_date": due.isoformat(), "days": str(rng.randint(1, 14))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(due_date, days):
    return (date.fromisoformat(due_date) + timedelta(days=int(days))).isoformat()


SCHEMA = Schema(
    id="education_assignment_extension",
    tool_names=('calculate_extended_due_date', 'extend_assignment_deadline', 'compute_extended_due_date', 'calculate_assignment_extension', 'add_deadline_days', 'compute_new_due_date', 'calculate_deadline_extension', 'add_calendar_days_to_due_date', 'get_extended_deadline', 'find_extended_due_date'),
    descriptions=('Add calendar days to an assignment due date.', 'Calculate the extended deadline using calendar days.', 'Compute the due date by adding calendar days.', 'Calculate an assignment deadline extended by calendar days.', 'Add the specified calendar days to the due date.', 'Compute the new due date from the original and calendar days.', 'Calculate a deadline extension in calendar days.', 'Add calendar days to an assignment’s original due date.', 'Get the extended deadline by adding calendar days.', 'Find the new due date after a calendar-day extension.'),
    parameters=(Parameter(names=("due_date", "original_due_date")), Parameter(names=("days", "extension_days"))),
    tasks=(Task(id="extension", prompts=("An assignment is due {due_date}; extend it by {days} calendar days. What is the new due date?", "Move the assignment deadline from {due_date} forward by {days} calendar days. What date results?", "What is the extended due date if {days} calendar days are added to {due_date}?", "The original assignment deadline is {due_date}. Add {days} calendar days to find its new due date.", "Extend a due date of {due_date} by {days} calendar days and report the new deadline.", "An assignment has a {days}-calendar-day extension on its {due_date} due date. When is it due now?", "Calculate the new assignment due date: original {due_date}, extension {days} calendar days.", "Starting from {due_date}, advance the assignment deadline {days} calendar days. What is the revised date?", "The deadline {due_date} has been extended by {days} calendar days. Find the updated due date.", "Add {days} calendar days to the assignment's original due date of {due_date}. What is the result?", "If an assignment due {due_date} gets {days} more calendar days, what is its new due date?"), answers=("The new due date is {result}.",), cases=cases),),
)
