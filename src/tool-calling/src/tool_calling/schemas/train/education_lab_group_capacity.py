from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("A", "B", "C", "D", "E"), 3)
        capacities = rng.sample(range(8, 25), 3)
        size = rng.randint(8, max(capacities))
        groups = "; ".join(f"{name}: {capacity}" for name, capacity in zip(names, capacities))
        yield {"groups": groups, "size": str(size)}


def prepare(*, task_id, case):
    groups = [(name, int(capacity)) for name, capacity in (entry.split(": ") for entry in case["groups"].split("; "))]
    name, _ = min((item for item in groups if item[1] >= int(case["size"])), key=lambda item: (item[1], item[0]))
    return Decision(fields=case, arguments={"group": name})


def resolve(group):
    return f"Selected group: {group}."


SCHEMA = Schema(
    id="education_lab_group_capacity",
    tool_names=('select_lab_group', 'record_lab_group', 'report_lab_group', 'record_selected_group', 'report_selected_lab_group', 'register_lab_group_selection', 'identify_lab_group', 'return_lab_group_selection', 'report_group_id', 'record_group_selection'),
    descriptions=('Record the selected lab group ID.', 'Report the selected lab group.', 'Report the supplied selected lab group ID.', 'Record the specified lab group selection.', 'Report the selected lab group identifier.', 'Register the supplied lab group selection.', 'Identify the given selected lab group.', 'Return the supplied lab group selection.', 'Report the selected lab group by ID.', 'Record the supplied selected group ID.'),
    parameters=(Parameter(names=("group", "group_id")),),
    tasks=(Task(id="select", prompts=("Lab group available seats: {groups}. Place {size} students together in the group with the fewest seats that fits; break ties by group ID alphabetically. Select the group.", "Choose a lab group for {size} students from {groups}. Use the smallest available seat count that fits everyone, breaking ties alphabetically by group ID.", "Available lab seats are {groups}. Fit all {size} students into one group with the fewest sufficient seats; resolve ties alphabetically by ID.", "Which group should take {size} students together? Capacities available: {groups}. Pick the smallest fitting group, then the alphabetically first ID if tied.", "Assign {size} students to one of these lab groups: {groups}. Select the fewest available seats that accommodate them, with alphabetical group ID tie-breaking.", "From {groups}, select the group with the smallest available capacity at least {size}; if tied, choose the alphabetically first group ID. Keep the students together.", "Lab groups have available seats {groups}. Place the {size} students together in the tightest fit, breaking ties alphabetically by group ID.", "Find a single group for {size} students among {groups}; minimize sufficient available seats and break equal-capacity ties by alphabetical group ID.", "For {size} students, choose from {groups} the group with fewest available seats that fits them all. Use alphabetical ID order for ties.", "Select a lab group from {groups} for all {size} students: use the lowest adequate seat count, then alphabetical group ID for a tie.", "The lab needs one group for {size} students. Available seats: {groups}. Pick the smallest fitting capacity and break ties alphabetically by group ID."), answers=("{result}",), cases=cases),),
)
