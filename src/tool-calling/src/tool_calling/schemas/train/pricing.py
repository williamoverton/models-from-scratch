from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"price": str(rng.randrange(1, 1001)), "discount": str(rng.randrange(1, 100))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="sale_price",
    tool_names=("sale_price", "apply_discount", "calculate_sale_price", "compute_discounted_price", "calculate_price_after_discount", "find_sale_price", "determine_discounted_price", "apply_percentage_discount", "compute_sale_amount", "price_after_percent_off"),
    descriptions=("Calculate a sale price in dollars after a percentage discount.", "Apply a percentage discount to a dollar price.", "Compute the dollar price after the specified percent off.", "Find the sale price after applying a percentage discount.", "Determine the discounted dollar amount from the original price.", "Calculate the final price after reducing the original by a percentage.", "Apply the given percent off and return the sale price in dollars.", "Compute the price remaining after a percentage reduction.", "Find the discounted price from the original dollar price and percent off.", "Return the dollar sale price after the specified discount."),
    parameters=(
        Parameter(names=("price", "original_price")),
        Parameter(names=("discount", "percent_off")),
    ),
    tasks=(Task(id="sale", prompts=("What is the price after {discount}% off ${price}?", "Apply a {discount}% discount to ${price}.", "Find the sale price of ${price} with {discount}% off.", "A ${price} item is discounted by {discount}%; what does it cost?", "Calculate the discounted dollar price: ${price}, less {discount}%.", "How much remains of ${price} after a {discount}% reduction?", "Take {discount}% off the original ${price} price and give the sale price.", "What is the final dollar price for ${price} discounted {discount}%?", "A product costs ${price} before a {discount}% sale. Find its sale price.", "Compute the price after reducing ${price} by {discount}%.", "For a ${price} purchase, determine the price after {discount}% off.", "Give the discounted price in dollars for ${price} at {discount}% off."), answers=("The sale price is {result}.", "After the discount it costs {result}."), cases=cases),),
)


def resolve(price, discount):
    cents = int(price) * (100 - int(discount))
    return f"${cents // 100}.{cents % 100:02d}"
