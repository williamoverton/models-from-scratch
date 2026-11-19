from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        checkout_day = rng.randrange(1, 30)
        days = rng.randrange(1, 31 - checkout_day)
        yield {"days": str(days), "checkout_day": str(checkout_day)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="library_loan_due",
    tool_names=('loan_due_day', 'library_due', 'calculate_april_due_date', 'april_loan_due', 'compute_library_due_date', 'get_april_loan_due_date', 'calculate_loan_due_day', 'find_library_due_day', 'add_loan_days_to_checkout', 'april_checkout_due_date'),
    descriptions=('Calculate the April due date for a sample library loan from its checkout day and loan length.', 'Add a library loan period to an April checkout date.', 'Compute the April due day from an April checkout day and a loan duration that stays in April.', 'Find the sample library loan’s April due date by adding its length to the checkout day.', 'Return the April due date for a checkout day and loan period ending in April.', 'Determine the sample due day in April from the checkout day and number of loan days.', 'Add the loan duration to the April checkout day to get an April due date.', 'Calculate a sample loan’s due date within April from its checkout day and duration.', 'Get the April date due for a library loan whose checkout and due dates are in April.', 'Compute an April library due date by adding loan days to the checkout day.'),
    parameters=(
        Parameter(names=("days", "loan_days")),
        Parameter(names=("checkout_day", "day")),
    ),
    tasks=(Task(id="due", prompts=("A book was checked out on April {checkout_day} for {days} days. When is it due?", "What is the due date for an April {checkout_day} checkout with a {days}-day loan?", 'Find the due date for a book checked out April {checkout_day} for {days} days.', 'A {days}-day loan begins on April {checkout_day}; what date is it due?', 'Add {days} loan days to an April {checkout_day} checkout to find the due date.', 'When is an April {checkout_day} library checkout due after {days} days?', 'Calculate the library due date for checkout April {checkout_day} and loan length {days} days.', 'For a checkout on April {checkout_day}, determine the due date after {days} days.', 'What April due date results from a {days}-day loan starting April {checkout_day}?', 'A library book was borrowed on April {checkout_day} for {days} days; give its due date.', 'Compute the due date by adding {days} days to April {checkout_day}.', 'With checkout April {checkout_day} and a {days}-day loan, when is the book due?'), answers=("It is due {result}.", "The due date is {result}."), cases=cases),),
)


def resolve(days, checkout_day):
    return f"April {int(checkout_day) + int(days)}"
