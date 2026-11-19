from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        opening = rng.randrange(7, 11) * 60
        closing = rng.randrange(16, 21) * 60
        time = rng.choice((opening, closing, opening - 30, closing + 30, rng.randrange(opening, closing, 30)))
        fmt = lambda t: f"{t // 60:02d}:{t % 60:02d}"
        yield {"opening": fmt(opening), "closing": fmt(closing), "time": fmt(time)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="schedule_opening_check",
    tool_names=("check_opening_hours", "is_time_open", "check_time_within_hours", "determine_business_hours_status", "compare_time_to_opening_hours", "check_daily_hours", "evaluate_open_time", "find_hours_membership", "check_business_time", "assess_time_against_hours"),
    descriptions=("Check a time against inclusive opening and exclusive closing times.", "Determine whether a time falls within business hours, including opening but excluding closing.", "Test whether a time is at or after opening and before closing.", "Check if a clock time lies in the half-open interval of business hours.", "Classify a time as within or outside the given opening and closing times.", "Determine whether a time is in the interval from opening inclusive to closing exclusive.", "Compare a time with business hours, counting opening but not closing.", "Report whether the specified time falls within the half-open hours.", "Evaluate a time against an inclusive opening and exclusive closing boundary.", "Check daily hours for a time, excluding the closing instant."),
    parameters=(Parameter(names=("time", "check_time")), Parameter(names=("opening", "opens_at")), Parameter(names=("closing", "closes_at"))),
    tasks=(Task(id="check", prompts=("Hours are {opening} to {closing}, opening inclusive and closing exclusive. Is {time} within hours?", "Does {time} fall in [{opening}, {closing})? Opening counts, closing does not.", "Check whether {time} is at or after {opening} and strictly before {closing}.", "Is {time} open if hours start at {opening} inclusive and end at {closing} exclusive?", "Compare {time} to hours {opening}–{closing}: include opening, exclude closing.", "Determine if {time} is within [{opening}, {closing}).", "For opening {opening} and closing {closing}, is {time} in hours? Count opening but not closing.", "Check {time} against {opening} through {closing}, including only the opening boundary.", "Is {time} at least {opening} and less than {closing}?", "Does {time} qualify under hours from {opening} inclusive to {closing} exclusive?", "Classify {time} as within or outside {opening}–{closing}; opening counts and closing does not.", "Given the half-open hours [{opening}, {closing}), check {time}."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(time, opening, closing):
    status = "within" if opening <= time < closing else "outside"
    return f"{time} is {status} the hours {opening}–{closing}."
