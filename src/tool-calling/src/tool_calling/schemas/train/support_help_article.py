from ...schema_types import Decision, Parameter, Schema, Task


ARTICLES = {"password reset": "Resetting your password", "billing": "Understanding your bill", "two-factor authentication": "Setting up two-factor authentication", "account closure": "Closing your account", "notifications": "Managing notifications", "data export": "Exporting your data", "invoices": "Downloading invoices", "profile": "Updating your profile"}


def cases(rng, count):
    for _ in range(count):
        yield {"topic": rng.choice(tuple(ARTICLES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(topic):
    return f"{topic}: {ARTICLES[topic]}"


SCHEMA = Schema(
    id="support_help_article_by_topic",
    tool_names=("find_help_article", "lookup_help_topic", "get_help_article_by_topic", "find_article_for_topic", "lookup_article_by_topic", "retrieve_help_article_title", "get_help_topic_article", "search_sample_help_catalog", "find_sample_article_title", "lookup_help_catalog_topic"),
    descriptions=("Find the sample help article title for an exact topic.", "Look up a topic in the sample help-center catalog.", "Retrieve the sample article title for a given topic.", "Find the help-center title matching an exact topic.", "Look up an exact topic in the sample article catalog.", "Get the sample help article associated with a topic.", "Return the catalog article title for the supplied topic.", "Find a sample help-center article by topic.", "Retrieve the help title for an exact catalog topic.", "Identify the sample article listed for a topic."),
    parameters=(Parameter(names=("topic", "help_topic", "subject")),),
    tasks=(Task(id="article", prompts=("Which help article covers {topic}?", "Find the help-center article for the topic {topic}.", "Look up the help article about {topic}.", "What help-center article addresses {topic}?", "Locate the catalog article for {topic}.", "I'd like the help article covering {topic}.", "Find the support article related to {topic}.", "Which article in the help catalog is for {topic}?", "Please identify the help-center article on {topic}.", "What article should I consult for {topic}?", "Retrieve the help article for the topic {topic}.", "Can you find the help-center entry that covers {topic}?"), answers=("The article is {result}.", "The help catalog lists {result}."), cases=cases),),
)
