from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"EXP-{number}" for number in range(100, 200)], 3)
        amounts = rng.sample(range(20, 1001), 3)
        yield {"expenses": ", ".join(f"{expense}=${amount}" for expense, amount in zip(ids, amounts))}


def prepare(*, task_id, case):
    expenses = (entry.split("=$") for entry in case["expenses"].split(", "))
    expense, _ = max(expenses, key=lambda entry: int(entry[1]))
    return Decision(fields=case, arguments={"expense": expense})


def resolve(expense):
    return f"Flagged expense: {expense}."


SCHEMA = Schema(
    id="finance_flag_largest_expense",
    tool_names=("flag_expense", "mark_expense_for_review", "flag_expense_for_review", "mark_expense", "record_expense_flag", "flag_expense_by_id", "mark_expense_id_for_review", "register_expense_flag", "set_expense_review_flag", "identify_flagged_expense"),
    descriptions=("Flag the specified expense for review.", "Mark an expense by its ID.", "Flag the given expense identifier for review.", "Record a review flag for the supplied expense.", "Mark the specified expense as flagged.", "Return confirmation of the expense selected for flagging.", "Flag an expense using its identifier.", "Register the specified expense for review.", "Mark the given expense ID for review.", "Identify the expense that has been flagged."),
    parameters=(Parameter(names=("expense", "expense_id")),),
    tasks=(Task(id="flag", prompts=("Expense amounts are {expenses}. Flag the expense with the largest amount.", "From {expenses}, mark the highest-dollar expense for review.", "Compare {expenses} and flag the expense with the greatest amount for review.", "Which expense is largest in {expenses}? Flag it for review.", "Flag the highest-value expense from these amounts: {expenses}.", "Review {expenses} and mark the expense with the largest dollar amount.", "Find and flag the most expensive entry in {expenses}.", "From the expense amounts {expenses}, flag the one with the maximum value.", "Identify the largest expense by amount and mark it for review: {expenses}.", "Please flag the expense with the highest listed amount: {expenses}.", "Select and flag the largest dollar expense among {expenses}.", "Using {expenses}, mark the expense whose amount is greatest for review."), answers=("{result}", "{result}"), cases=cases),),
)
