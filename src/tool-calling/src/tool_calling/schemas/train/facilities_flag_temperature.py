from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        low = rng.randint(17, 20)
        high = rng.randint(23, 26)
        names = rng.sample(("Ash", "Birch", "Cedar", "Elm", "Fir", "Maple"), 3)
        bad = rng.randrange(3)
        readings = [rng.randint(low, high) for _ in names]
        readings[bad] = rng.choice((low - rng.randint(1, 4), high + rng.randint(1, 4)))
        yield {"low": str(low), "high": str(high), "readings": ", ".join(f"{name}={value}" for name, value in zip(names, readings))}


def prepare(*, task_id, case):
    readings = (entry.split("=") for entry in case["readings"].split(", "))
    room = next(name for name, value in readings if not int(case["low"]) <= int(value) <= int(case["high"]))
    return Decision(fields=case, arguments={"room": room})


def resolve(room):
    return f"Flagged room: {room}."


SCHEMA = Schema(
    id="facilities_flag_temperature",
    tool_names=("flag_room_temperature", "mark_room_for_temperature_review", "flag_temperature_review", "mark_room_temperature_check", "record_temperature_flag", "report_room_temperature_flag", "flag_room_for_review", "register_temperature_review_room", "identify_room_for_temperature_check", "set_room_temperature_review"),
    descriptions=("Flag a room for temperature review by name.", "Mark the specified room for a temperature check.", "Record the named room as flagged for temperature review.", "Report a room selected for a temperature check.", "Flag the supplied room name for temperature review.", "Identify the room to be reviewed for temperature.", "Mark a named room for temperature-related attention.", "Return a temperature-review flag for the specified room.", "Register the room name for a temperature check.", "Record which room should receive a temperature review."),
    parameters=(Parameter(names=("room", "room_name")),),
    tasks=(Task(id="flag", prompts=("Room temperatures in Celsius: {readings}. The acceptable range is {low} to {high}, inclusive. Flag the room outside that range.", "Flag the room with a temperature below {low} C or above {high} C: {readings}. Both limits are acceptable.", "From Celsius readings {readings}, flag the room outside the inclusive {low} to {high} range.", "Which room should be flagged in {readings}? Temperatures from {low} to {high} Celsius, including both endpoints, are acceptable.", "Review {readings} in Celsius and flag the room below {low} or above {high}; readings exactly at either limit are acceptable.", "Flag the room whose Celsius reading in {readings} lies outside [{low}, {high}], with both limits included.", "Temperatures: {readings} Celsius. Identify and flag the room not within {low}–{high}, inclusive.", "Using {readings} as Celsius temperatures, flag the room outside the acceptable inclusive bounds of {low} and {high}.", "Find the room in {readings} that needs a temperature review: values under {low} or over {high} Celsius are unacceptable, but the limits themselves are fine.", "Given {readings} in Celsius, mark the room whose temperature is not between {low} and {high} inclusive.", "Flag the out-of-range room from {readings}; the allowed Celsius range includes both {low} and {high}.", "For the Celsius room readings {readings}, flag the room below {low} or above {high}. Both boundary temperatures are allowed."), answers=("{result}", "{result}"), cases=cases),),
)
