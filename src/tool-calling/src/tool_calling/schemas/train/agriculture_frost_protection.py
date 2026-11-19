from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        forecast = rng.randint(-5, 5)
        ids = rng.sample(range(10, 99), 3)
        thresholds = [forecast + rng.randint(1, 4), forecast, forecast - rng.randint(1, 4)]
        rng.shuffle(thresholds)
        yield {"forecast": str(forecast), "beds": "; ".join(f"B-{bed}={threshold}" for bed, threshold in zip(ids, thresholds))}


def prepare(*, task_id, case):
    forecast = int(case["forecast"])
    entries = [entry.strip().split("=") for entry in case["beds"].split(";")]
    bed = next(bed for bed, threshold in entries if forecast < int(threshold))
    return Decision(fields=case, arguments={"bed": bed})


def resolve(bed):
    return f"Protection requested for {bed}"


SCHEMA = Schema(
    id="agriculture_frost_protection",
    tool_names=("request_frost_cover", "protect_crop_bed", "submit_frost_cover_request", "request_bed_cover", "cover_bed_for_frost", "flag_bed_for_protection", "schedule_bed_frost_cover", "send_crop_cover_request", "request_protective_bed_cover", "mark_bed_for_frost_cover"),
    descriptions=("Request frost protection for the supplied bed ID.", "Submit a bed ID for protective covering.", "Request a protective cover for the specified crop bed.", "Submit a frost-cover request using a bed identifier.", "Mark the supplied bed for frost protection.", "Send a covering request for the given bed ID.", "Register a request to protect the identified bed from frost.", "Request frost covering for one selected bed.", "Identify a bed to be covered against frost.", "Submit the selected crop bed for protective covering."),
    parameters=(Parameter(names=("bed", "bed_id")),),
    tasks=(Task(id="protect", prompts=(
        'Forecast low is {forecast}°C. Cover the one bed where the low is strictly below its protection threshold; equality needs no cover. Beds are ID=threshold °C: {beds}.',
        'Request cover for the bed whose threshold exceeds the {forecast}°C forecast, not one equal to it. Entries ID=threshold: {beds}.',
        'Among these beds ({beds}, ID=threshold in °C), request frost cover for the one with a threshold above the forecast of {forecast}°C; equal temperatures do not qualify.',
        'A low of {forecast}°C is expected. Which bed in {beds} needs a cover request? Each entry gives ID=threshold °C; cover only when the low is strictly less than that threshold.',
        'Using {beds} as ID=protection threshold in °C, submit a cover request for the bed threatened by a {forecast}°C low. The forecast must be below, not equal to, the threshold.',
        'Please request protective covering: the forecast is {forecast}°C and {beds} lists bed IDs with their thresholds in °C. Select only the threshold strictly greater than the forecast.',
        'For the overnight low of {forecast}°C, cover the bed from {beds} whose ID=threshold °C entry has a higher threshold; a match at equality needs no cover.',
        'One crop bed warrants a frost-cover request. Its threshold in {beds} (ID=threshold °C) exceeds the forecast low of {forecast}°C; equal values are excluded. Request the cover.',
        'Compare the {forecast}°C forecast against the ID=threshold °C list {beds}. Request a cover for the bed only if the forecast falls strictly below its threshold, never when equal.',
        'Send a frost cover request for the qualifying bed in {beds}. Entries pair each ID with its threshold in °C; the predicted low is {forecast}°C and must be strictly lower.',
        'Which bed should be covered? At {forecast}°C, use {beds} (ID=threshold °C), select the threshold above the low rather than equal to it, and request cover.',
        'The bed thresholds, in °C, are {beds} (ID=threshold). With {forecast}°C forecast, submit a cover request for the one whose threshold is strictly higher; equality does not count.',
    ), answers=("{result}.", "{result}."), cases=cases),),
)
