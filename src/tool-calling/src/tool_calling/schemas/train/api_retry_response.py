from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        ids = rng.sample(range(100, 1000), 3)
        codes = [rng.choice((429, 500, 502, 503, 504)), *rng.sample((200, 201, 400, 401, 403, 404), 2)]
        entries = list(zip(ids, codes))
        rng.shuffle(entries)
        yield {'responses': '; '.join(f'R-{ident} {code}' for ident, code in entries)}


def prepare(*, task_id, case):
    entries = [entry.split() for entry in case['responses'].split('; ')]
    response = next(ident for ident, code in entries if int(code) == 429 or 500 <= int(code) <= 599)
    return Decision(fields=case, arguments={'response': response})


def resolve(response):
    return f'Retry requested for response {response}'


SCHEMA = Schema(
    id='api_retry_eligible_response',
    tool_names=('retry_api_response', 'request_response_retry', 'simulate_response_retry', 'retry_response_by_id', 'submit_api_retry_request', 'request_retry_by_response', 'retry_selected_response', 'simulate_api_response_retry', 'send_response_retry_request', 'request_selected_response_retry'),
    descriptions=('Simulate a retry for the supplied response ID.', 'Request a simulated response retry by ID.', 'Submit a simulated retry for the specified API response.', 'Return a retry request confirmation for the given response ID.', 'Simulate requesting another attempt for one response.', 'Request a retry of the selected response in the simulation.', 'Record a simulated retry request for an API response identifier.', 'Use a response ID to request a simulated retry.', 'Simulate sending a retry request for the supplied response.', 'Request retry of one identified response without performing a real API call.'),
    parameters=(Parameter(names=('response', 'response_id')),),
    tasks=(Task(id='retry', prompts=('Retry the only eligible response: {responses}. Entries are ID and status code; eligible codes are 429 and 500–599 inclusive.', 'Responses are {responses} (ID, status code). Simulate retrying the unique response with code 429 or 500 through 599, inclusive.', 'Request a simulated retry for whichever ID has status 429 or 500–599 inclusive in these ID/status pairs: {responses}.', 'Among {responses}, each entry pairs an ID with a status code. Retry the sole entry whose code is 429 or lies from 500 to 599 inclusive.', 'The retry policy permits status 429 and every status from 500 through 599, including both endpoints. Apply it to the ID and status entries {responses} and simulate retrying the match.', 'Given ID/status-code pairs {responses}, send a simulated retry request for the only response with code 429 or 500–599 inclusive.', 'One response qualifies for another attempt: its status is 429 or between 500 and 599 inclusive. Simulate that retry using these ID/code entries: {responses}.', 'Inspect the response IDs and status codes in {responses}; only 429 or 500 through 599 inclusive qualifies. Request a simulated retry for the qualifying ID.', 'For {responses}, entries consist of response ID and status code. Simulate a retry of the unique response permitted by the 429 or inclusive 500–599 rule.', 'Use the status codes in {responses} to pick the sole retryable ID, then simulate its retry. Eligible statuses are 429 and 500–599 inclusive.', 'Apply the retry rule to these response ID/status pairs: {responses}. A code of 429 or any code from 500 to 599 inclusive qualifies; simulate retrying that response.', 'Which response in {responses} should be retried? Each entry contains an ID and status code, and eligibility is limited to 429 or 500–599 inclusive. Simulate the retry.'), answers=('{result}.', '{result}.'), cases=cases),),
)
