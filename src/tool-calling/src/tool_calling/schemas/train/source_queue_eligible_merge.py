from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        statuses = [('approved', 'passed'), ('pending', 'passed'), ('approved', 'failed')]
        rng.shuffle(statuses)
        yield {'changes': '; '.join(f'C-{change}={review},{tests}' for change, (review, tests) in zip(ids, statuses))}


def prepare(*, task_id, case):
    entries = [entry.strip().split('=') for entry in case['changes'].split(';')]
    change = next(change for change, status in entries if status == 'approved,passed')
    return Decision(fields=case, arguments={'change': change})


def resolve(change):
    return f'Queued merge for change: {change}'


SCHEMA = Schema(
    id='source_queue_eligible_merge',
    tool_names=('queue_merge', 'enqueue_merge', 'queue_change_for_merge', 'enqueue_change_for_merge', 'add_change_to_merge_queue', 'queue_merge_for_change', 'enqueue_change_merge', 'submit_change_to_merge_queue', 'place_change_in_merge_queue', 'queue_specified_change_merge'),
    descriptions=('Queue the supplied change for merge.', 'Enqueue a change for merge.', 'Add the specified change to the merge queue.', 'Queue a merge for the identified change.', 'Place a change in the merge queue.', 'Enqueue the supplied change for merging.', 'Submit the specified change to the merge queue.', 'Queue the given change ID for merge.', 'Add the identified change to the queue for merging.', 'Enqueue a merge for the supplied change.'),
    parameters=(Parameter(names=('change', 'change_id')),),
    tasks=(Task(id='queue', prompts=('Queue the change that has an approved review AND passed tests. Entries are change ID=review,test: {changes}.', 'Among {changes} (change ID=review,test), queue the one with review approved and tests passed.', 'From {changes}, formatted ID=review,test, queue the change with approved review and passed tests.', 'Queue the eligible merge in {changes}: eligibility requires approved review and passed tests; entries are ID=review,test.', 'Find the change in {changes} with both review approved and tests passed, and queue it. Format: ID=review,test.', 'Using {changes} (ID=review,test), queue only the change that is approved and has passed tests.', 'Which change in {changes} has an approved review and passed tests? Queue it; format is ID=review,test.', 'Check {changes} as ID=review,test and queue the change meeting both approved and passed.', 'Add to the merge queue the approved, test-passing change in {changes}; entries are ID=review,test.', 'Queue the change satisfying review=approved and tests=passed in {changes}, whose entries are ID=review,test.', 'For {changes} (change ID=review,test), enqueue the change only if its review is approved and tests passed.', 'Identify and queue the merge-ready change in {changes}: approved review AND passed tests, in ID=review,test format.'), answers=('{result}.', '{result}.'), cases=cases),),
)
