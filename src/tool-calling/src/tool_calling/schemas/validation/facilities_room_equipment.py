from ...schema_types import Decision, Schema, Parameter, Task


EQUIPMENT = {
    "Ash": ("projector", "whiteboard"),
    "Birch": ("video conferencing", "whiteboard"),
    "Cedar": ("projector", "microphone"),
    "Elm": ("video conferencing", "microphone", "projector"),
    "Fir": ("whiteboard",),
    "Hazel": ("microphone", "whiteboard"),
}


def cases(rng, count):
    for _ in range(count):
        yield {"room": rng.choice(tuple(EQUIPMENT)), "equipment": rng.choice(("projector", "whiteboard", "microphone", "video conferencing"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="facilities_room_equipment",
    tool_names=('check_room_equipment', 'room_has_equipment', 'lookup_room_equipment', 'check_sample_room_item', 'room_equipment_available', 'find_room_equipment_status', 'has_sample_room_equipment', 'get_room_item_status', 'check_facility_room_equipment', 'report_room_equipment_presence'),
    descriptions=('Check whether a sample room has a specified item of equipment.', 'Look up equipment availability in the sample facilities directory.', 'Report whether the named sample room contains the specified equipment.', 'Check an equipment item against the sample room directory.', 'Find whether a sample room has the requested equipment item.', 'Return the presence or absence of an item in a sample room.', 'Look up whether a named sample room has a particular equipment item.', 'Determine from the sample directory if the room has the specified equipment.', 'Get the sample equipment status for a room and item.', 'Report the sample directory’s room and equipment match.'),
    parameters=(Parameter(names=("room", "room_name")), Parameter(names=("equipment", "equipment_item"))),
    tasks=(Task(id="equipment", prompts=("Does the sample {room} room have {equipment}?", "Check the sample directory for {equipment} in room {room}.", 'Check whether {equipment} is present in the sample room {room}.', 'In the sample directory, does room {room} contain {equipment}?', 'Look up {room} in the sample rooms and determine whether it has {equipment}.', 'Is {equipment} available in sample room {room}?', 'Report whether sample room {room} has the equipment item {equipment}.', 'For sample room {room}, check the presence of {equipment}.', 'Does the sample equipment list for room {room} include {equipment}?', 'Find out from the sample directory whether {equipment} is in {room}.', 'Determine whether the sample {room} room contains {equipment}.', 'Check the sample facilities directory: is {equipment} in room {room}?'), answers=("{result}", "Sample equipment result: {result}"), cases=cases),),
)


def resolve(room, equipment):
    status = "has" if equipment in EQUIPMENT[room] else "does not have"
    return f"Room {room} {status} {equipment}."
