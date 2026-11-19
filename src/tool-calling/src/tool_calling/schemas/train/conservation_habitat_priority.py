from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        habitats = rng.sample(("H101", "H102", "H103", "H104", "H105"), 3)
        scores = rng.sample(range(1, 100), 3)
        rows = list(zip(habitats, scores))
        yield {"rows": rows, "habitats": "; ".join(f"{name}: {score}" for name, score in rows)}


def prepare(*, task_id, case):
    habitat = max(case["rows"], key=lambda row: row[1])[0]
    return Decision(fields=case, arguments={"habitat": habitat})


def resolve(habitat):
    return f"Selected habitat: {habitat}"


SCHEMA = Schema(
    id="conservation_habitat_priority",
    tool_names=("select_priority_habitat", "record_habitat_priority", "record_selected_habitat", "mark_habitat_for_priority", "submit_priority_habitat", "register_habitat_selection", "select_habitat_by_id", "save_priority_habitat", "mark_selected_habitat", "record_priority_action_habitat"),
    descriptions=("Record the selected habitat ID.", "Select a habitat for priority action.", "Record the supplied habitat identifier as selected.", "Mark the identified habitat for priority action.", "Submit one selected habitat ID for priority action.", "Return confirmation of the selected habitat identifier.", "Register the specified habitat as the priority selection.", "Record a priority habitat using its supplied ID.", "Identify the selected habitat in the priority workflow.", "Select the provided habitat ID for priority action."),
    parameters=(Parameter(names=("habitat", "habitat_id")),),
    tasks=(Task(id="priority", prompts=('Select the habitat with the highest priority score: {habitats}.', 'Choose the highest-scoring habitat for priority action: {habitats}.', 'From the scores {habitats}, select the highest-scoring habitat for priority action.', 'Priority action should go to the habitat with the maximum score. Select it from {habitats}.', 'Given habitat scores {habitats}, mark the habitat with the greatest score for priority action.', 'Which habitat in {habitats} has the top priority score? Select it for priority action.', 'Review {habitats} and record the highest-scoring habitat as the selection for priority action.', 'For priority action, choose the habitat whose score is largest among these entries: {habitats}.', 'The score list is {habitats}. Select the habitat at the maximum score for priority action.', 'Compare the habitat priority scores in {habitats}, then select the leader for priority action.', 'Assign priority action to the habitat with the highest score from {habitats}; record that selection.', 'Using {habitats}, select for priority action the habitat that outranks all others by score.'), answers=('{result}.', '{result}.'), cases=cases),),
)
