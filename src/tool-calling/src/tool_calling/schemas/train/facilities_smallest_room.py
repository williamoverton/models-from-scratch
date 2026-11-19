from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("Ash", "Birch", "Cedar", "Elm", "Fir", "Hazel"), 3)
        if rng.choice((True, False)):
            smallest_fit = rng.randint(6, 90)
            attendance = rng.choice((smallest_fit, rng.randint(2, smallest_fit - 1)))
            other = rng.choice((rng.randint(1, attendance - 1), rng.randint(smallest_fit + 1, 100)))
            capacities = [smallest_fit, smallest_fit, other]
        else:
            capacities = sorted(rng.sample(range(5, 101), 3))
            attendance = rng.choice((rng.choice(capacities), rng.randint(1, capacities[-1])))
        rooms = list(zip(names, capacities))
        rng.shuffle(rooms)
        yield {"attendance": str(attendance), "rooms": ", ".join(f"{name}={capacity}" for name, capacity in rooms)}


def prepare(*, task_id, case):
    parsed = (entry.strip().split("=") for entry in case["rooms"].split(","))
    fitting = ((int(capacity), name) for name, capacity in parsed if int(capacity) >= int(case["attendance"]))
    _, room = min(fitting)
    return Decision(fields=case, arguments={"room": room})


SCHEMA = Schema(
    id="facilities_smallest_room",
    tool_names=("report_selected_room", "identify_fitting_room", "return_selected_room", "record_fitting_room", "name_selected_room", "report_room_choice", "identify_room_choice", "return_fitting_room", "record_selected_room_name", "get_selected_room_name"),
    descriptions=("Report the selected room name without reserving it.", "Return the name of a selected room.", "Return the chosen room's name without making a reservation.", "Report the room selected to fit the attendees.", "Provide the specified selected room name.", "Identify the chosen room without booking it.", "Return the room name selected for the group.", "Report a fitting room by name without reserving it.", "Record the name of the selected fitting room.", "Give the name of the chosen room."),
    parameters=(Parameter(names=("room", "room_name")),),
    tasks=(Task(id="fit", prompts=("Room capacities are {rooms}. Select the smallest room that fits {attendance} people. Equal capacity is sufficient; break capacity ties alphabetically by room name.", "For {attendance} attendees, choose the lowest-capacity room from {rooms} that can hold everyone, including an exact fit. Break ties alphabetically by room name.", "Choose the smallest adequate room for {attendance} people from {rooms}; exact fits count, and ties go to the alphabetically first room name.", "Given {rooms}, select the lowest-capacity room holding at least {attendance} people. If capacities tie, choose the alphabetically first name.", "Which room in {rooms} has the smallest capacity sufficient for {attendance} attendees? Accept equality and resolve ties alphabetically by room name.", "Find a room for {attendance} people among {rooms}, minimizing capacity. A capacity equal to attendance is enough; use alphabetical room names to break ties.", "From {rooms}, pick the smallest room that accommodates {attendance} people, allowing an exact fit and breaking capacity ties by room name alphabetically.", "Room options: {rooms}. For {attendance} attendees, report the minimum fitting capacity's room; equal capacity fits and alphabetical name wins a tie.", "Select a room from {rooms} for {attendance} people with the least sufficient capacity. Include exact fits and sort tied room names alphabetically.", "For a group of {attendance}, identify the smallest fitting room listed in {rooms}. A room exactly that size qualifies; break capacity ties alphabetically by name.", "Use {rooms} to choose the lowest-capacity room for {attendance} attendees. Capacity may equal attendance; if tied, choose the first room alphabetically.", "Among {rooms}, which room should host {attendance} people if we want the smallest sufficient capacity? Exact fits qualify, with alphabetical room-name tie-breaking."), answers=("The selected room is {result}.", "Choose room {result}."), cases=cases),),
)


def resolve(room):
    return room
