from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        ages = rng.sample(range(1, 100), 3)
        yield {'branches': '; '.join(f'branch-{branch}={age}' for branch, age in zip(ids, ages))}


def prepare(*, task_id, case):
    entries = [entry.strip().split('=') for entry in case['branches'].split(';')]
    branch = max(entries, key=lambda entry: int(entry[1]))[0]
    return Decision(fields=case, arguments={'branch': branch})


def resolve(branch):
    return f'Flagged branch: {branch}'


SCHEMA = Schema(
    id='source_flag_stalest_branch',
    tool_names=('flag_branch', 'flag_stale_branch', 'flag_branch_for_review', 'mark_branch_for_review', 'flag_branch_by_name', 'mark_specified_branch', 'flag_specified_branch', 'mark_branch_for_attention', 'flag_source_branch', 'mark_branch_by_name'),
    descriptions=('Flag the supplied branch.', 'Flag a branch for review.', 'Mark the specified branch for review.', 'Flag the branch identified by name.', 'Mark the supplied branch for attention.', 'Flag the given source branch.', 'Mark a branch using its name.', 'Flag the identified branch.', 'Mark the named branch for review.', 'Flag the specified branch for attention.'),
    parameters=(Parameter(names=('branch', 'branch_name')),),
    tasks=(Task(id='flag', prompts=('Flag the stalest branch, defined as the one with the most days since its last update. Branch=days: {branches}.', 'For {branches} (branch=days since update), flag the stalest branch: the largest number of days.', 'In {branches}, each branch is paired with days since update. Flag the largest age.', 'Flag the branch with the most days since its update in {branches} (branch=days).', 'Compare {branches} as branch=days since last update and flag the oldest.', 'Which branch in {branches} has gone longest without an update? Entries are branch=days; flag it.', 'Using {branches} (branch=days since update), flag the branch with the maximum days.', 'Find and flag the stalest branch in {branches}; the number is days since last update.', 'Flag the longest-unupdated branch from {branches}, formatted branch=days since update.', 'Select the highest age in {branches} and flag its branch; ages are days since update.', 'For branch=days since last update entries {branches}, flag the one with the most days.', 'Review {branches}: each value is days since update. Flag the branch with the greatest value.'), answers=('{result}.', '{result}.'), cases=cases),),
)
