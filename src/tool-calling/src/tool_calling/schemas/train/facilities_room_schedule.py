from ...schema_types import Decision, Parameter, Schema, Task


SCHEDULE = {
    ("Ash", "2026-11-02"): "09:00-10:00 planning; 14:00-15:00 review",
    ("Ash", "2026-11-03"): "11:00-12:00 interview",
    ("Birch", "2026-11-02"): "10:00-11:30 workshop",
    ("Birch", "2026-11-03"): "13:00-14:00 briefing",
    ("Cedar", "2026-11-02"): "No bookings",
    ("Cedar", "2026-11-03"): "15:00-16:00 training",
}


def cases(rng, count):
    for _ in range(count):
        room, day = rng.choice(tuple(SCHEDULE))
        yield {"room": room, "day": day}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(room, day):
    return f"{room} on {day}: {SCHEDULE[(room, day)]}."


SCHEMA = Schema(
    id="facilities_room_schedule",
    tool_names=("get_room_schedule", "lookup_room_bookings", "find_room_schedule", "get_sample_room_bookings", "lookup_booking_schedule", "retrieve_room_schedule", "find_sample_room_bookings", "read_room_bookings", "get_daily_room_schedule", "lookup_room_schedule_by_date"),
    descriptions=("Look up a room's schedule for a date in the sample booking registry.", "Find sample bookings by room and date.", "Retrieve the sample booking schedule for a room on a given date.", "Return the bookings recorded for a room and day in the sample registry.", "Look up a room and date in the sample schedule.", "Find a room's daily bookings in the sample data.", "Read the sample room schedule for the specified date.", "Get the sample bookings associated with a room and day.", "Return a dated room schedule from the sample booking registry.", "Retrieve the sample schedule entry for the given room and date."),
    parameters=(Parameter(names=("room", "room_name")), Parameter(names=("day", "date"))),
    tasks=(Task(id="lookup", prompts=("What is the schedule for room {room} on {day}?", "Look up bookings for {room} on {day}.", "Show the sample booking schedule for {room} on {day}.", "What bookings does room {room} have on {day} in the sample registry?", "Find the schedule entry for {room} on {day}.", "Retrieve {room}'s bookings for {day} from the sample schedule.", "Check the room schedule for {room} on {day}.", "Which bookings are listed for room {room} on {day}?", "Give me the sample schedule for {room} dated {day}.", "Read the booking registry entry for {room} on {day}.", "What is booked in {room} on {day} according to the sample registry?", "Get the daily schedule for room {room} on {day}."), answers=("{result}", "{result}"), cases=cases),),
)
