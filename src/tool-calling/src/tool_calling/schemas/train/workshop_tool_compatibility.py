from ...schema_types import Decision, Parameter, Schema, Task


TOOLS = {"T1": 6, "T2": 8, "T3": 10, "T4": 12, "T5": 6, "T6": 8}


def cases(rng, count):
    for _ in range(count):
        tool = rng.choice(tuple(TOOLS))
        size = rng.choice((TOOLS[tool], rng.choice(tuple(n for n in (6, 8, 10, 12) if n != TOOLS[tool]))))
        yield {"tool": tool, "size": str(size)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(tool, size):
    return "compatible" if TOOLS[tool] == int(size) else "not compatible"


SCHEMA = Schema(
    id="workshop_tool_compatibility",
    tool_names=('check_tool_attachment', 'check_attachment_compatibility', 'compare_tool_fitting', 'check_tool_fit', 'verify_attachment_size', 'assess_tool_attachment', 'match_attachment_size', 'determine_tool_compatibility', 'check_sample_tool_fit', 'compare_fitting_size'),
    descriptions=('Check exact attachment-size equality with a tool fitting in the sample registry.', 'Look up the sample tool fitting size and compare the attachment.', 'Determine whether the attachment exactly matches the sample tool fitting.', 'Compare an attachment size with the tool’s recorded sample fitting size.', 'Check compatibility by exact size match in the sample registry.', 'Verify the given attachment size against a sample tool fitting.', 'Report whether a sample tool and attachment have equal fitting sizes.', 'Check a tool’s sample fitting size against an attachment size in millimetres.', 'Look up a sample tool and test exact attachment-size equality.', 'Determine attachment compatibility using the sample tool registry.'),
    parameters=(Parameter(names=("tool", "tool_id")), Parameter(names=("size", "attachment_size_mm"))),
    tasks=(Task(id="compatibility", prompts=("Does a {size} mm attachment fit tool {tool} in the sample registry? The sizes must match exactly.", "Check whether tool {tool} accepts a {size} mm attachment using its recorded fitting size; an exact match is required.", 'Compare tool {tool} with a {size} mm attachment in the sample registry; compatibility requires exact size equality.', 'Using the sample fitting size for {tool}, determine whether a {size} mm attachment matches exactly.', 'Is a {size} mm attachment compatible with sample tool {tool}? Its fitting size must be identical.', 'Check the sample registry fitting for tool {tool} against {size} mm; only an exact match fits.', 'Does tool {tool} accept an attachment measuring {size} mm? Use the sample registry and exact equality.', 'For sample tool {tool}, compare its recorded fitting size to {size} mm and report exact-match compatibility.', 'Determine if the {size} mm attachment fits {tool} in the sample registry, requiring equal sizes.', 'Look up sample tool {tool} and check whether its fitting exactly matches {size} mm.', 'Assess compatibility of tool {tool} and a {size} mm attachment using exact fitting-size equality in the sample registry.', 'Would a {size} mm attachment fit sample tool {tool}? Compare sizes exactly.'), answers=("The attachment is {result}.", "Result: {result}."), cases=cases),),
)
