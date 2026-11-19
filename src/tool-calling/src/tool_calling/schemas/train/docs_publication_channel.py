from ...schema_types import Decision, Parameter, Schema, Task


CHANNELS = ("intranet", "help center", "partner portal", "public website", "email digest")
AUDIENCES = ("employees", "customers", "partners", "everyone", "subscribers")


def cases(rng, count):
    for _ in range(count):
        channels = rng.sample(CHANNELS, len(CHANNELS))
        rule = "; ".join(f"{audience}={channel}" for audience, channel in zip(AUDIENCES, channels))
        yield {"audience": rng.choice(AUDIENCES), "rule": rule}


def prepare(*, task_id, case):
    mapping = dict(entry.strip().split("=", 1) for entry in case["rule"].split(";"))
    return Decision(fields=case, arguments={"channel": mapping[case["audience"]]})


def resolve(channel):
    return f"Selected channel: {channel}"


SCHEMA = Schema(
    id="docs_publication_channel_by_audience",
    tool_names=('acknowledge_selected_publication_channel', 'report_publication_channel', 'return_selected_channel', 'acknowledge_publication_channel', 'show_selected_publication_channel', 'report_channel_selection', 'echo_publication_channel', 'confirm_selected_channel', 'return_publication_selection', 'report_chosen_channel'),
    descriptions=('Report the selected publication channel.', 'Return the channel selected for publication.', 'Acknowledge the supplied channel as the publication selection.', 'Show the provided channel with a selection label.', 'Echo the selected publication channel.', 'Return a selection message for the supplied publication channel.', 'Present the given channel as the selected publication channel.', 'Confirm the provided channel in a selection report.', 'Output the selected channel supplied by the caller.', 'Report the given channel as the publication selection.'),
    parameters=(Parameter(names=("channel", "publication_channel", "selected_channel")),),
    tasks=(Task(id="channel", prompts=("Choose a publication channel for audience {audience}. Use this exact audience=channel rule: {rule}.", "Given the mapping {rule}, select the publication channel for a document for {audience}.", 'For audience {audience}, report the publication channel dictated by this exact mapping: {rule}.', 'Using {rule} as the audience=channel mapping, select the channel for {audience}.', 'A document targets {audience}; determine its channel from the exact rule {rule}.', 'Apply {rule} to audience {audience} and report the chosen publication channel.', 'Which publication channel corresponds to {audience} under this exact mapping: {rule}?', 'Match the audience {audience} to its publication channel according to {rule}.', 'The audience is {audience}; use the audience=channel rule {rule} to choose where to publish.', 'Find the channel assigned to {audience} in this mapping: {rule}.', 'Select a document publication channel for {audience}, following {rule} exactly.', 'Consult the audience=channel rule {rule}: what channel should be selected for {audience}?'), answers=("{result}.", "The selection is {result}."), cases=cases),),
)
