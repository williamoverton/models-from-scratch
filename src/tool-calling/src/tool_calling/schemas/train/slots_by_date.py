from datetime import date as Date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        day = Date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        yield {"date": day.isoformat()}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"date": case["date"]})


SCHEMA = Schema(
    id="schedule_list_by_date",
    tool_names=("list_date_slots", "show_day_availability", "get_appointment_slots_by_date", "find_daily_open_slots", "list_available_times", "get_day_appointment_times", "lookup_date_availability", "show_available_appointments", "retrieve_daily_slots", "find_appointments_on_date"),
    descriptions=("Look up available appointment times for a date.", "List open slots on a specified day.", "Return the available appointment times for the given date.", "Find open appointment slots on a particular day.", "Show the scheduled availability for a specified date.", "Retrieve the available time slots for one calendar date.", "List appointment times available on the requested day.", "Look up a day's open appointment times.", "Provide the available slots for an ISO calendar date.", "Display appointment availability for the supplied date."),
    parameters=(Parameter(names=("date", "day")),),
    tasks=(Task(id="list", prompts=("What appointment slots are available on {date}?", "List the open appointment times for {date}.", "Show me the available slots on {date}.", "Find appointment availability for {date}.", "Which times can I book on {date}?", "Retrieve the open slots for {date}.", "Give me the appointment times available on {date}.", "Check the schedule for open appointments on {date}.", "Show the bookable times for {date}.", "What openings are there on {date}?", "Please look up available appointments for {date}.", "Display the slots available on the date {date}."), answers=("{result}", "Here are the slots: {result}"), cases=cases),),
)


def resolve(date):
    day = Date.fromisoformat(date)
    first = 8 + day.toordinal() % 3
    slots = ", ".join(f"{hour:02d}:00" for hour in (first, first + 3, first + 6))
    return f"Available slots on {date}: {slots}."
