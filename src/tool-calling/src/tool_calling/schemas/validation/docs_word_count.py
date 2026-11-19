from ...schema_types import Decision, Parameter, Schema, Task


WORDS = ("clear", "draft", "review", "team", "publish", "notes", "project", "update", "policy", "today", "quickly", "accurate")


def cases(rng, count):
    for _ in range(count):
        words = [rng.choice(WORDS) for _ in range(rng.randrange(2, 13))]
        separators = [rng.choice((" ", "  ", "\n")) for _ in range(len(words) - 1)]
        text = words[0] + "".join(separator + word for separator, word in zip(separators, words[1:]))
        yield {"text": text}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(text):
    return str(len(text.split()))


SCHEMA = Schema(
    id="docs_count_words",
    tool_names=('count_words', 'document_word_count', 'count_text_words', 'count_whitespace_tokens', 'calculate_word_count', 'get_text_word_count', 'tally_text_words', 'count_document_tokens', 'measure_text_word_count', 'compute_word_total'),
    descriptions=('Count whitespace-separated words in the supplied text.', 'Return the number of nonempty whitespace-delimited tokens in the input text.', 'Calculate the word count by splitting text on whitespace.', 'Count nonempty tokens separated by whitespace in text.', 'Tally words in the given text using whitespace as the separator.', 'Compute how many whitespace-delimited words the text contains.', 'Return a count of the text’s nonempty whitespace-separated tokens.', 'Measure the number of words in text, treating whitespace as the delimiter.', 'Find the number of tokens obtained by splitting text on whitespace.', 'Get the whitespace-based word count for the supplied text.'),
    parameters=(Parameter(names=("text", "content", "document_text")),),
    tasks=(Task(id="count", prompts=("Count the whitespace-separated words in this text, exactly as shown between the markers:\n<text>{text}</text>", "How many words are in the following text? A word is a nonempty whitespace-separated token.\n<text>{text}</text>", 'Count nonempty whitespace-separated tokens in the exact text between markers:\n<text>{text}</text>', 'How many whitespace-delimited words are in this exact marked text?\n<text>{text}</text>', 'Treat each nonempty whitespace-separated token as a word; count the marked text exactly:\n<text>{text}</text>', 'Find the word count of the text between these markers, splitting on whitespace:\n<text>{text}</text>', 'In the exact text below, count words as nonempty whitespace-separated tokens:\n<text>{text}</text>', 'Tally the whitespace-separated words in this marked text without changing it:\n<text>{text}</text>', 'How many nonempty tokens result from splitting this exact marked text on whitespace?\n<text>{text}</text>', 'Determine the number of words in the marked text, where words are whitespace-separated:\n<text>{text}</text>', 'Using whitespace as the word delimiter, count the exact text inside these markers:\n<text>{text}</text>', 'Count the nonempty words separated by whitespace in the following exact text:\n<text>{text}</text>'), answers=("The text contains {result} words.", "Word count: {result}."), cases=cases),),
)
