from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        start = rng.randrange(0, 1440, 5)
        yield {"start": f"{start // 60:02d}:{start % 60:02d}", "minutes": str(rng.randrange(5, 361, 5))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(start, minutes):
    hour, minute = map(int, start.split(":"))
    total = hour * 60 + minute + int(minutes)
    day = "next day" if total >= 1440 else "same day"
    total %= 1440
    return f"{total // 60:02d}:{total % 60:02d} ({day})"


SCHEMA = Schema(
    id="food_cooking_finish_time",
    tool_names=('calculate_cooking_finish', 'find_cooking_end_time', 'compute_cooking_finish_time', 'get_cooking_end_clock', 'add_cooking_minutes', 'determine_cooking_finish_time', 'calculate_cooking_end_clock', 'find_recipe_finish_time', 'compute_cooking_end_time', 'derive_cooking_finish_clock'),
    descriptions=('Add cooking minutes to a 24-hour start time and report the day.', 'Calculate the finish clock time and whether it is on the same or next day.', 'Add the cooking duration to the start and indicate same day or next day.', 'Find the 24-hour finish time for a start time and duration in minutes, with the day rollover.', 'Compute when cooking ends and report whether it finishes the same or next day.', 'Determine the cooking end clock from a start and minutes, indicating the day.', 'Return the finish time in 24-hour format with same-day or next-day status.', 'Calculate the end time after the given cooking minutes, including day rollover.', 'Find the clock time and day relation after adding a cooking duration.', 'Add the duration to the cooking start and report the resulting clock and day.'),
    parameters=(Parameter(names=("start", "start_time")), Parameter(names=("minutes", "duration_minutes"))),
    tasks=(Task(id="finish", prompts=("Cooking starts at {start} and takes {minutes} minutes. When does it finish? Specify same day or next day.", "Find the finish time, including whether it is the same or next day, for {minutes} minutes of cooking beginning at {start}.", "Starting at {start}, cook for {minutes} minutes. Give the finish time and whether it is the same or next day.", "What time does cooking end if it starts at {start} and lasts {minutes} minutes? Include same-day or next-day status.", "Add {minutes} cooking minutes to {start}; report the 24-hour finish time and day rollover.", "Cooking begins at {start} for {minutes} minutes. When is it done, and is that the same day or next day?", "Calculate the finish clock time for a {start} start and {minutes}-minute cooking duration, indicating same or next day.", "If cooking runs {minutes} minutes from {start}, what is the end time and relative day?", "At {start} I begin cooking for {minutes} minutes. State the finish time and whether it falls on the same or next day.", "Work out the 24-hour end time after {minutes} minutes starting at {start}, noting same day or next day.", "When will a {minutes}-minute cook begun at {start} finish? Include whether it rolls into the next day.", "Give the finish time and same-day or next-day designation for cooking from {start} lasting {minutes} minutes."), answers=("Cooking finishes at {result}.", "Finish: {result}."), cases=cases),),
)
