from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"first": str(rng.randint(2, 45)), "second": str(rng.randint(2, 45)), "third": str(rng.randint(2, 45)), "break1": str(rng.randint(1, 8)), "break2": str(rng.randint(1, 8))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(first, second, third, break1, break2):
    return str(sum(map(int, (first, second, third, break1, break2))))


SCHEMA = Schema(
    id="media_runtime_total",
    tool_names=("calculate_total_runtime", "sum_program_runtime", "compute_full_runtime", "calculate_program_duration", "sum_segments_and_breaks", "compute_total_program_minutes", "calculate_combined_runtime", "add_program_durations", "determine_total_airtime", "sum_segment_break_minutes"),
    descriptions=("Add three segment durations and two breaks in minutes.", "Calculate combined segment and break runtime in minutes.", "Sum the minutes for three segments and both breaks.", "Determine the full program runtime including two breaks.", "Compute total minutes from the three segments and two interposed breaks.", "Add all segment and break durations to obtain the overall runtime.", "Calculate the combined duration of three segments plus two breaks.", "Find the full runtime in minutes including every segment and break.", "Sum three program segments and two break durations.", "Return the total program duration including both breaks in minutes."),
    parameters=(Parameter(names=("first", "first_minutes")), Parameter(names=("second", "second_minutes")), Parameter(names=("third", "third_minutes")), Parameter(names=("break1", "first_break_minutes")), Parameter(names=("break2", "second_break_minutes"))),
    tasks=(Task(id="runtime", prompts=("Three segments run {first}, {second}, and {third} minutes, with breaks of {break1} and {break2} minutes. What is the total runtime including both breaks?", "Add segment durations {first}, {second}, and {third} minutes and breaks of {break1} and {break2} minutes. What is the full runtime?", "What's the total airtime for segments of {first}, {second}, and {third} minutes plus breaks of {break1} and {break2} minutes?", "A program has three segments lasting {first}, {second}, and {third} minutes and two breaks lasting {break1} and {break2} minutes. How long is it altogether?", "Find the combined runtime in minutes: segments {first}, {second}, {third}; breaks {break1}, {break2}.", "How many minutes should we schedule for three segments of {first}, {second}, and {third} minutes and breaks of {break1} and {break2} minutes?", "Please sum the {first}-, {second}-, and {third}-minute segments and the {break1}- and {break2}-minute breaks.", "Include both breaks when calculating the runtime: segments {first}, {second}, {third} minutes; breaks {break1}, {break2} minutes.", "What is the overall duration of a show with {first}, {second}, and {third} minutes of segments and {break1} and {break2} minutes of breaks?", "Work out the full program length in minutes from segment times {first}, {second}, {third} and break times {break1}, {break2}.", "The segments last {first}, {second}, and {third} minutes. Two breaks add {break1} and {break2} minutes. What's the total?", "Add up the entire broadcast: {first}, {second}, and {third} minutes for the segments, plus {break1} and {break2} minutes for breaks."), answers=("{result} minutes.", "Total runtime: {result} minutes."), cases=cases),),
)
