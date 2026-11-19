from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 4)
        prices = rng.sample(range(10, 200), 4)
        yield {"quotes": "; ".join(f"S{n}: ${p} per unit" for n, p in zip(ids, prices)), "winner": f"S{ids[prices.index(min(prices))]}"}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"supplier_id": case["winner"]})


def resolve(supplier_id):
    return f"Lowest-price supplier selected: {supplier_id}."


SCHEMA = Schema(id="purchasing_lowest_quote", tool_names=('report_lowest_supplier', 'acknowledge_flagged_supplier', 'report_selected_supplier', 'acknowledge_supplier_selection', 'return_selected_supplier_id', 'report_lowest_quote_selection', 'confirm_supplier_selection', 'echo_supplier_id', 'show_selected_supplier', 'report_supplier_choice'), descriptions=('Report the supplier selected for the lowest quote.', 'Identify a selected supplier by ID.', 'Return the supplied supplier ID as the lowest-price selection.', 'Acknowledge the provided supplier as the selected lowest-price supplier.', 'Report the given supplier ID with a lowest-price selection label.', 'Confirm the selected supplier ID in a lowest-price message.', 'Echo the supplied supplier identifier as the lowest-price selection.', 'Present the given supplier as the selected lowest-price supplier.', 'Output a lowest-price supplier selection for the supplied ID.', 'Return a selection message for the provided supplier ID.'), parameters=(Parameter(names=("supplier_id", "vendor_id")),), tasks=(Task(id="lowest", prompts=("Choose the supplier with the lowest unit price from these quotes: {quotes}.", "Flag the cheapest supplier by unit price: {quotes}.", 'Select the supplier offering the lowest per-unit price in {quotes}.', 'From {quotes}, flag the supplier with the cheapest unit price.', 'Compare unit prices in {quotes} and choose the lowest-price supplier.', 'Which supplier has the minimum price per unit? Choose from {quotes}.', 'Find and flag the supplier with the lowest unit quote: {quotes}.', 'Using {quotes}, select the supplier whose unit price is smallest.', 'The supplier quotes are {quotes}; choose the least expensive per unit.', 'Identify the cheapest supplier by unit price from {quotes} and select it.', 'For these quotes {quotes}, flag the supplier with the minimum unit price.', 'Choose the supplier offering the best unit price among {quotes}.'), answers=("{result}", "Selection: {result}"), cases=cases),))
