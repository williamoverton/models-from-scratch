from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        files = rng.sample(['auth.py', 'billing.py', 'search.py', 'profile.py', 'catalog.py', 'deploy.py'], 3)
        errors = rng.sample(range(1, 25), 3)
        yield {'report': '; '.join(f'{file}={error}' for file, error in zip(files, errors))}


def prepare(*, task_id, case):
    entries = [entry.strip().split('=') for entry in case['report'].split(';')]
    file = max(entries, key=lambda entry: int(entry[1]))[0]
    return Decision(fields=case, arguments={'file': file})


def resolve(file):
    return f'Flagged file: {file}'


SCHEMA = Schema(
    id='development_flag_most_lint_errors',
    tool_names=('flag_lint_file', 'flag_file', 'mark_lint_file', 'flag_file_for_lint_review', 'mark_file_for_lint_review', 'record_lint_flag', 'submit_lint_file', 'flag_lint_review', 'register_lint_flag', 'identify_lint_file'),
    descriptions=('Flag the supplied file.', 'Flag a file for lint review.', 'Flag the supplied file for lint review.', 'Mark the given file for lint review.', 'Flag a file identifier for lint review.', 'Record a lint-review flag for the supplied file.', 'Submit the specified file for lint review.', 'Flag the named file for review of lint errors.', 'Register a lint flag for the given file.', 'Identify the supplied file for lint review.'),
    parameters=(Parameter(names=('file', 'file_path')),),
    tasks=(Task(id='flag', prompts=('Flag the file with the most lint errors. Report file=error count: {report}.', 'From lint counts {report} (file=count), flag the file with the highest count.', 'Using {report} as file=lint error count, flag the file with the most errors.', 'Which file has the greatest lint error count? Flag it; report file=count: {report}.', 'Flag the highest-count file in this lint report, where entries are file=count: {report}.', 'Please flag the file with the maximum lint errors in {report} (file=error count).', 'The lint report is {report}, with file=error count entries. Flag the file with the most.', 'Find and flag the file with the largest lint error count from {report} (file=count).', 'For lint counts {report}, given as file=count, flag the file with the highest count.', 'Inspect the lint counts {report} (file=error count) and flag the worst file by count.', 'Identify and flag the file with the most lint errors; the file=count report is {report}.', 'From these file=lint error count entries, flag the file with the greatest count: {report}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
