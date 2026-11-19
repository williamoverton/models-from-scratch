from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("Aspen", "Birch", "Cedar", "Dune", "Elm"), 3)
        limit = rng.randint(3, 8)
        lengths = [rng.randint(1, limit), rng.randint(limit + 1, limit + 4), rng.randint(1, limit)]
        accessible = ["yes", "yes", "no"]
        trails = list(zip(names, lengths, accessible))
        rng.shuffle(trails)
        yield {"limit": str(limit), "trails": "; ".join(f"{name}: {distance} km, wheelchair accessible {access}" for name, distance, access in trails)}


def prepare(*, task_id, case):
    for entry in case["trails"].split("; "):
        name, details = entry.split(": ")
        distance, access = details.split(", ")
        if int(distance.split()[0]) <= int(case["limit"]) and access == "wheelchair accessible yes":
            return Decision(fields=case, arguments={"trail": name})


def resolve(trail):
    return f"Selected trail: {trail}."


SCHEMA = Schema(
    id="recreation_trail_access",
    tool_names=("select_accessible_trail", "record_trail_selection", "report_selected_trail", "identify_chosen_trail", "submit_trail_choice", "mark_selected_trail", "register_trail_selection", "note_chosen_trail", "return_trail_choice", "capture_selected_trail"),
    descriptions=("Record the selected trail name.", "Report the chosen trail.", "Submit the name of the selected trail.", "Identify the trail chosen by name.", "Register a trail selection by name.", "Return the selected trail's name.", "Note which trail was selected.", "Capture the name of the chosen trail.", "Mark a named trail as selected.", "Provide the chosen trail identifier."),
    parameters=(Parameter(names=("trail", "trail_id")),),
    tasks=(Task(id="select", prompts=("Trail details: {trails}. Select the trail that is wheelchair accessible and no longer than {limit} km; exactly one meets both requirements.", 'From {trails}, select the only wheelchair-accessible trail at most {limit} km long.', 'Choose the sole trail in {trails} that is wheelchair accessible and within {limit} km.', 'Which trail meets both wheelchair accessibility and a maximum length of {limit} km? {trails}. Select it.', 'Select the unique wheelchair-accessible route no longer than {limit} km: {trails}.', 'Given {trails}, pick the one accessible by wheelchair whose distance does not exceed {limit} km.', 'Among {trails}, select the only wheelchair-accessible trail with length <= {limit} km.', 'Trail options: {trails}. Record the sole wheelchair-accessible choice within {limit} km.', 'Find and select the one trail that is wheelchair accessible and up to {limit} km: {trails}.', 'Use {trails} to select the unique trail satisfying wheelchair accessibility and the {limit} km maximum.', 'Pick the only qualifying trail: wheelchair accessible, no more than {limit} km. Details: {trails}.'), answers=("{result}",), cases=cases),),
)
