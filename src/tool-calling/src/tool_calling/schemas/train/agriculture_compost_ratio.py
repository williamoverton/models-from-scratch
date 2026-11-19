from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"green": str(rng.randint(1, 30)), "brown_parts": str(rng.randint(2, 5)), "green_parts": str(rng.choice((1, 2, 3)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(green, brown_parts, green_parts):
    from fractions import Fraction
    return str(Fraction(int(green) * int(brown_parts), int(green_parts)))


SCHEMA = Schema(
    id="agriculture_compost_ratio",
    tool_names=("calculate_compost_browns", "estimate_brown_material", "compute_compost_brown_volume", "find_browns_for_greens", "size_compost_brown_input", "determine_brown_volume", "calculate_brown_ratio_volume", "match_compost_materials", "derive_brown_material_amount", "compute_browns_from_ratio"),
    descriptions=("Calculate brown material volume from green volume and a brown-to-green volume ratio; return exact fractions if needed.", "Apply a brown:green volume ratio to a given green volume.", "Multiply green volume by brown parts over green parts, preserving exact fractions.", "Find liters of brown compost material matching the supplied greens and ratio.", "Determine brown volume from a green volume and the specified brown-to-green parts.", "Compute the exact brown material requirement for a compost mix.", "Apply the given brown-to-green proportions to the green volume.", "Calculate browns needed for greens using the stated volume ratio.", "Derive brown material volume, expressing nonintegers as exact fractions.", "Convert a green material volume into its corresponding brown volume using the ratio."),
    parameters=(Parameter(names=("green", "green_volume")), Parameter(names=("brown_parts",)), Parameter(names=("green_parts",))),
    tasks=(Task(id="ratio", prompts=(
        'For compost, use a brown:green volume ratio of {brown_parts}:{green_parts}. Given {green} liters of green material, how many liters of brown material are needed? Give an exact fraction if necessary.',
        'At a {brown_parts}:{green_parts} brown-to-green volume ratio, how many liters of browns match {green} liters of greens? Use an exact fraction if needed.',
        'You have {green} liters of greens. For a compost mix with {brown_parts} parts brown by volume to {green_parts} parts green, calculate the brown liters, using an exact fraction if needed.',
        'How much brown material, in liters, accompanies {green} liters of green material at a brown:green volume ratio of {brown_parts}:{green_parts}? Keep any fractional result exact.',
        'A compost recipe specifies {brown_parts}:{green_parts} brown to green by volume. The green supply is {green} liters; find the matching brown volume in liters as an exact fraction if necessary.',
        'Scale {brown_parts} brown parts to {green_parts} green parts by volume for {green} liters of green compost material. Report brown liters, with an exact fraction where needed.',
        'For {green} liters of greens, determine the liters of browns required by a {brown_parts}:{green_parts} brown-to-green volume mix; do not round fractional quantities.',
        'What is the exact brown material volume in liters if {green} liters of green material must be mixed at {brown_parts} brown parts per {green_parts} green parts by volume? Give fractions when needed.',
        'The green component measures {green} liters. Match it with brown material at a volume ratio of brown:green = {brown_parts}:{green_parts}, expressing the brown liters as an exact fraction if nonintegral.',
        'Mix browns and greens in the volume proportions {brown_parts}:{green_parts}. Given {green} liters of the latter, calculate liters of the former and retain exact fractions.',
        'Find the brown liters needed for {green} liters of green matter when the compost volume ratio is {brown_parts} brown to {green_parts} green. Use an exact fraction if the answer is not whole.',
        'The recipe calls for {brown_parts} volumes of brown for every {green_parts} volumes of green. With {green} liters of green, report the required brown liters exactly, using a fraction if necessary.',
    ), answers=("Use {result} liters of brown material.", "Brown material needed: {result} liters."), cases=cases),),
)
