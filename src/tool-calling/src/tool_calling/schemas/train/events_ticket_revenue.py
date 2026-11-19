from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"adult_count": rng.randint(1, 300), "adult_price": rng.randint(10, 80), "child_count": rng.randint(1, 150), "child_price": rng.randint(5, 30)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(adult_count, adult_price, child_count, child_price):
    revenue = int(adult_count) * int(adult_price) + int(child_count) * int(child_price)
    return f"${revenue}"


SCHEMA = Schema(
    id="events_ticket_revenue",
    tool_names=("calculate_ticket_revenue", "sum_ticket_category_revenue", "compute_gross_ticket_sales", "total_adult_child_sales", "calculate_event_ticket_income", "sum_adult_child_revenue", "compute_ticket_sales_total", "find_gross_event_revenue", "calculate_category_ticket_sales", "total_ticket_revenue_before_fees"),
    descriptions=("Sum revenue across adult and child ticket categories.", "Calculate gross ticket sales before fees.", "Multiply each ticket count by its price and add the adult and child totals.", "Compute gross adult and child ticket revenue without fees.", "Find total ticket sales from the two category counts and prices.", "Add adult ticket revenue to child ticket revenue.", "Calculate the combined gross sales of adult and child tickets.", "Determine ticket income as each category's count times its price, summed.", "Compute total ticket revenue before fees for both categories.", "Sum the sales values of the adult and child tickets."),
    parameters=(Parameter(names=("adult_count", "adult_tickets")), Parameter(names=("adult_price", "adult_ticket_price")), Parameter(names=("child_count", "child_tickets")), Parameter(names=("child_price", "child_ticket_price"))),
    tasks=(Task(id="revenue", prompts=("An event sold {adult_count} adult tickets at ${adult_price} each and {child_count} child tickets at ${child_price} each. Calculate total gross ticket revenue before fees.", "Add ticket revenue for {adult_count} adult tickets at ${adult_price} each and {child_count} child tickets at ${child_price} each.", "Find gross revenue before fees from {adult_count} adult tickets at ${adult_price} each and {child_count} child tickets at ${child_price} each.", "An event sold {adult_count} adult tickets for ${adult_price} apiece plus {child_count} child tickets for ${child_price} apiece. What are gross ticket sales before fees?", "Calculate total ticket income before fees: adults {adult_count} at ${adult_price}, children {child_count} at ${child_price}.", "What is the combined gross revenue before fees for {adult_count} adult tickets priced ${adult_price} each and {child_count} child tickets priced ${child_price} each?", "Multiply {adult_count} adult tickets by ${adult_price} and {child_count} child tickets by ${child_price}, then sum for gross revenue before fees.", "Ticket sales were {adult_count} adults at ${adult_price} each and {child_count} children at ${child_price} each. Find the total before fees.", "Compute gross event ticket revenue before fees given {adult_count} adult tickets at ${adult_price} and {child_count} child tickets at ${child_price} each.", "How much gross revenue before fees comes from {adult_count} adult tickets at ${adult_price} each and {child_count} child tickets at ${child_price} each?", "Add adult sales of {adult_count} tickets at ${adult_price} each to child sales of {child_count} tickets at ${child_price} each; report the gross before fees.", "For {adult_count} adult tickets costing ${adult_price} each and {child_count} child tickets costing ${child_price} each, calculate total sales before fees."), answers=("Revenue: {result}.", "Gross revenue: {result}."), cases=cases),),
)
