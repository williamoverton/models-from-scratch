from ...schema_types import Decision, Parameter, Schema, Task


TITLES = ("Project Atlas", "Annual Review", "Roadmap 2026", "Q&A Guide", "Design Notes", "Plan B", "North-West", "Meeting: Phase 2")


def cases(rng, count):
    for _ in range(count):
        yield {"title": rng.choice(TITLES)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"title": case["title"]})


def resolve(title):
    return f"{len(title)} characters"


SCHEMA = Schema(
    id="docs_title_character_count",
    tool_names=('count_title_characters', 'measure_document_title', 'count_document_title_characters', 'title_character_count', 'get_title_length', 'measure_title_length', 'count_title_chars', 'calculate_title_length', 'character_count_for_title', 'compute_title_characters'),
    descriptions=('Count characters in the supplied title, including spaces and punctuation.', 'Return the number of characters in a document title, including spaces and punctuation.', 'Count characters in a title including spaces and punctuation.', 'Return the title character count including spaces and punctuation.', 'Get the number of title characters, including spaces and punctuation.', 'Measure title length counting spaces and punctuation.', 'Count all characters in the provided title, including punctuation and spaces.', 'Calculate title length with spaces and punctuation included.', 'Return the count of characters in the title including spaces and punctuation.', 'Compute the supplied title’s character count including spaces and punctuation.'),
    parameters=(Parameter(names=("title", "document_title")),),
    tasks=(Task(id="count", prompts=('Count the characters in the title "{title}", including spaces and punctuation.', 'How many characters are in "{title}"? Count spaces and punctuation too.', 'Measure the character length of "{title}", counting spaces and punctuation.', 'How long is the title "{title}" in characters, including punctuation and spaces?', 'Give the character count for "{title}"; include spaces and punctuation.', 'Count every character in the title "{title}", including its spaces and punctuation.', 'What is the length of "{title}" when spaces and punctuation are counted?', 'For the title "{title}", calculate the number of characters including punctuation and spaces.', 'Please count the characters of "{title}" without excluding spaces or punctuation.', 'Find the total character count of the title "{title}", spaces and punctuation included.', 'Determine how many characters the title "{title}" contains, counting punctuation and spaces.', 'Count all characters, including spaces and punctuation, in this title: "{title}".'), answers=("The title has {result}.", "Count: {result}."), cases=cases),),
)
