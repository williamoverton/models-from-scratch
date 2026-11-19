from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    accounts = ("Aster", "Birch", "Cedar", "Dahlia", "Elm", "Fern", "Grove")
    for _ in range(count):
        names = rng.sample(accounts, 3)
        target = rng.randint(50, 500)
        winner = rng.randrange(3)
        rows = [(name, rng.randint(1, target) if i == winner else rng.randint(target + 1, target + 100)) for i, name in enumerate(names)]
        yield {"rows": rows, "target": target, "options": "; ".join(f"{name}: {usage} kWh" for name, usage in rows)}


def prepare(*, task_id, case):
    account = next(name for name, usage in case["rows"] if usage <= case["target"])
    return Decision(fields=case, arguments={"account": account})


def resolve(account):
    return f"Marked account: {account}."


SCHEMA = Schema(
    id="energy_account_usage_target",
    tool_names=("mark_account_meeting_target", "flag_account_by_usage", "record_target_account", "mark_selected_energy_account", "flag_selected_account", "acknowledge_usage_account", "record_account_identifier", "mark_usage_target_account", "confirm_target_account", "flag_energy_account"),
    descriptions=("Mark an account by its identifier.", "Flag the specified account.", "Record the selected account identifier.", "Acknowledge the account chosen for the usage target.", "Mark the supplied energy account.", "Flag the named account.", "Confirm the selected account identifier.", "Record which account was selected.", "Mark an identified account for the target.", "Report the account to be marked."),
    parameters=(Parameter(names=("account", "account_id")),),
    tasks=(Task(id="target", prompts=("Mark the account meeting the usage target of at most {target} kWh: {options}.", "Which account used no more than {target} kWh? Mark it: {options}.", "From {options}, mark the account with usage at or below {target} kWh.", "The target is a maximum of {target} kWh. Mark the account meeting it: {options}.", "Identify and mark the account whose usage does not exceed {target} kWh: {options}.", "Account usage: {options}. Which account meets the inclusive {target} kWh maximum? Mark it.", "Mark the account in {options} that used {target} kWh or less.", "Find the account meeting the at-most-{target}-kWh target and mark it: {options}.", "Given {options}, mark the account whose consumption is no greater than {target} kWh.", "Which account is within the usage limit of {target} kWh, inclusive? Mark it: {options}.", "Select and mark the account at or under {target} kWh from {options}.", "The usage target is no more than {target} kWh. Identify and mark the qualifying account: {options}."), answers=("{result}", "Done. {result}"), cases=cases),),
)
