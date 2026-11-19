from ...schema_types import Decision, Parameter, Schema, Task


CATEGORIES = {
    "Railway Co": "travel",
    "City Taxi": "travel",
    "Paper Mart": "office supplies",
    "Ink Depot": "office supplies",
    "Cafe Central": "meals",
    "Garden Bistro": "meals",
}


def cases(rng, count):
    for _ in range(count):
        yield {"merchant": rng.choice(tuple(CATEGORIES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(merchant):
    return f"{merchant}: {CATEGORIES[merchant]}"


SCHEMA = Schema(
    id="finance_categorize_merchant",
    tool_names=("categorize_merchant", "lookup_expense_category", "classify_merchant_expense", "get_merchant_category", "find_merchant_expense_category", "apply_merchant_category_rules", "resolve_merchant_category", "identify_merchant_category", "lookup_merchant_classification", "classify_expense_merchant"),
    descriptions=("Determine the sample expense category for a merchant.", "Look up a merchant's category in the sample rules.", "Classify a merchant using the provided sample expense mapping.", "Find the mapped expense category for the named merchant.", "Apply the sample merchant-to-category rules.", "Identify the category assigned to a merchant by the sample rules.", "Resolve a merchant's expense category from the fixed mapping.", "Return the merchant and its mapped expense category.", "Look up the sample classification for a specified merchant.", "Use the fixed merchant rules to categorize an expense."),
    parameters=(Parameter(names=("merchant", "merchant_name")),),
    tasks=(Task(id="categorize", prompts=("Use these merchant rules: Railway Co and City Taxi are travel; Paper Mart and Ink Depot are office supplies; Cafe Central and Garden Bistro are meals. Categorize the expense from {merchant}.", "Categorize {merchant} using this mapping: travel = Railway Co or City Taxi; office supplies = Paper Mart or Ink Depot; meals = Cafe Central or Garden Bistro.", "What category applies to {merchant}? Railway Co and City Taxi map to travel, Paper Mart and Ink Depot to office supplies, and Cafe Central and Garden Bistro to meals.", "Classify the expense for {merchant}: travel includes Railway Co and City Taxi; office supplies includes Paper Mart and Ink Depot; meals includes Cafe Central and Garden Bistro.", "Using the rules Railway Co/City Taxi = travel, Paper Mart/Ink Depot = office supplies, Cafe Central/Garden Bistro = meals, find the category for {merchant}.", "For {merchant}, select its expense category from this mapping: Railway Co and City Taxi are travel; Paper Mart and Ink Depot are office supplies; Cafe Central and Garden Bistro are meals.", "Assign {merchant} a category under these rules: travel for Railway Co or City Taxi, office supplies for Paper Mart or Ink Depot, meals for Cafe Central or Garden Bistro.", "Which expense category is {merchant} in? Travel: Railway Co, City Taxi. Office supplies: Paper Mart, Ink Depot. Meals: Cafe Central, Garden Bistro.", "Look up {merchant} using the sample categories: Railway Co and City Taxi are travel, Paper Mart and Ink Depot office supplies, Cafe Central and Garden Bistro meals.", "Apply this merchant mapping to {merchant}: Railway Co and City Taxi go to travel; Paper Mart and Ink Depot to office supplies; Cafe Central and Garden Bistro to meals.", "Categorize the merchant {merchant}. Travel merchants are Railway Co and City Taxi; office supplies merchants are Paper Mart and Ink Depot; meal merchants are Cafe Central and Garden Bistro.", "Find the mapped category for {merchant} given travel = Railway Co and City Taxi, office supplies = Paper Mart and Ink Depot, and meals = Cafe Central and Garden Bistro.", "An expense is from {merchant}. Under the rules Railway Co and City Taxi are travel, Paper Mart and Ink Depot are office supplies, and Cafe Central and Garden Bistro are meals, what is its category?"), answers=("Category: {result}.", "The rule gives {result}."), cases=cases),),
)
