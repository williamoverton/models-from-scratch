from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        budget = rng.randint(8, 30) * 100
        used = rng.randint(1, budget // 100) * 100
        yield {"budget": str(budget), "used": str(used)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(budget, used):
    return str(int(budget) - int(used))


SCHEMA = Schema(
    id="publishing_word_budget",
    tool_names=("calculate_words_remaining", "compute_word_budget", "subtract_words_used", "find_remaining_words", "calculate_word_allowance", "determine_words_left", "compute_remaining_word_budget", "get_words_remaining", "work_out_word_balance", "subtract_word_usage"),
    descriptions=("Subtract used words from the total word budget.", "Calculate the remaining word allowance.", "Find words left by subtracting words used from the budget.", "Compute the unused portion of an article's word limit.", "Determine the remaining words from a budget and current usage.", "Subtract the written word count from the word allowance.", "Calculate the word budget balance after words already used.", "Return the difference between the word limit and words used.", "Work out how many words remain under the article budget.", "Compute remaining allowance from the total and used word counts."),
    parameters=(Parameter(names=("budget", "word_limit")), Parameter(names=("used", "words_used"))),
    tasks=(Task(id="remaining", prompts=("The article budget is {budget} words and {used} are already written. How many words remain?", "A {budget}-word limit has {used} words used. Calculate the remaining allowance.", "With {used} words written from a {budget}-word budget, how many are left?", "Subtract {used} used words from the {budget}-word article allowance.", "Find the remaining words: budget {budget}, written {used}.", "An article may use {budget} words and has used {used}. What is its balance?", "How many words remain if {used} of {budget} have been written?", "Calculate the unused portion of a {budget}-word limit after {used} words.", "The word allowance is {budget}; {used} words are complete. Find the remainder.", "Determine the words left in a {budget}-word budget with {used} used.", "For an article capped at {budget} words, subtract the {used} already written.", "What is the remaining word allowance after using {used} out of {budget} words?"), answers=("{result} words remain.", "Remaining: {result} words."), cases=cases),),
)
