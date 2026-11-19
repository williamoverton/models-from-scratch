from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"CR-{n}" for n in range(100, 200)], 3)
        days = rng.sample(range(1, 300), 3)
        records = [(identifier, (date(2027, 1, 1) + timedelta(days=day)).isoformat()) for identifier, day in zip(ids, days)]
        yield {"credentials": "; ".join(f"{identifier} expires {expiry}" for identifier, expiry in records)}


def prepare(*, task_id, case):
    records = [entry.split(" expires ") for entry in case["credentials"].split("; ")]
    identifier, _ = min(records, key=lambda entry: entry[1])
    return Decision(fields=case, arguments={"credential": identifier})


def resolve(credential):
    return f"Flagged credential: {credential}"


SCHEMA = Schema(
    id="security_credential_expiry",
    tool_names=("flag_credential", "mark_credential", "flag_credential_by_id", "mark_credential_by_id", "flag_security_credential", "mark_security_credential", "flag_specified_credential", "mark_specified_credential", "set_credential_flag", "flag_credential_record"),
    descriptions=("Flag a credential by ID.", "Mark the specified credential.", "Flag the supplied credential.", "Mark a credential identified by its ID.", "Flag the given security credential.", "Mark the supplied credential record.", "Flag a specified credential by identifier.", "Mark a security credential by ID.", "Set a flag on the identified credential.", "Flag the credential matching the supplied ID."),
    parameters=(Parameter(names=("credential", "credential_id")),),
    tasks=(Task(id="earliest", prompts=("Credentials: {credentials}. Flag the one with the earliest expiry date.", "Which credential expires first? Flag it: {credentials}.", "From {credentials}, flag the credential with the earliest expiration.", "Compare the expiry dates in {credentials} and flag the first to expire.", "Flag the credential whose expiration date comes earliest: {credentials}.", "Among {credentials}, identify and flag the soonest-expiring credential.", "Select the minimum expiry date in {credentials} and flag its credential.", "Use {credentials} to flag the credential that expires before the others.", "Flag the credential associated with the earliest date in {credentials}.", "Review {credentials}; flag whichever credential has the first expiry.", "For {credentials}, flag the ID with the oldest expiration date.", "Find the earliest expiring credential in {credentials} and flag it."), answers=("{result}.", "{result}."), cases=cases),),
)
