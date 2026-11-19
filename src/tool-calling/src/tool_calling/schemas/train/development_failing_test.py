from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        statuses = ['passed', 'passed', 'failed']
        rng.shuffle(statuses)
        yield {'report': '; '.join(f'T-{i}={status}' for i, status in zip(ids, statuses))}


def prepare(*, task_id, case):
    entries = (entry.strip().split('=') for entry in case['report'].split(';'))
    return Decision(fields=case, arguments={'test_id': next(test for test, status in entries if status == 'failed')})


def resolve(test_id):
    return f'Inspected test: {test_id}'


SCHEMA = Schema(
    id='development_inspect_failing_test',
    tool_names=('inspect_test', 'view_test', 'inspect_test_by_id', 'view_test_by_id', 'examine_test', 'open_test_inspection', 'get_test_inspection', 'inspect_reported_test', 'view_reported_test', 'request_test_inspection'),
    descriptions=('Inspect the supplied test.', 'View a test by ID.', 'Inspect the specified test by ID.', 'View the supplied test identifier.', 'Examine the given test.', 'Open an inspection of the supplied test.', 'Get an inspection of a test by ID.', 'Inspect the specified reported test.', 'View the specified reported test.', 'Request an inspection of the given test.'),
    parameters=(Parameter(names=('test_id', 'test')),),
    tasks=(Task(id='inspect', prompts=('Inspect the failed test in this report (test ID=status): {report}.', 'Report {report} uses test ID=status. Inspect the one failed test.', 'Find and inspect the failed test in {report}, where entries are test ID=status.', 'Which test failed? Inspect it using this test ID=status report: {report}.', 'Please inspect the failed test from {report} (test ID=status).', 'The report lists test ID=status: {report}. Inspect the test marked failed.', 'Identify the one failed test in {report} and inspect it; entries are test ID=status.', 'Using {report} as test ID=status pairs, inspect the failing test.', 'Open an inspection of the failed test in this test ID=status report: {report}.', 'From test statuses {report} (test ID=status), inspect the one that failed.', 'Inspect whichever test is marked failed in {report}; the entries are test ID=status.', 'Review {report}, which maps test IDs to statuses, and inspect the failed test.'), answers=('{result}.', '{result}.'), cases=cases),),
)
