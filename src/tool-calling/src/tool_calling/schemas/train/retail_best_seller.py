from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 5)
        counts = rng.sample(range(1, 150), 5)
        yield {"products": "; ".join(f"P{p}: {n}" for p, n in zip(ids, counts)), "winner": f"P{ids[counts.index(max(counts))]}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"product_id": case["winner"]})


def resolve(product_id):
    return f"Flagged product {product_id}."


SCHEMA = Schema(id="retail_best_seller", tool_names=("flag_product", "mark_product", "flag_product_id", "mark_product_for_review", "report_flagged_product", "select_product_for_review", "record_product_flag", "submit_product_flag", "identify_flagged_product", "register_product_selection"), descriptions=("Flag the product with the supplied ID.", "Mark the specified product for review.", "Record a flag for the given product ID.", "Report the product selected for flagging.", "Select the specified product for review.", "Submit a product ID to be flagged.", "Identify the product to mark by ID.", "Register the given product as flagged.", "Mark a product using its identifier.", "Capture the ID of the selected product."), parameters=(Parameter(names=("product_id", "item_id")),), tasks=(Task(id="best", prompts=("Sales counts by product ID: {products}. Flag the product with the highest count.", "Which product sold the most? Flag it from these ID: count pairs: {products}.", 'Flag the top-selling product in these ID and sales-count pairs: {products}.', 'Select and flag the product with the greatest sales count: {products}.', 'From {products}, mark the product ID with the most units sold.', 'Identify and flag the highest-selling product using {products}.', 'Sales by ID are {products}; flag the one with maximum sales.', 'Which ID has the largest sales count in {products}? Flag it.', 'Review these product sales: {products}. Flag the best seller.', 'Mark the product that sold the greatest number from {products}.', 'Given {products} as product IDs and counts, flag the sales leader.', 'Find the highest count in {products} and flag its product.'), answers=("{result}", "Selection: {result}"), cases=cases),))
