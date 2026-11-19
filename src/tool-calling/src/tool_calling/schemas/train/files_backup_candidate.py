from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"FILE-{n}" for n in range(100, 200)], 3)
        target_type = rng.choice(("csv", "pdf", "txt"))
        other_type = rng.choice([kind for kind in ("csv", "pdf", "txt") if kind != target_type])
        cutoff = rng.randint(10, 50)
        records = [(ids[0], target_type, cutoff + rng.randint(1, 20)), (ids[1], target_type, rng.randint(1, cutoff)), (ids[2], other_type, cutoff + rng.randint(1, 20))]
        rng.shuffle(records)
        yield {"files": "; ".join(f"{identifier} type={kind} age={age} days" for identifier, kind, age in records), "type": target_type, "cutoff": str(cutoff)}


def prepare(*, task_id, case):
    candidates = []
    for entry in case["files"].split("; "):
        identifier, kind, age, _ = entry.split()
        if kind[5:] == case["type"] and int(age[4:]) > int(case["cutoff"]):
            candidates.append(identifier)
    identifier, = candidates
    return Decision(fields=case, arguments={"file": identifier})


def resolve(file):
    return f"Marked for backup: {file}"


SCHEMA = Schema(
    id="files_backup_candidate",
    tool_names=("mark_file_for_backup", "select_backup_file", "flag_file_for_backup", "record_backup_candidate", "mark_backup_candidate", "report_file_for_backup", "identify_backup_file", "register_file_for_backup", "select_file_for_backup", "record_file_backup_selection"),
    descriptions=("Mark a file for simulated backup.", "Select a file ID for backup.", "Record the supplied file ID as a simulated backup candidate.", "Flag the specified file for simulated backup.", "Report which file is selected for backup.", "Mark a named file ID for backup without performing a backup.", "Identify the file selected for simulated backup.", "Register the specified file as a backup candidate.", "Return the file ID marked for backup.", "Record a file selection for simulated backup."),
    parameters=(Parameter(names=("file", "file_id")),),
    tasks=(Task(id="backup", prompts=("Files: {files}. Mark the {type} file older than {cutoff} days for backup; older means strictly more days.", "Select for backup the file in {files} with type {type} and age strictly greater than {cutoff} days.", "From {files}, mark the {type} file whose age exceeds {cutoff} days for backup.", "Which {type} file in {files} is more than {cutoff} days old? Select it for backup.", "Choose the backup candidate from {files} with type {type} and age over {cutoff} days, not equal to the cutoff.", "Find and mark the file in {files} for backup if its type is {type} and its age is strictly above {cutoff} days.", "Select the {type} file older than {cutoff} days from {files} for backup; an age equal to the cutoff does not qualify.", "File records: {files}. Mark for backup the {type} file aged strictly more than {cutoff} days.", "Using {files}, identify the file to back up with type {type} and an age exceeding {cutoff} days.", "Mark the backup candidate in {files}: its type must be {type} and its age must be greater than {cutoff} days.", "Among {files}, select for backup the {type} file with age above {cutoff} days, excluding equality.", "Pick the {type} file from {files} for backup when its age is strictly greater than {cutoff} days."), answers=("{result}.", "{result}."), cases=cases),),
)
