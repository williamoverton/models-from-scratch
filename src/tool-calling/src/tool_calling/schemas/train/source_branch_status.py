from ...schema_types import Decision, Parameter, Schema, Task


STATUSES = {'feature-auth': 'open', 'fix-cache': 'merged', 'feature-search': 'open', 'fix-login': 'closed', 'feature-billing': 'merged', 'fix-build': 'open'}


def cases(rng, count):
    for _ in range(count):
        branches = rng.sample(tuple(STATUSES), 3)
        yield {'branches': ', '.join(branches), 'branch': rng.choice(branches)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={'branch': case['branch']})


def resolve(branch):
    return f'{branch}: {STATUSES[branch]}'


SCHEMA = Schema(
    id='source_branch_status_lookup',
    tool_names=('get_branch_status', 'lookup_branch_status', 'find_branch_status', 'retrieve_branch_status', 'read_branch_status', 'get_registered_branch_status', 'lookup_registered_branch', 'check_sample_branch_status', 'find_status_for_branch', 'get_sample_branch_status'),
    descriptions=('Look up branch status in the sample registry.', 'Find a branch status in the sample registry.', 'Retrieve the registered status of a branch.', 'Check a branch status in the sample registry.', 'Get the sample registry status for a named branch.', 'Read the status of the specified sample branch.', 'Find the status registered for a branch.', 'Look up the sample status of a branch by name.', 'Return the registered status of the supplied branch.', 'Retrieve a branch status from the sample registry.'),
    parameters=(Parameter(names=('branch', 'branch_name')),),
    tasks=(Task(id='status', prompts=('Branches: {branches}. Look up the status of {branch} in the sample registry.', 'From {branches}, look up the registered status for {branch}.', 'For branches {branches}, retrieve {branch} status from the sample registry.', 'Check the sample registry status of {branch}; the branches are {branches}.', 'Among {branches}, what status does the sample registry give {branch}?', 'Find the registered status of {branch} from the sample registry. Branches: {branches}.', 'Given {branches}, read the sample registry status for {branch}.', 'Consult the sample registry for {branch} in this branch list: {branches}.', 'Return the sample registry status of {branch} from {branches}.', 'Which status is registered for {branch} in the sample registry? Branches: {branches}.', 'Look up {branch} in the sample registry, using the listed branches {branches}.', 'For {branch}, get its registered status in the sample registry; branch list: {branches}.'), answers=('Status: {result}.', 'The registry lists {result}.'), cases=cases),),
)
