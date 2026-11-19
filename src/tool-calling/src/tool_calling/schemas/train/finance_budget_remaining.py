from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        budget = rng.randint(1000, 50000)
        spent = rng.randint(0, budget + 5000)
        yield {"budget": str(budget), "spent": str(spent)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(budget, spent):
    return f"{Decimal(budget) - Decimal(spent):.2f}"


SCHEMA = Schema(
    id="finance_budget_remaining",
    tool_names=("calculate_budget_remaining", "subtract_budget_spending", "compute_remaining_budget", "get_budget_balance", "calculate_budget_less_spending", "find_remaining_budget", "compute_budget_difference", "determine_unspent_budget", "subtract_spending_from_budget", "get_budget_spending_difference"),
    descriptions=("Subtract spending from the budget, retaining a negative result for overspending.", "Calculate budget less spending.", "Compute the remaining budget as budget minus amount spent.", "Find the budget balance without clamping overspending to zero.", "Return the difference between the budget and spending.", "Calculate how much remains after spending, including negative balances.", "Subtract the amount spent from the budget and return the signed result.", "Determine the signed budget remainder after expenditures.", "Compute a budget balance that can be negative when spending exceeds budget.", "Find budget minus spending, formatted to two decimal places."),
    parameters=(Parameter(names=("budget", "budget_amount")), Parameter(names=("spent", "amount_spent"))),
    tasks=(Task(id="remaining", prompts=("The budget is ${budget} and spending is ${spent}. What is the remaining budget? Use a negative amount if overspent.", "Subtract ${spent} spent from the ${budget} budget; retain a negative balance if spending exceeds budget.", "Calculate ${budget} minus ${spent} in spending, keeping the result negative if overspent.", "What is the signed remaining balance on a ${budget} budget after spending ${spent}? Do not clamp overspending to zero.", "A budget of ${budget} has ${spent} spent. Find the remainder, including a negative balance for overspending.", "How much remains from ${budget} after ${spent} is spent? Report a negative amount if over budget.", "Subtract spending of ${spent} from the ${budget} budget and retain any negative result.", "Find the budget balance for ${budget} allocated and ${spent} spent, allowing negative values.", "With ${budget} budgeted and ${spent} spent, calculate the signed budget remainder.", "Compute budget less spending: ${budget} minus ${spent}; if overspent, give the negative balance.", "What is the remaining budget if the allocation is ${budget} and expenditure is ${spent}? Keep overspending negative.", "Determine the signed difference between a ${budget} budget and ${spent} spent."), answers=("The remaining budget is ${result}.", "Budget less spending is ${result}."), cases=cases),),
)
