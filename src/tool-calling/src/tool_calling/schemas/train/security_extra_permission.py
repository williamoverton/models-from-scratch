from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        accounts = rng.sample([f"AC-{n}" for n in range(100, 200)], 3)
        allowed = rng.sample(("read", "write", "export", "deploy"), 2)
        extra = rng.choice([permission for permission in ("read", "write", "export", "deploy") if permission not in allowed])
        flagged = rng.choice(accounts)
        records = []
        for account in accounts:
            permissions = allowed[:] if account != flagged else allowed + [extra]
            rng.shuffle(permissions)
            records.append(f"{account}={'+'.join(permissions)}")
        yield {"allowed": ", ".join(allowed), "accounts": "; ".join(records)}


def prepare(*, task_id, case):
    allowed = set(case["allowed"].split(", "))
    records = [entry.split("=") for entry in case["accounts"].split("; ")]
    account, = [identifier for identifier, permissions in records if set(permissions.split("+")) - allowed]
    return Decision(fields=case, arguments={"account": account})


def resolve(account):
    return f"Flagged account: {account}"


SCHEMA = Schema(
    id="security_extra_permission",
    tool_names=("flag_account_permission", "mark_excess_access", "flag_account", "mark_account_for_review", "flag_account_by_id", "mark_account_access", "flag_access_for_review", "flag_specified_account", "mark_account_by_id", "flag_account_for_review"),
    descriptions=("Flag an account by ID.", "Mark an account for access review.", "Flag the specified account.", "Mark an account identified by its ID.", "Flag an account for access review.", "Mark the supplied account for review.", "Flag the given account record.", "Mark access for the specified account.", "Flag an identified account for review.", "Mark the account matching the supplied ID."),
    parameters=(Parameter(names=("account", "account_id")),),
    tasks=(Task(id="extra", prompts=("Allowed permissions: {allowed}. Accounts (permissions joined by +): {accounts}. Flag the account with any permission outside the allowed list.", "Flag the account with an extra permission; allowed: {allowed}; account permissions: {accounts}. A + separates permissions.", "Allowed: {allowed}. In {accounts}, + joins permissions; flag the account with a permission not allowed.", "Compare {accounts} against {allowed}; permissions are + separated. Flag the account with excess access.", "Using {allowed} as the allowed list, flag the account in {accounts} that has an extra + separated permission.", "Flag the account whose permissions exceed {allowed}: {accounts}. Each + separates permissions.", "Check {accounts} for a permission outside {allowed}; + joins each account's permissions. Flag that account.", "In {accounts}, permissions are separated by +. With {allowed} allowed, flag the account holding an additional permission.", "Which account in {accounts} has a permission not in {allowed}? Permissions use + as a separator; flag it.", "Audit {accounts} against the allowed permissions {allowed}, splitting permissions on +; flag the account with an extra.", "The permitted list is {allowed}; account permissions in {accounts} are + joined. Flag the account violating the list.", "Flag the account with excess permissions in {accounts}, where + separates permissions and {allowed} is the allowed list."), answers=("{result}.", "{result}."), cases=cases),),
)
