from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        start = rng.randrange(8 * 60, 19 * 60, 15)
        yield {"start": f"{start // 60:02d}:{start % 60:02d}", "first": rng.choice((15, 30, 45, 60)), "second": rng.choice((15, 30, 45, 60)), "third": rng.choice((15, 30, 45, 60))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(start, first, second, third):
    hour, minute = map(int, start.split(":"))
    end = hour * 60 + minute + int(first) + int(second) + int(third)
    return f"{end // 60:02d}:{end % 60:02d}"


SCHEMA = Schema(
    id="events_run_of_show",
    tool_names=("calculate_performance_end", "run_of_show_end_time", "compute_show_finish_time", "add_performance_segments", "find_show_end_time", "calculate_segmented_event_end", "determine_performance_finish", "sum_run_of_show_durations", "compute_consecutive_segment_end", "find_performance_end_time"),
    descriptions=("Add consecutive segment durations to a performance start time.", "Calculate a performance end time from its run of show.", "Add three consecutive minute durations with no gaps to the start time.", "Determine the finish time of three back-to-back performance segments.", "Compute the show end from a start time and three segment lengths.", "Find the 24-hour end time after three consecutive segments.", "Calculate when a performance ends by adding its three durations.", "Determine the end of a gapless three-segment run of show.", "Add the three segment lengths to the performance start.", "Compute the finish time for the supplied consecutive segments."),
    parameters=(Parameter(names=("start", "start_time")), Parameter(names=("first", "first_minutes")), Parameter(names=("second", "second_minutes")), Parameter(names=("third", "third_minutes"))),
    tasks=(Task(id="end", prompts=("A performance starts at {start}. Its three consecutive segments last {first}, {second}, and {third} minutes, with no gaps. Give the end time in 24-hour HH:MM format.", "Starting at {start}, a performance has consecutive segments of {first}, {second}, and {third} minutes with no gaps. When does it end? Use 24-hour HH:MM.", "The show begins at {start} and runs for {first}, {second}, and {third} minutes in consecutive segments without gaps. Give its end in 24-hour HH:MM.", "Calculate the 24-hour HH:MM end time for a {start} start and three back-to-back segments of {first}, {second}, and {third} minutes.", "A performance starts at {start}; its consecutive gapless segments last {first}, {second}, and {third} minutes. When does it finish in 24-hour HH:MM?", "Add three consecutive segments of {first}, {second}, and {third} minutes to the {start} start, with no gaps. Report the end in 24-hour HH:MM.", "What is the 24-hour HH:MM finish time if the performance starts at {start} and has gapless segments of {first}, {second}, and {third} minutes?", "Run of show: start {start}, then {first}, {second}, and {third} minutes back-to-back. Give the finish time in 24-hour HH:MM.", "Starting at {start}, three segments take {first}, {second}, and {third} minutes consecutively without gaps. Calculate the 24-hour HH:MM end time.", "Find the performance end in 24-hour HH:MM: start {start}, segment lengths {first}, {second}, and {third} minutes, no gaps.", "The show starts at {start} and has three consecutive segments lasting {first}, {second}, and {third} minutes. With no gaps, when does it end in 24-hour HH:MM?", "For a {start} start followed by uninterrupted segments of {first}, {second}, and {third} minutes, report the finish in 24-hour HH:MM."), answers=("Ends at {result}.", "{result}."), cases=cases),),
)
