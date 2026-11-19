from ...schema_types import Decision, Schema, Parameter, Task


CAPACITIES = {"Ash": 8, "Birch": 12, "Cedar": 20, "Dogwood": 30, "Elm": 45, "Fir": 60, "Grove": 75, "Hazel": 100}


def cases(rng, count):
    for _ in range(count):
        yield {"room": rng.choice(tuple(CAPACITIES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="facilities_room_capacity",
    tool_names=("get_room_capacity", "room_seating_lookup", "lookup_room_capacity", "find_sample_room_capacity", "retrieve_room_occupancy", "get_sample_room_seating", "lookup_sample_occupancy", "find_room_seating_capacity", "read_room_capacity", "get_room_maximum_occupancy"),
    descriptions=("Look up the capacity of a room in the sample facilities directory.", "Return the sample room's maximum occupancy.", "Retrieve the seating capacity for a named room in the sample directory.", "Find a sample room's maximum number of occupants.", "Get the capacity associated with a room in the sample facilities data.", "Return the sample directory's occupancy limit for the named room.", "Read a room's seating capacity from the sample directory.", "Look up maximum occupancy for a specified sample room.", "Find the number of people a sample room holds.", "Retrieve the sample capacity for a room by name."),
    parameters=(Parameter(names=("room", "room_name")),),
    tasks=(Task(id="capacity", prompts=("What is the capacity of the sample {room} room?", "Look up the maximum occupancy for room {room} in the sample directory.", "How many people can the sample room {room} hold?", "Find the seating capacity of {room} in the sample facilities directory.", "What maximum occupancy is listed for {room} in the sample directory?", "Check the sample capacity for room {room}.", "Retrieve the sample directory's occupancy limit for {room}.", "In the sample facilities data, how many seats does {room} have?", "Give me the listed capacity of sample room {room}.", "Find the maximum number of occupants for {room} in the sample directory.", "What's the sample room {room}'s seating limit?", "Read the capacity entry for {room} from the sample facilities directory."), answers=("Room {room} holds {result} people.", "The capacity of {room} is {result} people."), cases=cases),),
)


def resolve(room):
    return str(CAPACITIES[room])
