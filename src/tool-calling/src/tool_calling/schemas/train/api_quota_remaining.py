from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        limit = rng.randint(10, 10000)
        yield {'limit': str(limit), 'used': str(rng.randint(0, limit))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(limit, used):
    return str(int(limit) - int(used))


SCHEMA = Schema(
    id='api_quota_remaining',
    tool_names=('calculate_api_quota_remaining', 'subtract_api_usage', 'compute_remaining_api_requests', 'find_unused_api_quota', 'calculate_request_headroom', 'derive_quota_balance', 'compute_quota_after_usage', 'find_remaining_request_allowance', 'subtract_requests_from_limit', 'determine_api_quota_balance'),
    descriptions=('Subtract requests used from the quota.', 'Calculate remaining requests.', 'Compute the request limit minus requests used.', 'Find unused API quota by subtracting usage from the limit.', 'Determine how many requests remain within the quota.', 'Calculate the remaining request allowance after usage.', 'Subtract the used request count from the API limit.', 'Return the difference between quota limit and used requests.', 'Find request headroom from the stated limit and usage.', 'Compute the unused portion of a request quota.'),
    parameters=(Parameter(names=('limit', 'quota_limit')), Parameter(names=('used', 'requests_used'))),
    tasks=(Task(id='remaining', prompts=('An API quota permits {limit} requests and {used} have been used. How many remain?', 'The limit is {limit} requests, with {used} used. Subtract usage to find the remaining quota.', 'After {used} requests against a {limit}-request API allowance, calculate the unused request count.', 'How much request headroom is left if usage stands at {used} and the API cap is {limit} requests?', 'Deduct {used} consumed requests from the API quota of {limit}; report the remaining requests.', 'The API has already handled {used} requests out of an allowed {limit}. Determine how many more requests fit within the quota.', 'Given a request ceiling of {limit} and current usage of {used}, find the remaining API allowance.', 'There are {limit} requests in the quota. With {used} spent, what is the balance in requests?', 'Calculate limit minus usage for an API with {used} requests used and a limit of {limit} requests.', 'Of the {limit} API requests permitted, {used} are consumed. Give the number still available.', 'A request budget started at {limit} and usage is now {used} requests. Compute its unused portion.', 'If the API request limit is {limit}, what remains after {used} requests have been used?'), answers=('{result} requests remain.', '{result} requests remain.'), cases=cases),),
)
