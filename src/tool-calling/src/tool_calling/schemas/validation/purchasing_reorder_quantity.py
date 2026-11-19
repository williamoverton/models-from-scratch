from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"current": str(rng.randrange(0, 101)), "target": str(rng.randrange(0, 151))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(current, target):
    return str(max(0, int(target) - int(current)))


SCHEMA = Schema(id="purchasing_reorder_quantity", tool_names=('calculate_reorder_quantity', 'units_to_reorder', 'compute_reorder_units', 'find_reorder_quantity', 'calculate_stock_shortfall', 'reorder_quantity_for_target', 'get_replenishment_quantity', 'compute_stock_reorder', 'determine_reorder_amount', 'stock_units_to_target'), descriptions=('Calculate the nonnegative units needed to reach a stock target.', 'Subtract current stock from target, using zero if stock already meets or exceeds the target.', 'Compute target stock minus current stock, floored at zero.', 'Find how many units are needed to reach the target, or zero when already met.', 'Return the nonnegative difference between target and current stock.', 'Determine the reorder quantity from current and target inventory, never below zero.', 'Calculate the stock shortfall relative to target, with a minimum of zero.', 'Get the units required to reach target stock without returning a negative quantity.', 'Compute the replenishment quantity as the positive stock deficit or zero.', 'Find the nonnegative stock quantity required to meet the target.'), parameters=(Parameter(names=("current", "current_stock")), Parameter(names=("target", "target_stock"))), tasks=(Task(id="reorder", prompts=("Current stock is {current} units and the target is {target}. How many units should be reordered to reach the target? Use zero if already at or above target.", "With {current} on hand and a target of {target}, calculate the nonnegative reorder quantity.", 'With {current} units in stock and a {target}-unit target, calculate the reorder amount, no less than zero.', 'How many units are needed to bring {current} on hand up to {target}? Reorder zero if already at or above target.', 'Find the nonnegative reorder quantity for current stock {current} and target {target}.', 'Target stock is {target}, current stock {current}; calculate units to reorder, using zero if the target is met or exceeded.', 'Replenish from {current} units to a target of {target}: how many units should be ordered, at minimum zero?', 'Calculate the stock shortfall from {current} to {target} units, flooring the reorder at zero.', 'Given {current} units on hand and target {target}, determine the reorder quantity; never use a negative amount.', 'How many units should be reordered for a {target} target and {current} current stock? Use zero at or above target.', 'Determine units needed to reach {target} from {current}, or zero if already there or higher.', 'Order enough to raise {current} units to {target}; give zero if stock already meets or exceeds the target.'), answers=("Reorder {result} units.", "The reorder quantity is {result} units."), cases=cases),))
