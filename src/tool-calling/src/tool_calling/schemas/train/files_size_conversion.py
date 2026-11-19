from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"size": str(rng.randint(1, 100)), "source": rng.choice(("MiB", "GiB"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(size, source):
    return str(int(size) * {"MiB": 1024, "GiB": 1024 * 1024}[source])


SCHEMA = Schema(
    id="files_size_conversion",
    tool_names=("convert_size_to_kib", "size_in_kibibytes", "convert_binary_size_to_kib", "calculate_size_in_kib", "mib_or_gib_to_kib", "express_size_in_kib", "compute_kibibytes", "convert_to_kibibytes", "get_binary_size_in_kib", "calculate_kib_from_binary_unit"),
    descriptions=("Convert a binary file size to KiB.", "Express a MiB or GiB size in KiB.", "Convert an amount in MiB or GiB to kibibytes using factors of 1024.", "Calculate KiB from a size in MiB or GiB.", "Return the kibibyte equivalent of the supplied binary size.", "Multiply a MiB or GiB amount by the appropriate binary factor to obtain KiB.", "Express a file size given in MiB or GiB as KiB.", "Compute the number of KiB in a binary size.", "Translate the supplied MiB or GiB amount into kibibytes.", "Convert the input size and source unit to KiB using binary units."),
    parameters=(Parameter(names=("size", "amount")), Parameter(names=("source", "source_unit"))),
    tasks=(Task(id="convert", prompts=("Convert {size} {source} to KiB; 1 MiB = 1024 KiB and 1 GiB = 1024 MiB.", "How many KiB are in {size} {source}? Use 1024 KiB per MiB and 1024 MiB per GiB.", "Express {size} {source} in KiB, using 1024 KiB per MiB and 1024 MiB per GiB.", "Calculate KiB for {size} {source}; take 1 MiB as 1024 KiB and 1 GiB as 1024 MiB.", "What is {size} {source} in kibibytes? Use the binary factors 1024 KiB per MiB and 1024 MiB per GiB.", "Convert the binary size {size} {source} into KiB, with 1 GiB = 1024 MiB and 1 MiB = 1024 KiB.", "Find the KiB equivalent of {size} {source}; use 1024 MiB per GiB and 1024 KiB per MiB.", "Translate {size} {source} to KiB. Each MiB has 1024 KiB and each GiB has 1024 MiB.", "Give {size} {source} in KiB using 1024 KiB = 1 MiB and 1024 MiB = 1 GiB.", "How many kibibytes equal {size} {source} if a MiB is 1024 KiB and a GiB is 1024 MiB?", "Calculate the binary conversion of {size} {source} to KiB, using 1024 for both KiB per MiB and MiB per GiB.", "Determine the KiB count for {size} {source}, with 1024 KiB in a MiB and 1024 MiB in a GiB."), answers=("{result} KiB.", "{result} KiB."), cases=cases),),
)
