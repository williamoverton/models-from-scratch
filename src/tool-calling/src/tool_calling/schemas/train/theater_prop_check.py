from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        required = rng.sample(("lantern", "letter", "crown", "sword", "book", "hat"), 3)
        missing = rng.choice(required)
        present = [prop for prop in required if prop != missing]
        rng.shuffle(present)
        yield {"missing": missing, "required": ", ".join(required), "present": ", ".join(present)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"prop": case["missing"]})


def resolve(prop):
    return f"Missing prop: {prop}"


SCHEMA = Schema(
    id="theater_prop_check",
    tool_names=('record_missing_prop', 'flag_missing_prop', 'report_missing_prop', 'show_missing_prop', 'identify_missing_prop', 'return_missing_prop', 'report_absent_prop', 'display_missing_prop', 'state_missing_prop', 'specify_missing_prop'),
    descriptions=('Report the specified missing prop.', 'Record the name of a missing prop.', 'Flag the given prop as missing.', 'Return the supplied missing prop name.', 'Show which prop is missing.', 'Identify a missing prop by name.', 'Report the provided missing prop.', 'Display the name of the absent prop.', 'State the missing prop.', 'Report a prop absent from the checklist.'),
    parameters=(Parameter(names=("prop", "prop_name")),),
    tasks=(Task(id="check", prompts=("Required props: {required}. Present props: {present}. Record the one missing prop.", "Which one required prop is missing? Required: {required}; present: {present}.", 'Compare required props {required} against those present, {present}; record the absent prop.', 'From the required list {required}, which prop is absent from {present}? Record it.', 'The checklist calls for {required}; we have {present}. Identify the missing prop.', 'Inventory {present} against requirements {required} and report the one missing prop.', 'A production needs {required}, but has {present}. Record the missing item.', 'Find the sole missing prop: required {required}; available {present}.', 'Given required props {required} and present props {present}, report the missing one.', 'Which prop must be flagged missing when {required} are required and {present} are present?', 'The required set is {required}; the present set is {present}. Identify the missing prop.', 'Record the prop not present in {present} from the required props {required}.'), answers=("{result}.", "{result}."), cases=cases),),
)
