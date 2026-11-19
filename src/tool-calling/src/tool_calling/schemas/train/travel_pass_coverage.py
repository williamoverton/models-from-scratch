from ...schema_types import Decision, Schema, Parameter, Task


COVERAGE = {"local": ("A",), "regional": ("A", "B"), "network": ("A", "B", "C", "D")}


def cases(rng, count):
    for _ in range(count):
        yield {"pass_type": rng.choice(tuple(COVERAGE)), "zone": rng.choice(("A", "B", "C", "D"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="travel_pass_coverage",
    tool_names=('check_pass_zone', 'pass_coverage', 'check_zone_coverage', 'determine_pass_coverage', 'lookup_pass_zone', 'check_transit_pass_zone', 'verify_pass_coverage', 'assess_pass_zone', 'get_pass_zone_coverage', 'evaluate_pass_coverage'),
    descriptions=('Check whether a sample pass type covers a transit zone.', 'Determine zone coverage for a sample transit pass.', 'Check a zone against the sample pass coverage.', 'Report whether the named sample pass includes the given zone.', 'Look up coverage of a zone by a sample pass type.', 'Evaluate whether a sample transit pass covers a specified zone.', 'Determine if a zone is included with a sample pass.', 'Compare a sample pass type with a transit zone.', 'Return the sample pass coverage status for a zone.', 'Check the given zone against the sample transit pass.'),
    parameters=(Parameter(names=("pass_type", "pass_name")), Parameter(names=("zone", "travel_zone"))),
    tasks=(Task(id="coverage", prompts=("Does the sample {pass_type} pass cover zone {zone}?", "Check whether zone {zone} is included in the sample {pass_type} transit pass.", 'In the sample system, is zone {zone} covered by a {pass_type} pass?', 'Determine whether the sample {pass_type} pass includes zone {zone}.', 'For zone {zone}, check coverage under the sample {pass_type} transit pass.', 'Would the sample {pass_type} pass cover travel in zone {zone}?', 'Look up whether zone {zone} falls within the sample {pass_type} pass coverage.', 'Does zone {zone} belong to the zones covered by the sample {pass_type} pass?', 'Assess the sample {pass_type} pass against zone {zone}. Is it covered?', 'Check the sample coverage of zone {zone} for pass type {pass_type}.', 'Is a sample {pass_type} transit pass valid for zone {zone}?', 'Report whether the sample {pass_type} pass covers the specified zone {zone}.'), answers=("{result}", "Sample coverage result: {result}"), cases=cases),),
)


def resolve(pass_type, zone):
    status = "covers" if zone in COVERAGE[pass_type] else "does not cover"
    return f"The {pass_type} pass {status} zone {zone}."
