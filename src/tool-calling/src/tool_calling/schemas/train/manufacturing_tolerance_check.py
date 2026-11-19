from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        nominal = rng.randint(20, 80)
        tolerance = rng.randint(2, 5)
        offset = rng.randint(-tolerance - 3, tolerance + 3)
        yield {"nominal": str(nominal), "tolerance": str(tolerance), "measurement": str(nominal + offset)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(nominal, tolerance, measurement):
    return "within tolerance" if abs(int(measurement) - int(nominal)) <= int(tolerance) else "outside tolerance"


SCHEMA = Schema(
    id="manufacturing_tolerance_check",
    tool_names=("check_measurement_tolerance", "evaluate_part_tolerance", "assess_measurement_tolerance", "classify_part_measurement", "compare_measurement_to_tolerance", "determine_tolerance_status", "evaluate_measurement_limits", "check_part_size_tolerance", "calculate_tolerance_conformance", "assess_nominal_deviation"),
    descriptions=("Check a measurement against a nominal value and symmetric inclusive tolerance.", "Determine whether the measurement lies within the inclusive tolerance.", "Classify a measured size relative to nominal plus or minus the allowed deviation.", "Assess whether the absolute deviation from nominal is within tolerance, including both limits.", "Compare a part measurement with the inclusive symmetric tolerance interval.", "Return whether the measurement is within or outside the nominal tolerance.", "Evaluate a measurement against its nominal value and allowed deviation.", "Check if a measured dimension meets inclusive upper and lower tolerance bounds.", "Determine tolerance conformance using the absolute difference from nominal.", "Assess a part size against a symmetric tolerance around its nominal size."),
    parameters=(Parameter(names=("nominal", "nominal_size")), Parameter(names=("tolerance", "allowed_deviation")), Parameter(names=("measurement", "measured_size"))),
    tasks=(Task(id="tolerance", prompts=("Nominal size is {nominal} mm with tolerance ±{tolerance} mm, inclusive. Is a measurement of {measurement} mm within tolerance?", "Check {measurement} mm against {nominal} ± {tolerance} mm. Both limits pass.", "Does {measurement} mm meet a nominal size of {nominal} mm with an inclusive ±{tolerance} mm tolerance?", "Classify a {measurement} mm measurement against {nominal} mm plus or minus {tolerance} mm, including the endpoints.", "A part measures {measurement} mm; its nominal size is {nominal} mm and tolerance is ±{tolerance} mm. Are the inclusive limits met?", "Is {measurement} mm within the inclusive range defined by {nominal} ± {tolerance} mm?", "Check whether a measured {measurement} mm is within {tolerance} mm of the nominal {nominal} mm; equality is acceptable.", "For a nominal {nominal} mm and symmetric tolerance of {tolerance} mm, assess the {measurement} mm measurement, counting either limit as passing.", "Determine whether {measurement} mm is inside or outside the {nominal} ± {tolerance} mm tolerance, with both boundaries included.", "The target is {nominal} mm, with an allowed deviation of {tolerance} mm inclusive. Does {measurement} mm pass?", "Evaluate {measurement} mm against a {nominal} mm nominal dimension and inclusive ±{tolerance} mm tolerance.", "Is the deviation of {measurement} mm from {nominal} mm no greater than the allowed {tolerance} mm?"), answers=("The measurement is {result}.", "Result: {result}."), cases=cases),),
)
