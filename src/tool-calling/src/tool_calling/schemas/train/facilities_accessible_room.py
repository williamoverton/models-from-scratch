from ...schema_types import Decision, Schema, Parameter, Task


FEATURES = ("step-free access", "hearing loop", "adjustable table", "accessible restroom")


def cases(rng, count):
    for _ in range(count):
        required = rng.sample(FEATURES, 2)
        names = rng.sample(("Ash", "Birch", "Cedar", "Elm", "Fir", "Hazel"), 3)
        other_features = [feature for feature in FEATURES if feature not in required]
        winner = required + rng.sample(other_features, rng.randrange(len(other_features) + 1))
        rooms = [(names[0], winner)]
        for name in names[1:]:
            missing = rng.choice(required)
            available = [feature for feature in FEATURES if feature != missing]
            rooms.append((name, rng.sample(available, rng.randint(1, len(available)))))
        rng.shuffle(rooms)
        yield {
            "requirements": ", ".join(required),
            "rooms": "; ".join(f"{name}: {' | '.join(features)}" for name, features in rooms),
        }


def prepare(*, task_id, case):
    required = {feature.strip() for feature in case["requirements"].split(",")}
    matches = []
    for room in case["rooms"].split(";"):
        name, features = room.strip().split(":", 1)
        if required <= {feature.strip() for feature in features.split("|")}:
            matches.append(name)
    return Decision(fields=case, arguments={"room": matches[0]})


SCHEMA = Schema(
    id="facilities_accessible_room",
    tool_names=('report_accessible_room', 'report_selected_accessible_room', 'return_accessible_room_choice', 'acknowledge_room_selection', 'show_selected_room', 'report_accessible_room_choice', 'echo_selected_room', 'confirm_room_selection', 'return_room_name', 'report_accessibility_selection'),
    descriptions=('Report the selected room name without reserving it.', 'Return the name of a selected room.', 'Echo the supplied room name without making a reservation.', 'Acknowledge the provided room as the selection without reserving it.', 'Show the selected room name without booking a room.', 'Return the supplied room name for an accessibility selection.', 'Present the given room name as the selection without reserving it.', 'Output the selected room name without changing room bookings.', 'Confirm the provided room name without making a reservation.', 'Report the supplied room name as the selected room, without a reservation.'),
    parameters=(Parameter(names=("room", "room_name")),),
    tasks=(Task(id="accessibility", prompts=("Rooms and their features are {rooms}. Select the unique room with all of these features: {requirements}.", "Choose the one room in {rooms} that meets both accessibility requirements: {requirements}.", 'From {rooms}, select the unique room containing every required feature: {requirements}.', 'Which room in {rooms} has all the accessibility features {requirements}? Select it.', 'Choose the sole room satisfying all of {requirements} from these features: {rooms}.', 'Required features: {requirements}. Select the matching room from {rooms}.', 'Review {rooms} and choose the one room with both required features, {requirements}.', 'Find the uniquely qualifying room in {rooms} for accessibility requirements {requirements}.', 'Using {rooms}, select the room whose features include every item in {requirements}.', 'The accessibility requirements are {requirements}; which one room meets them in {rooms}?', 'Pick the only room with all of {requirements}, given these room features: {rooms}.', 'Identify and select the unique room meeting {requirements} from {rooms}.'), answers=("The selected room is {result}.", "Choose room {result}."), cases=cases),),
)


def resolve(room):
    return room
