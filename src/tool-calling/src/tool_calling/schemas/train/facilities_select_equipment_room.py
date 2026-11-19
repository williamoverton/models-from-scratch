from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    equipment = ("projector", "whiteboard", "video conference", "speakerphone", "display")
    for _ in range(count):
        requested = rng.choice(equipment)
        names = rng.sample(("Ash", "Birch", "Cedar", "Elm", "Fir", "Maple"), 3)
        match = rng.randrange(3)
        rooms = []
        for index, name in enumerate(names):
            items = rng.sample([item for item in equipment if item != requested], 2)
            if index == match:
                items.append(requested)
            rng.shuffle(items)
            rooms.append(f"{name}: {' + '.join(items)}")
        yield {"requested": requested, "rooms": "; ".join(rooms)}


def prepare(*, task_id, case):
    room = next(entry.split(": ")[0] for entry in case["rooms"].split("; ") if case["requested"] in entry.split(": ")[1].split(" + "))
    return Decision(fields=case, arguments={"room": room})


def resolve(room):
    return f"Selected room: {room}."


SCHEMA = Schema(
    id="facilities_select_equipment_room",
    tool_names=("select_equipped_room", "report_equipment_room", "record_selected_room", "identify_equipment_room", "report_selected_equipment_room", "mark_equipped_room", "register_selected_room", "return_equipment_room", "record_equipment_room", "name_selected_room"),
    descriptions=("Record the name of the selected room.", "Report a selected room by name.", "Return the name of the room selected for its equipment.", "Record the supplied room as the equipment-room selection.", "Identify the selected room by its name.", "Report the named room as the selection.", "Register the room chosen for its equipment.", "Mark the specified room as selected.", "Return the selected equipment room's name.", "Record which room was selected."),
    parameters=(Parameter(names=("room", "room_name")),),
    tasks=(Task(id="select", prompts=("Room equipment: {rooms}. Select the room with a {requested}.", "Choose the room containing {requested} from these inventories: {rooms}.", "Which room in {rooms} has {requested}?", "Select the room equipped with {requested}: {rooms}.", "Find the room offering {requested} among these inventories: {rooms}.", "Given {rooms}, identify the room that contains {requested}.", "We need {requested}; choose the matching room from {rooms}.", "From the room equipment list {rooms}, report the room with {requested}.", "Pick the room that has {requested}. Equipment by room: {rooms}.", "Identify the {requested}-equipped room using {rooms}.", "Which of these rooms includes {requested} in its equipment: {rooms}?", "Use the inventories {rooms} to select the room with {requested}."), answers=("{result}", "{result}"), cases=cases),),
)
