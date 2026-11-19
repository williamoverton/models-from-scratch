from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randrange(200, 1001)
        accounts = rng.sample(("Alder", "Birch", "Cedar", "Dogwood", "Elm", "Fir"), 3)
        usage = [rng.randrange(0, threshold + 1), rng.randrange(0, threshold + 1), threshold + rng.randrange(1, 201)]
        rng.shuffle(usage)
        yield {"readings": "; ".join(f"{account}: {value} kWh" for account, value in zip(accounts, usage)), "threshold": str(threshold), "choices": list(zip(accounts, usage))}


def prepare(*, task_id, case):
    account, = (account for account, usage in case["choices"] if usage > int(case["threshold"]))
    return Decision(fields=case, arguments={"account": account})


def resolve(account):
    return f"Flagged account: {account}."


SCHEMA = Schema(
    id="energy_flag_sole_account_above_threshold",
    tool_names=('report_high_usage_account', 'report_threshold_account', 'report_flagged_account', 'acknowledge_selected_account', 'return_flagged_account_id', 'report_high_usage_selection', 'confirm_account_flag', 'echo_selected_account', 'show_flagged_account', 'report_account_for_flagging'),
    descriptions=('Acknowledge the selected account identifier.', 'Report the account selected for flagging.', 'Return the provided account name as a flagged account.', 'Confirm the supplied account as the flagging selection.', 'Show the selected account name with a flagged label.', 'Report a flag for the given account name.', 'Echo the provided account identifier as flagged.', 'Return the selected account in a flagged-account message.', 'Present the supplied account as the flagged selection.', 'Output a flagged-account label for the given account.'),
    parameters=(Parameter(names=("account", "account_name")),),
    tasks=(Task(id="flag", prompts=("Flag the sole account strictly above {threshold} kWh; equality is not above. Readings: {readings}.", "Which account exceeds {threshold} kWh? Only values greater than the threshold count: {readings}.", 'Flag the sole account in {readings} whose usage is strictly greater than {threshold} kWh; equality does not qualify.', 'From {readings}, flag the only account exceeding {threshold} kWh, not one equal to it.', 'Which account in {readings} is above {threshold} kWh? Flag it; the threshold itself is excluded.', 'Compare {readings} against {threshold} kWh and flag the sole account strictly above it.', 'Flag the unique account with usage greater than {threshold} kWh in {readings}; equal readings do not count.', 'Using {readings}, identify and flag the one account exceeding the {threshold} kWh threshold, exclusively.', 'At a cutoff of {threshold} kWh, flag the only account in {readings} over, not equal to, the cutoff.', 'The readings are {readings}. Flag the sole account above {threshold} kWh; values at the threshold are excluded.', 'Select and flag the account in {readings} with strictly more than {threshold} kWh.', 'Which sole account exceeds {threshold} kWh in {readings}? Flag it, excluding equality.'), answers=("{result}", "The selection is confirmed. {result}"), cases=cases),),
)
