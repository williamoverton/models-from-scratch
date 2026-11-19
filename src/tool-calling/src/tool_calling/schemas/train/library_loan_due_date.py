from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        borrowed = date(2025, 11, 1) + timedelta(days=rng.randrange(500))
        yield {"borrowed": borrowed.isoformat(), "days": str(rng.choice((7, 14, 21, 28, 42)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(borrowed, days):
    return (date.fromisoformat(borrowed) + timedelta(days=int(days))).isoformat()


SCHEMA = Schema(
    id="library_loan_due_date",
    tool_names=("calculate_library_due_date", "add_loan_period", "compute_library_loan_due_date", "find_loan_due_date", "calculate_book_due_date", "add_calendar_days_to_checkout", "derive_library_due_date", "compute_checkout_due_date", "find_book_return_date", "determine_loan_due_date"),
    descriptions=("Add a loan period in calendar days to the checkout date.", "Calculate a book loan's due date using calendar days.", "Find the due date by adding the loan's calendar days to its checkout date.", "Compute a library loan's return date from checkout and loan duration.", "Add the specified number of calendar days to the borrowed date.", "Determine when a library loan is due from its checkout date and period in days.", "Calculate the date after the stated number of calendar days following checkout.", "Work out a book's due date by adding the loan period to the checkout date.", "Return the library due date for a checkout date and calendar-day duration.", "Determine the loan due date using elapsed calendar days."),
    parameters=(Parameter(names=("borrowed", "checkout_date")), Parameter(names=("days", "loan_days"))),
    tasks=(Task(id="due", prompts=("A library loan starts on {borrowed} and lasts {days} calendar days. Add that many days to the checkout date; when is it due?", "What is the due date {days} calendar days after the {borrowed} checkout?", "Calculate the due date by adding {days} calendar days to checkout on {borrowed}.", "A book checked out on {borrowed} is due {days} calendar days later. Give its due date.", "Starting with the checkout date {borrowed}, advance {days} calendar days to find the library loan's due date.", "When must a loan checked out {borrowed} be returned if its term is {days} calendar days?", "The loan period is {days} calendar days after {borrowed}. On what date is the library loan due?", "Determine the library due date for a {borrowed} checkout and a {days}-calendar-day loan.", "Add {days} calendar days to {borrowed}, the checkout date, and report the loan due date.", "A library item was borrowed on {borrowed} for {days} calendar days. What date is its loan due?", "For a checkout on {borrowed}, find the date that falls {days} calendar days later as the due date.", "How does the due date work out when {days} calendar days are added to the {borrowed} checkout date?"), answers=("The loan is due {result}.", "Due date: {result}."), cases=cases),),
)
