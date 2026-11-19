from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(('A', 'B', 'C', 'D', 'E', 'F'), 3)
        durations = rng.sample(range(15, 121, 5), 3)
        entries = list(zip(names, durations))
        rng.shuffle(entries)
        yield {'slots': '; '.join(f'{name}={duration} minutes' for name, duration in entries)}


def prepare(*, task_id, case):
    entries = [entry.split('=') for entry in case['slots'].split('; ')]
    name, _ = max(entries, key=lambda entry: int(entry[1].split()[0]))
    return Decision(fields=case, arguments={'slot': name})


def resolve(slot):
    return f'Selected slot: {slot}'


SCHEMA = Schema(
    id='schedule_longest_free_slot',
    tool_names=('select_longest_free_slot', 'choose_free_slot', 'record_free_slot_choice', 'acknowledge_free_slot', 'report_selected_free_slot', 'confirm_free_slot_selection', 'register_free_slot_choice', 'submit_selected_free_slot', 'identify_chosen_free_slot', 'set_selected_free_slot'),
    descriptions=('Acknowledge a selected free slot ID.', 'Record a free slot selection.', 'Return the supplied free slot identifier as selected.', 'Acknowledge the chosen free slot by ID.', 'Report the specified free slot as the selection.', 'Record the provided free slot identifier.', 'Confirm the supplied slot ID as the chosen free slot.', 'Identify the free slot selected by its given ID.', 'Return an acknowledgement of a free slot choice.', 'Register the selected free slot identifier.'),
    parameters=(Parameter(names=('slot', 'slot_id')),),
    tasks=(Task(id='longest', prompts=('Free slots and durations: {slots}. Select the longest free slot.', 'Choose the free slot with the greatest duration: {slots}.', 'Select the free slot ID with the most minutes in {slots}.', 'Which available slot lasts longest? {slots}. Select it.', 'From {slots}, choose the maximum-duration free slot.', 'Pick the free slot with the largest duration: {slots}.', 'Identify and select the longest opening among {slots}.', 'Use {slots} to select the slot with the greatest length.', 'Select the free slot that offers the most time: {slots}.', 'Compare the free slot durations in {slots} and choose the longest.', 'Which slot in {slots} has the highest duration? Select it.', 'Please choose the longest free slot from {slots}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
