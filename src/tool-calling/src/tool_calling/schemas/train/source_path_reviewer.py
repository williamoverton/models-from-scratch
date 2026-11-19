from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        pairs = rng.sample([('src/auth.py', 'reviewer-identity'), ('src/pay.py', 'reviewer-payments'), ('src/find.py', 'reviewer-search'), ('docs/api.md', 'reviewer-docs'), ('infra/build.yml', 'reviewer-platform'), ('src/cart.py', 'reviewer-commerce')], 3)
        yield {'mapping': '; '.join(f'{path}={reviewer}' for path, reviewer in pairs), 'path': rng.choice(pairs)[0], 'change': f'C-{rng.randrange(100, 1000)}'}


def prepare(*, task_id, case):
    mapping = dict(entry.strip().split('=') for entry in case['mapping'].split(';'))
    return Decision(fields=case, arguments={'change': case['change'], 'reviewer': mapping[case['path']]})


def resolve(change, reviewer):
    return f'Requested review from {reviewer} for {change}'


SCHEMA = Schema(
    id='source_request_path_reviewer',
    tool_names=('request_review', 'request_change_review', 'request_reviewer', 'request_review_for_change', 'request_change_reviewer', 'ask_reviewer_for_review', 'send_review_request', 'request_review_from_reviewer', 'request_named_reviewer', 'request_reviewer_for_change'),
    descriptions=('Request a reviewer for a change.', 'Request review of a change from a reviewer.', 'Ask the specified reviewer to review a change.', 'Send a review request for a change to a reviewer.', 'Request a named reviewer for the supplied change.', 'Request review from the identified reviewer.', 'Ask a reviewer to inspect the specified change.', 'Send the specified reviewer a change review request.', 'Request a change review using reviewer and change IDs.', 'Request the given reviewer for the identified change.'),
    parameters=(Parameter(names=('change', 'change_id')), Parameter(names=('reviewer', 'reviewer_id'))),
    tasks=(Task(id='request', prompts=('Change {change} modifies {path}. Request review from its reviewer using the path=reviewer mapping: {mapping}.', 'Using path=reviewer pairs {mapping}, request the mapped reviewer for {change}, which modifies {path}.', 'For {change}, request review from the reviewer mapped to {path} in {mapping} (path=reviewer).', 'Find {path} in the path=reviewer mapping {mapping}, then request that reviewer for {change}.', 'Request a review of {change} from the owner of {path} according to path=reviewer pairs {mapping}.', 'The modified path is {path} in change {change}; request its reviewer from {mapping} (path=reviewer).', 'Use {mapping} as path=reviewer entries to request the reviewer for {path} on {change}.', 'Who reviews {path} in {mapping}? Request that reviewer for change {change}; pairs are path=reviewer.', 'Match {path} to its reviewer in {mapping} (path=reviewer), and request review for {change}.', 'Please request review for {change} from the reviewer assigned to {path} in path=reviewer mapping {mapping}.', 'Change {change} touches {path}; using {mapping} as path=reviewer pairs, request its mapped reviewer.', 'Look up {path} in {mapping} (path=reviewer) and send a review request for {change} to that reviewer.'), answers=('{result}.', '{result}.'), cases=cases),),
)
