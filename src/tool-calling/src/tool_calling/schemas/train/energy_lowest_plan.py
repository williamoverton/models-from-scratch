from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    names = ("Cedar", "Harbor", "Meadow", "Summit", "Willow", "Valley")
    for _ in range(count):
        plans = rng.sample(names, 3)
        costs = rng.sample(range(40, 201), 3)
        yield {"options": "; ".join(f"{plan}: ${cost}" for plan, cost in zip(plans, costs)), "choices": list(zip(plans, costs))}


def prepare(*, task_id, case):
    plan, _ = min(case["choices"], key=lambda choice: choice[1])
    return Decision(fields=case, arguments={"plan": plan})


def resolve(plan):
    return f"Selected plan: {plan}."


SCHEMA = Schema(
    id="energy_select_lowest_cost_plan",
    tool_names=("report_cheapest_energy_plan", "identify_lowest_plan", "record_selected_energy_plan", "confirm_plan_choice", "report_chosen_plan", "acknowledge_energy_plan", "select_plan_by_name", "record_plan_identifier", "confirm_selected_plan", "report_energy_plan_choice"),
    descriptions=("Report the selected energy plan identifier.", "Acknowledge the chosen energy plan.", "Record the supplied plan name.", "Confirm the selected energy plan.", "Report the plan chosen for its cost.", "Acknowledge the provided plan identifier.", "Record which energy plan was selected.", "Confirm the named plan choice.", "Select the supplied energy plan.", "Report the chosen plan name."),
    parameters=(Parameter(names=("plan", "plan_name")),),
    tasks=(Task(id="select", prompts=("Which energy plan has the lowest total cost? {options}.", "Choose the cheapest plan by its stated total: {options}.", "Select the energy plan with the smallest total cost from {options}.", "Compare these energy plans by total cost and pick the least expensive: {options}.", "Which plan costs least overall among {options}?", "From the listed totals, choose the lowest-cost energy plan: {options}.", "Find and select the cheapest energy plan based on these total costs: {options}.", "Energy plan totals are {options}. Which is the least expensive?", "Pick the plan with the minimum stated total: {options}.", "Among {options}, identify the energy plan with the lowest total price.", "Please select the energy plan costing the least in total: {options}.", "Review the total costs {options} and choose the cheapest plan."), answers=("{result}", "The choice is confirmed. {result}"), cases=cases),),
)
