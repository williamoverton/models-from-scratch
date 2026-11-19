from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample([f"FILE-{n}" for n in range(100, 200)], 3)
        checksums = rng.sample([f"{n:04x}" for n in range(256)], 2)
        records = [(ids[0], checksums[0]), (ids[1], checksums[0]), (ids[2], checksums[1])]
        rng.shuffle(records)
        yield {"files": "; ".join(f"{identifier}={checksum}" for identifier, checksum in records)}


def prepare(*, task_id, case):
    records = [entry.split("=") for entry in case["files"].split("; ")]
    duplicates = sorted(identifier for identifier, checksum in records if sum(other == checksum for _, other in records) == 2)
    return Decision(fields=case, arguments={"file_a": duplicates[0], "file_b": duplicates[1]})


def resolve(file_a, file_b):
    return f"Marked duplicates: {file_a}, {file_b}"


SCHEMA = Schema(
    id="files_checksum_duplicates",
    tool_names=("mark_duplicate_files", "flag_duplicate_pair", "record_duplicate_files", "mark_file_pair_duplicates", "report_duplicate_pair", "flag_file_duplicates", "identify_duplicate_file_pair", "register_duplicate_pair", "record_matching_files", "mark_files_as_duplicates"),
    descriptions=("Mark two file IDs as duplicates.", "Flag a specified pair of files.", "Record the two supplied file IDs as duplicates.", "Report the specified duplicate file pair.", "Mark a pair of file identifiers as duplicates.", "Flag two named files as a duplicate pair.", "Register the supplied pair of duplicate file IDs.", "Identify two specified file IDs as duplicates.", "Record a duplicate relationship between the two supplied files.", "Return the two file IDs marked as duplicates."),
    parameters=(Parameter(names=("file_a", "first_file_id")), Parameter(names=("file_b", "second_file_id"))),
    tasks=(Task(id="duplicates", prompts=("File IDs and checksums: {files}. Mark the pair with matching checksums as duplicates; pass the IDs in alphabetical order.", "Mark the two files with equal checksums in {files}; list their IDs alphabetically.", "From {files}, mark the matching-checksum pair as duplicates, passing their IDs alphabetically.", "Identify the two files sharing a checksum in {files} and mark them as duplicates, with IDs in alphabetical order.", "Which files in {files} have equal checksums? Mark them as duplicates and order their IDs alphabetically.", "Use {files} to find and flag the duplicate pair by checksum; supply the file IDs in alphabetical order.", "Mark as duplicates the files with the same checksum in {files}, listing their IDs alphabetically.", "Compare checksums in {files}; flag the matching pair and pass the IDs in alphabetical order.", "Given {files}, select the two IDs with identical checksums as duplicates, ordered alphabetically.", "Find the duplicate files in {files} by matching checksums, and mark them using alphabetical ID order.", "File checksum records: {files}. Mark the equal-checksum pair as duplicates, with the alphabetically first ID first.", "Flag the two matching-checksum files from {files} as duplicates; provide their IDs in alphabetical order."), answers=("{result}.", "{result}."), cases=cases),),
)
