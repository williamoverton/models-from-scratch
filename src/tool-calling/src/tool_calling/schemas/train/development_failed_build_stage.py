from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        stages = rng.sample(['compile', 'package', 'unit-tests', 'integration-tests', 'deploy', 'lint'], 3)
        statuses = ['passed', 'passed', 'failed']
        rng.shuffle(statuses)
        yield {'report': '; '.join(f'{stage}={status}' for stage, status in zip(stages, statuses))}


def prepare(*, task_id, case):
    entries = (entry.strip().split('=') for entry in case['report'].split(';'))
    return Decision(fields=case, arguments={'stage': next(stage for stage, status in entries if status == 'failed')})


def resolve(stage):
    return f'Inspected build stage: {stage}'


SCHEMA = Schema(
    id='development_inspect_failed_build_stage',
    tool_names=('inspect_build_stage', 'view_build_stage', 'inspect_stage', 'view_stage', 'inspect_build_step', 'view_build_step', 'open_build_stage', 'examine_build_stage', 'inspect_stage_by_id', 'get_build_stage_inspection'),
    descriptions=('Inspect the supplied build stage.', 'View a build stage.', 'Inspect the specified build stage.', 'View the supplied build stage by ID.', 'Inspect a build stage identified by the supplied ID.', 'View the given build step.', 'Open the specified build stage for inspection.', 'Examine the provided build stage.', 'Inspect a build stage by its identifier.', 'Get an inspection of the supplied build stage.'),
    parameters=(Parameter(names=('stage', 'stage_id')),),
    tasks=(Task(id='inspect', prompts=('Inspect the failed build stage. Report stage=status: {report}.', 'In build report {report} (stage=status), inspect the failed stage.', 'Find and inspect the failed stage in {report}, where entries are stage=status.', 'Which build stage failed? Inspect it using the stage=status report {report}.', 'Please inspect the failed build stage from these stage=status entries: {report}.', 'Using the build report {report} (stage=status), inspect the stage that failed.', 'Identify the failed stage in {report} and inspect it; entries are stage=status.', 'The build report lists stage=status: {report}. Inspect the failure.', 'From {report}, a stage=status build report, open an inspection of the failed stage.', 'Inspect the stage marked failed in the build report {report} (stage=status).', 'Given these build stage statuses, inspect the failed stage: {report}. Entries are stage=status.', 'Use {report} (stage=status) to find and inspect the failed build stage.'), answers=('{result}.', '{result}.'), cases=cases),),
)
