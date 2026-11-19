from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        limit = rng.randint(1, 4)
        yield {"renewals": str(rng.randint(0, limit + 1)), "limit": str(limit), "holds": str(rng.randint(0, 3))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(renewals, limit, holds):
    return "eligible" if int(renewals) < int(limit) and int(holds) == 0 else "not eligible"


SCHEMA = Schema(
    id="library_renewal_eligibility",
    tool_names=("check_loan_renewal", "assess_renewal_eligibility", "determine_loan_renewal_eligibility", "check_library_renewal_rule", "evaluate_renewal_eligibility", "check_renewal_limit_and_holds", "determine_if_loan_renewable", "assess_library_loan_renewal", "evaluate_loan_renewal_status", "check_loan_renewability"),
    descriptions=("A loan is renewable only when renewals used are below the limit and there are no holds.", "Check the renewal count and outstanding holds against the stated rule.", "Determine renewal eligibility from renewals used, the limit, and the number of holds.", "A loan qualifies for renewal if its renewal count is less than the limit and its hold count is zero.", "Evaluate whether a loan can be renewed under the stated limit and no-holds rule.", "Check whether prior renewals are below the allowed maximum and no holds exist.", "Assess a library loan's renewal eligibility using the renewal count, limit, and holds.", "Return eligible only for a loan below its renewal limit with zero holds.", "Apply the renewal policy to a loan's used renewals and outstanding holds.", "Determine whether both renewal conditions are met: fewer renewals than the limit and no holds."),
    parameters=(Parameter(names=("renewals", "renewals_used")), Parameter(names=("limit", "renewal_limit")), Parameter(names=("holds", "hold_count"))),
    tasks=(Task(id="eligibility", prompts=("A loan has used {renewals} renewals, with a limit of {limit}, and has {holds} holds. It can be renewed only if used renewals are below the limit and holds are zero. Is it eligible?", "Renewal requires fewer than {limit} prior renewals and no holds. This loan has {renewals} renewals and {holds} holds. Is it eligible?", "Can this loan be renewed? It has {renewals} renewals used, a limit of {limit}, and {holds} holds; eligibility requires fewer renewals than the limit and zero holds.", "Given {renewals} used renewals, a {limit} renewal limit, and {holds} holds, determine eligibility: renewals must be strictly below the limit and holds must be zero.", "The policy permits renewal only with no holds and fewer than {limit} prior renewals. This loan has {holds} holds and {renewals} renewals. Is it eligible?", "Evaluate this loan for renewal: {renewals} renewals used, {limit} allowed, {holds} holds. Both fewer than the limit and zero holds are required.", "With {holds} holds and {renewals} renewals already used out of a limit of {limit}, does the loan qualify? Qualification requires zero holds and usage below the limit.", "Is a loan with {renewals} prior renewals and {holds} holds renewable under a limit of {limit}, when renewals must be below the limit and holds must be zero?", "Apply the renewal rule to {renewals} used renewals, limit {limit}, and {holds} holds: eligible only if usage is strictly below the limit and there are no holds.", "A loan has {holds} holds and has used {renewals} of its {limit} renewal limit. Determine eligibility using the rules: no holds and renewals below the limit.", "Check whether renewal is allowed for {renewals} renewals, limit {limit}, and {holds} holds. The count must be less than the limit and holds must equal zero.", "Under a policy requiring zero holds and renewals used strictly below the limit, is a loan with {renewals} renewals, a {limit} limit, and {holds} holds eligible?"), answers=("The loan is {result} for renewal.", "Renewal status: {result}."), cases=cases),),
)
