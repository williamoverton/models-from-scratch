from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        modules = rng.sample(['auth', 'billing', 'search', 'profile', 'catalog', 'checkout'], 3)
        tests = [f'test_{module}' for module in modules]
        yield {'mapping': '; '.join(f'{module}={test}' for module, test in zip(modules, tests)), 'module': rng.choice(modules)}


def prepare(*, task_id, case):
    mapping = dict(entry.strip().split('=') for entry in case['mapping'].split(';'))
    return Decision(fields=case, arguments={'test_id': mapping[case['module']]})


def resolve(test_id):
    return f'Ran test: {test_id}'


SCHEMA = Schema(
    id='development_run_mapped_test',
    tool_names=('run_test', 'execute_test', 'run_test_by_id', 'execute_test_by_id', 'invoke_test', 'start_test', 'run_named_test', 'execute_named_test', 'launch_test', 'run_selected_test'),
    descriptions=('Run the supplied test.', 'Execute a test by ID.', 'Run the specified test by ID.', 'Execute the supplied test identifier.', 'Invoke the given test.', 'Start the supplied test.', 'Run the specified named test.', 'Execute the given named test.', 'Launch the supplied test by ID.', 'Run the selected test identifier.'),
    parameters=(Parameter(names=('test_id', 'test')),),
    tasks=(Task(id='run', prompts=('Module {module} changed. Run its test using this module=test mapping: {mapping}.', 'Using module=test pairs {mapping}, run the test for changed module {module}.', 'Run the test mapped to changed module {module}; module=test pairs: {mapping}.', 'The changed module is {module}. Find and execute its test in {mapping} (module=test).', 'From the module=test mapping {mapping}, run the test associated with changed module {module}.', 'Which test belongs to changed module {module}? Run it using {mapping} (module=test).', 'Please execute the test for {module}, the changed module, using the module=test mapping {mapping}.', 'A change was made to {module}. Run its mapped test from these module=test pairs: {mapping}.', 'Use {mapping} (module=test) to select and run the test for changed module {module}.', 'Find the test for changed module {module} in {mapping}, where entries are module=test, and run it.', 'Execute the test corresponding to {module}, which changed, according to module=test entries {mapping}.', 'The module=test map is {mapping}; run the test assigned to the changed module {module}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
