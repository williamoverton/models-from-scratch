from ...schema_types import Decision, Parameter, Schema, Task


CATEGORY_BY_KEYWORD = {'invoice': 'Billing', 'password': 'Accounts', 'crash': 'Technical', 'delivery': 'Fulfillment'}


def cases(rng, count):
    for ticket in rng.sample(range(100000, 1000000), count):
        keyword = rng.choice(tuple(CATEGORY_BY_KEYWORD))
        subject = rng.choice(('Please investigate {}', 'Question about {}', 'Help needed: {}', 'Issue involving {}')).format(keyword)
        yield {'subject': subject, 'ticket': f'T-{ticket}'}


def prepare(*, task_id, case):
    category = next(category for keyword, category in CATEGORY_BY_KEYWORD.items() if keyword in case['subject'].lower().split())
    return Decision(fields=case, arguments={'category': category})


def resolve(category):
    return f'Selected category: {category}'


SCHEMA = Schema(
    id='support_category_by_keyword',
    tool_names=('select_ticket_category', 'record_support_category', 'report_ticket_category', 'submit_support_category', 'confirm_ticket_category', 'acknowledge_support_category', 'return_ticket_category', 'provide_support_category', 'record_ticket_category', 'report_support_category'),
    descriptions=('Record the supplied category.', 'Acknowledge a support category selection.', 'Report the selected ticket category.', 'Submit the chosen support category.', 'Confirm the supplied ticket category.', 'Return the selected support category.', 'Provide a category for the ticket.', 'Record the chosen support category.', 'Identify the supplied ticket category.', 'Report a support category selection.'),
    parameters=(Parameter(names=('category', 'category_name')),),
    tasks=(Task(id='category', prompts=('Choose a category for ticket {ticket} with subject "{subject}" using this keyword map: invoice -> Billing; password -> Accounts; crash -> Technical; delivery -> Fulfillment. Match whole words case-insensitively.', 'Apply this whole-word, case-insensitive keyword map to ticket {ticket}, subject "{subject}": invoice=Billing, password=Accounts, crash=Technical, delivery=Fulfillment. Select the category.', 'Categorize ticket {ticket} with subject "{subject}": invoice goes to Billing, password to Accounts, crash to Technical, delivery to Fulfillment. Match whole words without case sensitivity.', 'For ticket {ticket}, subject "{subject}", select the category using whole-word, case-insensitive matches: invoice -> Billing; password -> Accounts; crash -> Technical; delivery -> Fulfillment.', 'Which category fits ticket {ticket}, subject "{subject}"? Map invoice to Billing, password to Accounts, crash to Technical, delivery to Fulfillment; match whole words case-insensitively.', 'Classify ticket {ticket} based on "{subject}" using case-insensitive whole words: invoice=Billing, password=Accounts, crash=Technical, delivery=Fulfillment.', 'Choose the category for {ticket}, subject "{subject}", by matching whole words ignoring case: invoice/Billing, password/Accounts, crash/Technical, delivery/Fulfillment.', 'Apply the following case-insensitive whole-word map to ticket {ticket}, subject "{subject}": invoice -> Billing; password -> Accounts; crash -> Technical; delivery -> Fulfillment. Select its category.', 'Determine the category of ticket {ticket} with subject "{subject}" from invoice: Billing, password: Accounts, crash: Technical, delivery: Fulfillment. Match whole words, ignoring case.', 'Ticket {ticket} has subject "{subject}". Use whole-word case-insensitive matching to select a category: invoice=Billing, password=Accounts, crash=Technical, delivery=Fulfillment.', 'For "{subject}" on ticket {ticket}, categorize by whole words without regard to case: invoice to Billing, password to Accounts, crash to Technical, delivery to Fulfillment.', 'Select the category for ticket {ticket} ("{subject}"): invoice maps to Billing, password to Accounts, crash to Technical, delivery to Fulfillment. Match whole words case-insensitively.'), answers=('{result}.', '{result}.'), cases=cases),),
)
