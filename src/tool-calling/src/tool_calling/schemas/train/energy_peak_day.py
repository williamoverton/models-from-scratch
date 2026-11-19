from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    base = date(2021, 1, 1)
    for _ in range(count):
        start = base + timedelta(days=rng.randrange(2000))
        days = [(start + timedelta(days=i)).isoformat() for i in range(3)]
        usage = rng.sample(range(1, 101), 3)
        yield {"readings": "; ".join(f"{day}: {value} kWh" for day, value in zip(days, usage)), "choices": list(zip(days, usage))}


def prepare(*, task_id, case):
    day, _ = max(case["choices"], key=lambda choice: choice[1])
    return Decision(fields=case, arguments={"day": day})


def resolve(day):
    return f"Flagged day: {day}."


SCHEMA = Schema(
    id="energy_flag_maximum_usage_day",
    tool_names=('report_peak_usage_day', 'report_highest_daily_usage_selection', 'report_flagged_day', 'acknowledge_selected_day', 'return_flagged_date', 'report_peak_day_selection', 'confirm_day_flag', 'echo_selected_day', 'show_flagged_date', 'report_day_for_flagging'),
    descriptions=('Acknowledge the selected day identifier.', 'Report the date selected for flagging.', 'Return the supplied date as a flagged day.', 'Confirm the provided day as the flagging selection.', 'Show the selected date with a flagged label.', 'Report a flag for the given day.', 'Echo the provided date as flagged.', 'Return the selected day in a flagged-day message.', 'Present the supplied date as the flagged selection.', 'Output a flagged-day label for the given date.'),
    parameters=(Parameter(names=("day", "date")),),
    tasks=(Task(id="peak", prompts=("Which day had the maximum energy usage? {readings}.", "Flag the day with the highest kWh reading: {readings}.", 'Flag the date with the greatest kWh usage in these readings: {readings}.', 'From {readings}, identify and flag the highest-usage day.', 'Which date should be flagged for the largest energy reading? {readings}.', 'Select the peak consumption day and flag it: {readings}.', 'The daily readings are {readings}; flag the day with the most kWh.', 'Among {readings}, flag the date recording the maximum energy use.', 'Find the highest daily usage in {readings} and flag its day.', 'Flag the day corresponding to the largest kWh value: {readings}.', 'Given the energy readings {readings}, which day is the peak? Flag it.', 'Compare {readings} and flag the date with greatest consumption.'), answers=("{result}", "The selection is confirmed. {result}"), cases=cases),),
)
