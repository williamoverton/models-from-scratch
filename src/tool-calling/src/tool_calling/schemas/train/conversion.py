from ...schema_types import Decision, Schema, Parameter, Task


def cases(rng, count):
    for _ in range(count):
        yield {"metres": str(rng.randrange(1, 1001)), "unit": rng.choice(("cm", "mm"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="length_conversion",
    tool_names=("convert_length", "length_in", "convert_metres_to_metric_unit", "calculate_metric_length", "express_metres_in_unit", "convert_metre_measurement", "compute_centimetres_or_millimetres", "convert_metres_to_smaller_unit", "find_metric_length_conversion", "translate_metre_length"),
    descriptions=("Convert a length in metres to centimetres or millimetres.", "Express a metre measurement in a smaller metric unit.", "Multiply metres by 100 for centimetres or 1000 for millimetres.", "Convert the supplied metre value to the requested cm or mm unit.", "Calculate the equivalent length in centimetres or millimetres from metres.", "Express a whole number of metres in the selected smaller metric unit.", "Find the cm or mm equivalent of a length specified in metres.", "Convert metres to cm using 100 per metre or mm using 1000 per metre.", "Compute a metric length conversion from metres to the requested unit.", "Return the numerical length in either centimetres or millimetres."),
    parameters=(
        Parameter(names=("metres", "length_m")),
        Parameter(names=("unit", "target_unit")),
    ),
    tasks=(Task(id="convert", prompts=('Convert {metres} metres to {unit}.', 'How many {unit} are in {metres} metres?', 'Express a length of {metres} metres in {unit}.', 'The measurement is {metres} metres; calculate its equivalent in {unit}.', 'In {unit}, what is the value of a {metres}-metre length?', 'Change the unit of this measurement from metres to {unit}: {metres} metres.', 'Please give the {unit} equivalent for {metres} metres.', 'A distance measures {metres} metres. Represent it using {unit} instead.', 'Find the numerical length in {unit} corresponding to {metres} metres.', 'Rewrite {metres} metres as a measurement in {unit}.', 'For a length of {metres} metres, determine the conversion into {unit}.', 'What does {metres} metres become when expressed in {unit}?'), answers=("{metres} metres is {result} {unit}.", "That is {result} {unit}."), cases=cases),),
)


def resolve(metres, unit):
    return str(int(metres) * {"cm": 100, "mm": 1000}[unit])
