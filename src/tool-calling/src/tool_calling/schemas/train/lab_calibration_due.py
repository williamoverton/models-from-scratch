from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        today = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        ids = rng.sample(range(100, 1000), 3)
        due_count = rng.choice((1, 2))
        due_offsets = rng.sample(range(-30, 0), due_count)
        if rng.choice((True, False)):
            due_offsets[0] = 0
        future_offsets = rng.sample(range(1, 51), 3 - due_count)
        dates = [today + timedelta(days=offset) for offset in due_offsets + future_offsets]
        entries = list(zip(ids, dates))
        rng.shuffle(entries)
        yield {"today": today.isoformat(), "instruments": "; ".join(f"I-{ident}={due.isoformat()}" for ident, due in entries)}


def prepare(*, task_id, case):
    entries = (entry.split("=") for entry in case["instruments"].split("; "))
    instrument, _ = max(
        ((ident, due) for ident, due in entries if due <= case["today"]),
        key=lambda entry: entry[1],
    )
    return Decision(fields=case, arguments={"instrument": instrument})


def resolve(instrument):
    return f"Calibration requested for {instrument}"


SCHEMA = Schema(
    id="lab_calibration_due",
    tool_names=("request_calibration", "schedule_instrument_calibration", "request_instrument_calibration", "record_calibration_request", "submit_calibration_request", "request_lab_instrument_calibration", "create_instrument_calibration_request", "record_instrument_calibration_request", "request_calibration_by_instrument_id", "submit_instrument_calibration_request"),
    descriptions=("Request calibration for the specified instrument ID.", "Record a calibration request for an instrument.", "Submit a calibration request for the selected instrument.", "Request calibration of the instrument identified by the supplied ID.", "Record a request to calibrate the specified lab instrument.", "Create a calibration request for the given instrument identifier.", "Request instrument calibration using the selected instrument ID.", "Submit a request to calibrate a particular laboratory instrument.", "Record the selected instrument's calibration request.", "Request calibration for the instrument passed as an argument."),
    parameters=(Parameter(names=("instrument", "instrument_id")),),
    tasks=(Task(id="calibrate", prompts=(
        "Today is {today}. Instrument calibration due dates: {instruments}. Request calibration for the instrument with the most recent due date on or before today.",
        "From {instruments}, request calibration for the instrument with the latest due date no later than {today}.",
        "On {today}, select the instrument most recently due for calibration, including today, from {instruments}, and request calibration.",
        "Instrument due dates are {instruments}; today is {today}. Request calibration for the latest date that is today or earlier.",
        "Find the instrument in {instruments} whose calibration due date is closest to {today} without being later, and request calibration.",
        "Request calibration for the most recently due instrument as of {today}, counting dates on today: {instruments}.",
        "Using {today} as today, inspect {instruments} and request calibration for the latest due date at or before today.",
        "The due dates are {instruments}. As of {today}, request calibration for the instrument with the most recent date that has arrived.",
        "Which instrument in {instruments} has the latest calibration due date at or before {today}? Request its calibration.",
        "From {instruments}, request calibration for the instrument most recently due by {today}, including a date of {today}.",
        "Treat {today} as the current date. Among {instruments}, submit a calibration request for the latest due date not after today.",
        "Among these instrument calibration dates {instruments}, request calibration for the most recent date less than or equal to {today}.",
    ), answers=("{result}.", "{result}."), cases=cases),),
)
