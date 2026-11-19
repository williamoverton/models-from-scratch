from ...schema_types import Decision, Schema, Parameter, Task


HOURS = {
    "North": {"weekday": "08:00-18:00", "Saturday": "09:00-14:00", "Sunday": "closed"},
    "South": {"weekday": "07:00-19:00", "Saturday": "10:00-16:00", "Sunday": "closed"},
    "Central": {"weekday": "06:00-22:00", "Saturday": "08:00-20:00", "Sunday": "10:00-18:00"},
    "West": {"weekday": "09:00-17:00", "Saturday": "closed", "Sunday": "closed"},
}
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def cases(rng, count):
    for _ in range(count):
        yield {"building": rng.choice(tuple(HOURS)), "day": rng.choice(DAYS)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="facilities_building_hours",
    tool_names=('lookup_building_hours', 'get_building_schedule', 'find_sample_building_hours', 'check_building_hours', 'get_sample_opening_hours', 'lookup_sample_schedule', 'building_hours_for_day', 'find_building_opening_times', 'get_building_day_hours', 'report_sample_building_hours'),
    descriptions=('Look up sample building opening hours for a named day of the week.', 'Return a sample building’s opening hours or closed status on a specified day.', 'Find the sample opening schedule for a building and weekday.', 'Check whether a sample building is open and its hours on a given day.', 'Retrieve the sample hours or closed status for a building on a named day.', 'Look up a sample building’s daily opening interval.', 'Report the sample schedule for the specified building and day of the week.', 'Get the daily opening hours or closed status from the sample building schedule.', 'Find a building’s sample opening hours for the requested day.', 'Return the sample building schedule entry for a given day.'),
    parameters=(Parameter(names=("building", "building_name")), Parameter(names=("day", "day_of_week"))),
    tasks=(Task(id="hours", prompts=("What are the sample {building} building hours on {day}?", "Find the {day} opening hours for the sample {building} building.", 'Look up the sample opening hours of the {building} building for {day}.', 'On {day}, when is the sample {building} building open?', 'Report the sample {building} building schedule for {day}, including if it is closed.', 'Find whether the sample {building} building is open on {day} and its hours.', 'For {day}, retrieve the sample hours or closed status of the {building} building.', 'What schedule does the sample {building} building have on {day}?', 'Check the sample {building} building opening times for {day}.', 'Give the {day} hours for the sample building named {building}.', 'Is the sample {building} building open on {day}, and what are its hours?', 'Consult the sample schedule for the {building} building on {day}.'), answers=("The {building} building on {day}: {result}.", "On {day}, {building} is {result}."), cases=cases),),
)


def resolve(building, day):
    category = "weekday" if day in DAYS[:5] else day
    hours = HOURS[building][category]
    return "closed" if hours == "closed" else f"open {hours}"
