from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        limits = [rng.randrange(15, 61, 5) for _ in range(3)]
        sizes = [max(1, limit + rng.choice((-5, 0, 5))) for limit in limits]
        yield dict(zip(("length", "width", "height", "max_length", "max_width", "max_height"), map(str, sizes + limits)))


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="parcel_dimension_fit",
    tool_names=("check_parcel_fit", "compare_box_dimensions", "assess_parcel_dimensions", "check_dimension_limits", "evaluate_box_fit", "verify_parcel_size", "compare_parcel_limits", "determine_dimension_fit", "check_fixed_orientation_fit", "assess_shipment_size"),
    descriptions=("Compare each parcel dimension to its corresponding inclusive limit without rotation.", "Check length, width and height against matching maximums; equality fits and rotation is not allowed.", "Determine whether a parcel fits its dimension limits in the stated orientation.", "Evaluate each parcel measurement against its matching maximum without rotating it.", "Check fixed-orientation parcel fit, allowing measurements equal to their limits.", "Compare parcel length, width and height with their respective inclusive caps.", "Assess whether all three parcel dimensions stay within their corresponding limits.", "Verify box dimensions against their matching maximums with no rotation.", "Determine parcel size compliance using inclusive, axis-specific limits.", "Test whether a parcel fits the given length, width and height limits as oriented."),
    parameters=(Parameter(names=("length", "parcel_length")), Parameter(names=("width", "parcel_width")), Parameter(names=("height", "parcel_height")), Parameter(names=("max_length", "length_limit")), Parameter(names=("max_width", "width_limit")), Parameter(names=("max_height", "height_limit"))),
    tasks=(Task(id="fit", prompts=("A parcel is {length} × {width} × {height} cm (length × width × height). Limits are {max_length} × {max_width} × {max_height} cm in that order. Does it fit? Equality is allowed; no rotation.", "Check {length} cm length, {width} cm width and {height} cm height against respective limits {max_length}, {max_width}, {max_height} cm. Each may equal its limit; do not rotate.", "Does a {length} × {width} × {height} cm parcel fit limits {max_length} × {max_width} × {max_height} cm, respectively? Equality fits; no rotation.", "Compare length {length}, width {width}, height {height} cm to respective caps {max_length}, {max_width}, {max_height} cm. No rotation; equality is permitted.", "Assess fixed-orientation fit: parcel L/W/H {length}/{width}/{height} cm, maximum L/W/H {max_length}/{max_width}/{max_height} cm; equal dimensions fit.", "Are dimensions {length}, {width}, {height} cm within their matching limits {max_length}, {max_width}, {max_height} cm? Allow equality and prohibit rotation.", "Check a parcel of length {length}, width {width}, height {height} cm against maximum length {max_length}, width {max_width}, height {max_height} cm. Equality counts; no turning.", "With no rotation and inclusive limits, does {length} × {width} × {height} cm fit {max_length} × {max_width} × {max_height} cm in corresponding order?", "Determine whether each of {length}, {width}, {height} cm is at most its respective limit {max_length}, {max_width}, {max_height} cm; do not rotate the parcel.", "For L/W/H {length}/{width}/{height} cm and respective maxima {max_length}/{max_width}/{max_height} cm, report fit without rotation; equality is allowed.", "Can the {length} × {width} × {height} cm box fit the corresponding {max_length} × {max_width} × {max_height} cm limits without rotation? Equal is acceptable.", "Compare parcel axes {length}, {width}, {height} cm with corresponding limits {max_length}, {max_width}, {max_height} cm. Include equality; keep orientation fixed."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(length, width, height, max_length, max_width, max_height):
    fits = all(int(size) <= int(limit) for size, limit in zip((length, width, height), (max_length, max_width, max_height)))
    return f"The {length} × {width} × {height} cm parcel {'fits' if fits else 'does not fit'} the {max_length} × {max_width} × {max_height} cm limits without rotation."
