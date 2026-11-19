from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 999), 3)
        counts = rng.sample(range(5, 300), 3)
        yield {'changes': '; '.join(f'C-{change}={lines}' for change, lines in zip(ids, counts))}


def prepare(*, task_id, case):
    entries = [entry.strip().split('=') for entry in case['changes'].split(';')]
    change = max(entries, key=lambda entry: int(entry[1]))[0]
    return Decision(fields=case, arguments={'change': change})


def resolve(change):
    return f'Inspected change: {change}'


SCHEMA = Schema(
    id='source_inspect_largest_change',
    tool_names=('inspect_change', 'view_change', 'report_inspected_change', 'acknowledge_change_inspection', 'return_inspected_change', 'show_inspected_change', 'report_change_inspection', 'confirm_change_inspection', 'echo_inspected_change', 'identify_inspected_change'),
    descriptions=('Inspect the supplied change.', 'View a change by ID.', 'Report the supplied change ID as inspected.', 'Acknowledge inspection of the given change identifier.', 'Return an inspection message for the supplied change.', 'Show the ID of the inspected change.', 'Report inspection of a change by ID.', 'Confirm the supplied change ID in an inspection message.', 'Echo the change identifier as inspected.', 'Identify the supplied change as inspected.'),
    parameters=(Parameter(names=('change', 'change_id')),),
    tasks=(Task(id='inspect', prompts=('Inspect the change with the most changed lines. Change ID=total changed lines: {changes}.', 'For {changes} (change ID=changed lines), inspect the change with the largest count.', 'In {changes}, each entry is change ID=changed lines. Inspect the largest change.', 'Compare changed-line counts in {changes} (ID=count) and inspect the highest.', 'Inspect the ID with the maximum changed lines in {changes}; entries are ID=count.', 'From {changes}, where each ID equals its changed-line count, inspect the greatest count.', 'Which change has the most changed lines in {changes}? Entries are ID=count; inspect it.', 'Using {changes} as change ID=total changed lines, inspect the largest by count.', 'Find the maximum line count in {changes} (ID=changed lines) and inspect that change.', 'Inspect the change associated with the highest count in {changes}; format is ID=changed lines.', 'Among {changes}, select and inspect the change with the most lines changed; ID=count.', 'Entries {changes} give change IDs and changed-line counts as ID=count. Inspect the highest.'), answers=('{result}.', '{result}.'), cases=cases),),
)
