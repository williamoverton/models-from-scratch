from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"FILE-{n}" for n in range(100, 200)], 3)
        sizes = rng.sample(range(1, 1000), 3)
        yield {"files": "; ".join(f"{identifier}={size} KiB" for identifier, size in zip(ids, sizes))}


def prepare(*, task_id, case):
    files = [entry.split("=") for entry in case["files"].split("; ")]
    identifier, _ = max(files, key=lambda entry: int(entry[1].split()[0]))
    return Decision(fields=case, arguments={"file": identifier})


def resolve(file):
    return f"Selected file: {file}"


SCHEMA = Schema(
    id="files_largest",
    tool_names=("select_file", "mark_selected_file", "report_selected_file", "record_file_selection", "identify_selected_file", "mark_file_selection", "return_selected_file", "register_selected_file", "report_file_choice", "record_selected_file_id"),
    descriptions=("Select a file by ID.", "Mark the specified file.", "Report the supplied file ID as selected.", "Record the selected file identifier.", "Mark a file ID as the chosen file.", "Identify the specified file as selected.", "Return the ID of the selected file.", "Register the supplied file selection.", "Report which file was selected by ID.", "Record a file as the selected choice."),
    parameters=(Parameter(names=("file", "file_id")),),
    tasks=(Task(id="largest", prompts=("Files and sizes: {files}. Select the largest file.", "Select the file with the greatest size in {files}.", "Which file is largest among {files}? Select it.", "Choose the biggest file from {files}.", "From the file sizes {files}, select the largest file.", "Identify and select the file with the maximum size: {files}.", "Given {files}, mark the file that takes up the most space.", "Pick the largest file listed in {files}.", "Compare {files} and select the file with the highest size.", "Select the biggest file by size from this list: {files}.", "File sizes are {files}. Which file should be selected as the largest?", "Find the greatest file size in {files} and select its file."), answers=("{result}.", "{result}."), cases=cases),),
)
