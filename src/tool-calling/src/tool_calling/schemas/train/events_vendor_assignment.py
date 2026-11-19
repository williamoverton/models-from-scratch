from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        booths = rng.sample(("B101", "B102", "B103", "B104", "B105"), 3)
        required = rng.randint(3, 8)
        sizes = [rng.randint(1, required - 1), *rng.sample(range(required, required + 8), 2)]
        eligible = [rng.choice((True, False)), True, rng.choice((True, False))]
        options = list(zip(sizes, eligible))
        rng.shuffle(options)
        rows = [(booth, size, allowed) for booth, (size, allowed) in zip(booths, options)]
        details = "; ".join(f"{booth}: {size} sq m, {'eligible' if allowed else 'ineligible'}" for booth, size, allowed in rows)
        yield {"required": required, "rows": rows, "booths": details}


def prepare(*, task_id, case):
    booth = min((row for row in case["rows"] if row[2] and row[1] >= case["required"]), key=lambda row: row[1])[0]
    return Decision(fields=case, arguments={"booth": booth})


def resolve(booth):
    return f"Assigned booth: {booth}"


SCHEMA = Schema(
    id="events_vendor_assignment",
    tool_names=("assign_vendor_booth", "record_booth_assignment", "confirm_vendor_booth", "record_selected_booth", "assign_selected_booth", "acknowledge_booth_choice", "report_booth_assignment", "confirm_booth_identifier", "record_vendor_space", "mark_assigned_booth"),
    descriptions=("Record the booth assigned to the vendor.", "Assign the selected booth ID.", "Confirm the supplied booth assignment.", "Record the chosen booth identifier.", "Acknowledge the booth selected for the vendor.", "Assign the provided booth to the vendor.", "Report the booth that was assigned.", "Record the selected vendor booth.", "Confirm the named booth ID.", "Mark the supplied booth as assigned."),
    parameters=(Parameter(names=("booth", "booth_id")),),
    tasks=(Task(id="assign", prompts=("A vendor needs at least {required} sq m. Assign the smallest eligible booth that fits: {booths}.", "Select the eligible booth with the least space that is at least {required} sq m: {booths}.", "Assign a vendor needing {required} sq m to the smallest eligible booth that accommodates them: {booths}.", "Booth options: {booths}. Choose the smallest eligible one with at least {required} sq m for the vendor.", "Which eligible booth has the least space while fitting a vendor requiring {required} sq m? Assign it from {booths}.", "A vendor requires at least {required} sq m. From {booths}, assign the smallest booth that is eligible and large enough.", "Choose a booth for a {required} sq m minimum requirement: {booths}. It must be eligible and the smallest fitting one.", "Review {booths} and assign the smallest eligible booth of at least {required} sq m.", "Find the least spacious eligible booth that meets the vendor's {required} sq m minimum and assign it: {booths}.", "Assign the vendor to the smallest eligible booth that fits {required} sq m or more: {booths}.", "Given booth sizes and eligibility {booths}, select the smallest eligible space no smaller than {required} sq m.", "The vendor needs {required} sq m minimum. Assign the tightest-fitting eligible booth among {booths}."), answers=("{result}.", "{result}."), cases=cases),),
)
