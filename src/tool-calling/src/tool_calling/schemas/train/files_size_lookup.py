from ...schema_types import Decision, Parameter, Schema, Task


SIZES = {"report.csv": 128, "image.png": 640, "notes.txt": 12, "archive.zip": 2048}


def cases(rng, count):
    for _ in range(count):
        yield {"file": rng.choice(tuple(SIZES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(file):
    return f"{file}: {SIZES[file]} KiB"


SCHEMA = Schema(
    id="files_size_lookup",
    tool_names=("get_file_size", "lookup_sample_file_size", "find_sample_file_size", "retrieve_sample_file_size", "get_sample_size_in_kib", "lookup_file_size_in_kib", "read_sample_file_size", "get_registered_file_size", "find_registered_file_size", "retrieve_file_size_in_kib"),
    descriptions=("Look up a sample file's size.", "Retrieve a sample file size in KiB.", "Find the size in KiB of a named file in the sample registry.", "Return the registered sample size for a file.", "Look up a file name in the sample size table.", "Get the sample file's size in kibibytes.", "Retrieve the KiB size associated with a sample file name.", "Read the size of a file from the sample registry.", "Find a named sample file's registered size in KiB.", "Return the sample registry's file size in KiB."),
    parameters=(Parameter(names=("file", "file_name")),),
    tasks=(Task(id="size", prompts=("What is the size of {file} in the sample file registry?", "Look up the sample size of {file}.", "Find the registered sample size of {file}.", "How large is {file} according to the sample file registry?", "Retrieve the size of {file} from the sample registry.", "What's the sample registry's size entry for {file}?", "Check the sample file size listed for {file}.", "Give me the sample size recorded for {file}.", "Read the size of {file} in the sample file table.", "In the sample registry, what size is assigned to {file}?", "Find the sample file registry entry for the size of {file}.", "Report the registered sample size for file {file}."), answers=("{result}.", "{result}."), cases=cases),),
)
