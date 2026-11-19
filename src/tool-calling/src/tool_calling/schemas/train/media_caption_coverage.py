from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("V1", "V2", "V3", "V4", "V5", "V6"), 3)
        language, other = rng.sample(("English", "French", "Spanish", "German"), 2)
        missing = rng.randrange(3)
        rows = [(name, (other,) if i == missing else (language, other)) for i, name in enumerate(names)]
        yield {"language": language, "rows": rows, "videos": "; ".join(f"{name}: {', '.join(languages)}" for name, languages in rows)}


def prepare(*, task_id, case):
    video = next(name for name, languages in case["rows"] if case["language"] not in languages)
    return Decision(fields=case, arguments={"video": video})


def resolve(video):
    return f"Flagged video: {video}."


SCHEMA = Schema(
    id="media_caption_coverage",
    tool_names=("flag_video_missing_captions", "mark_video_for_captioning", "flag_video_for_captioning", "mark_video_missing_captions", "record_captioning_flag", "flag_selected_video", "mark_selected_video_for_captions", "record_video_caption_flag", "flag_caption_work_item", "mark_video_caption_needed"),
    descriptions=("Flag a video by identifier.", "Mark the named video for captioning.", "Flag the selected video ID for captioning.", "Record a captioning flag for the supplied video identifier.", "Mark the specified video as needing captions.", "Flag the named video for caption work.", "Record that the selected video needs captioning.", "Mark a video identified by ID for captioning.", "Flag the given video identifier as needing captions.", "Record the selected video as a captioning work item."),
    parameters=(Parameter(names=("video", "video_id")),),
    tasks=(Task(id="coverage", prompts=("Each video's caption languages are listed: {videos}. Flag the video missing {language} captions.", "Caption tracks: {videos}. Mark the video that does not have a {language} track.", "Which video needs {language} captions? Flag it based on these tracks: {videos}.", "Review the caption languages ({videos}) and flag the video without {language}.", "From {videos}, mark the video missing a {language} caption track.", "Please flag the video requiring {language} captions: {videos}.", "The available caption tracks are {videos}. Identify and flag the video lacking {language}.", "Check {videos} for {language} caption coverage and mark the video that lacks it.", "One of these videos has no {language} captions: {videos}. Flag that video.", "Using the listed caption languages, {videos}, mark the video that needs a {language} track.", "Flag the video without captions in {language}; the tracks are {videos}.", "For captioning in {language}, which video should be flagged? Available tracks: {videos}."), answers=("{result}", "{result}"), cases=cases),),
)
