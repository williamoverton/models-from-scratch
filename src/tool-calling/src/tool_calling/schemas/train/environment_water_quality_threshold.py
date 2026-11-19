from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        threshold = rng.randint(5, 30)
        yield {"reading": max(0, threshold + rng.randint(-5, 5)), "threshold": threshold}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(reading, threshold):
    return "above threshold" if int(reading) > int(threshold) else "not above threshold"


SCHEMA = Schema(
    id="environment_water_quality_threshold",
    tool_names=("compare_water_reading", "check_reading_threshold", "check_water_measurement_limit", "compare_sample_to_threshold", "test_water_reading_above", "evaluate_water_threshold", "check_sample_reading", "assess_measurement_against_limit", "compare_water_quality_value", "determine_reading_above_threshold"),
    descriptions=("Compare a water measurement with the supplied threshold.", "Report whether a reading strictly exceeds a threshold.", "Check if the water reading is greater than the supplied limit; equality is not above.", "Compare the sample measurement against its threshold using strict greater-than.", "Determine whether a reading exceeds, rather than equals, the threshold.", "Classify the water measurement as above or not above the limit.", "Test a water reading against a threshold, treating equality as not above.", "Report above threshold only when the reading is greater than the limit.", "Evaluate whether the supplied measurement strictly exceeds its threshold.", "Compare the water sample reading with the provided cutoff."),
    parameters=(Parameter(names=("reading", "measurement")), Parameter(names=("threshold", "limit"))),
    tasks=(Task(id="compare", prompts=("A water sample reading is {reading} mg/L; the comparison threshold is {threshold} mg/L. Is the reading strictly above the threshold?", "Compare {reading} mg/L with {threshold} mg/L. Report above threshold only if the reading is greater; equality is not above.", "Is the water reading of {reading} mg/L greater than the {threshold} mg/L threshold? Equality does not count as above.", "Classify a water sample at {reading} mg/L against {threshold} mg/L: above only means strictly greater.", "The threshold is {threshold} mg/L and the reading is {reading} mg/L. Is it strictly above?", "Check whether {reading} mg/L exceeds {threshold} mg/L, treating equality as not above.", "A sample measured {reading} mg/L against a {threshold} mg/L cutoff. Report whether it is above; equal is not above.", "Does the water measurement {reading} mg/L strictly exceed its {threshold} mg/L threshold?", "Compare the water reading {reading} mg/L to the limit {threshold} mg/L. Only a greater reading is above.", "Is {reading} mg/L above {threshold} mg/L? Use a strict comparison, so equal values are not above.", "Evaluate a {reading} mg/L sample with a threshold of {threshold} mg/L; above requires a strictly higher reading.", "For a water reading of {reading} mg/L and threshold of {threshold} mg/L, say whether the reading is strictly above."), answers=("{result}.", "{result}."), cases=cases),),
)
