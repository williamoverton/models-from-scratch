from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        size = rng.randint(50, 65)
        names = rng.sample(("A", "B", "C", "D", "E"), 3)
        ranges = [(size - rng.randint(0, 3), size + rng.randint(0, 3))]
        ranges += [(size - 10, size - 5), (size + 5, size + 10)]
        rng.shuffle(ranges)
        yield {"measurement": str(size), "equipment": "; ".join(f"{name}: {low}-{high} cm" for name, (low, high) in zip(names, ranges))}


def prepare(*, task_id, case):
    measurement = int(case["measurement"])
    for entry in case["equipment"].split("; "):
        name, bounds = entry.split(": ")
        low, high = map(int, bounds.removesuffix(" cm").split("-"))
        if low <= measurement <= high:
            return Decision(fields=case, arguments={"item": name})


def resolve(item):
    return f"Selected equipment: {item}."


SCHEMA = Schema(
    id="sports_equipment_fit",
    tool_names=("select_fitting_equipment", "record_equipment_choice", "report_equipment_choice", "submit_equipment_choice", "register_selected_equipment", "announce_selected_equipment", "declare_equipment_choice", "save_equipment_selection", "set_selected_equipment", "report_selected_item"),
    descriptions=("Record the selected equipment ID.", "Report the chosen equipment item.", "Submit the identifier of the selected equipment.", "Register the chosen equipment item.", "Announce the supplied equipment selection.", "Declare the selected item by its identifier.", "Save the identifier of the chosen item.", "Set the selected equipment to the supplied item.", "Report the selected equipment by name.", "Record which equipment item was chosen."),
    parameters=(Parameter(names=("item", "equipment_id")),),
    tasks=(Task(id="fit", prompts=("Head circumference is {measurement} cm. Helmet ranges: {equipment}. Select the helmet whose inclusive size range fits; exactly one fits.", "Which helmet fits a {measurement} cm head? The ranges are {equipment}; endpoints are inclusive and exactly one fits.", "Choose the one fitting helmet for a head circumference of {measurement} cm from {equipment}. Treat each range as inclusive; exactly one fits.", "A head measures {measurement} cm around. Helmet sizes: {equipment}. Select the sole fit, counting both range endpoints.", "From {equipment}, find the helmet whose inclusive range contains {measurement} cm. Exactly one fits this head circumference.", "Helmet ranges are {equipment}, and the head circumference is {measurement} cm. Which single helmet fits, including endpoints?", "Select the unique helmet fitting a {measurement} cm head using these inclusive ranges: {equipment}.", "The circumference is {measurement} cm; available helmet ranges are {equipment}. Exactly one fits when bounds are inclusive. Identify it.", "Determine which helmet fits: head {measurement} cm, ranges {equipment}. Include both endpoints; there is exactly one match.", "For a {measurement} cm head, pick the only fitting helmet among {equipment}, with range boundaries included.", "Use inclusive size ranges {equipment} to select the one helmet that fits a head circumference of {measurement} cm; exactly one fits."), answers=("{result}",), cases=cases),),
)
