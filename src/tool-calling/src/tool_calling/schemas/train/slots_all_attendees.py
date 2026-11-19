from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        slots = rng.sample(('A', 'B', 'C', 'D', 'E', 'F'), 3)
        attendees = rng.sample(('Ari', 'Bo', 'Chen', 'Dev', 'Emi', 'Fran'), 3)
        common = rng.choice(slots)
        others = [slot for slot in slots if slot != common]
        availability = [(attendees[0], [common, others[0]]), (attendees[1], [common, others[1]]), (attendees[2], [common, rng.choice(others)])]
        rng.shuffle(availability)
        for _, available in availability:
            rng.shuffle(available)
        yield {'availability': '; '.join(f'{name}: {", ".join(available)}' for name, available in availability)}


def prepare(*, task_id, case):
    sets = [set(entry.split(': ')[1].split(', ')) for entry in case['availability'].split('; ')]
    slot, = set.intersection(*sets)
    return Decision(fields=case, arguments={'slot': slot})


def resolve(slot):
    return f'Selected slot: {slot}'


SCHEMA = Schema(
    id='schedule_all_attendees_available',
    tool_names=('select_common_slot', 'choose_meeting_slot', 'record_selected_slot', 'acknowledge_slot_selection', 'submit_meeting_slot', 'confirm_selected_slot', 'register_slot_choice', 'report_chosen_slot', 'set_meeting_slot', 'acknowledge_meeting_slot'),
    descriptions=('Acknowledge the selected slot ID.', 'Record a meeting slot selection.', 'Return the supplied meeting slot as the selected slot.', 'Acknowledge a chosen slot by its ID.', 'Report the meeting slot ID supplied as the selection.', 'Record the specified slot ID as selected.', 'Confirm the provided slot identifier as the choice.', 'Return an acknowledgement of the chosen meeting slot.', 'Register the supplied slot identifier as the selection.', 'Identify the selected meeting slot by its provided ID.'),
    parameters=(Parameter(names=('slot', 'slot_id')),),
    tasks=(Task(id='common', prompts=('Each attendee lists their available slot IDs: {availability}. Select the slot available to everyone.', 'Choose the slot common to every attendee in {availability}.', 'Find the shared slot ID in {availability} and select it.', 'Which slot is every person available for? {availability}. Select it.', 'From the availability lists {availability}, select their intersection.', 'Pick the slot that all attendees can attend: {availability}.', 'Identify and select the universally available slot from {availability}.', 'Use {availability} to choose the slot appearing in every list.', 'Select the meeting slot shared by all attendees: {availability}.', 'Which slot ID is common across {availability}? Select it.', 'Compare the attendees in {availability} and select their common slot.', 'Please select the slot for which everyone is available: {availability}.'), answers=('{result}.', '{result}.'), cases=cases),),
)
