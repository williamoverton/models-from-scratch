from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        total = rng.choice((100, 200, 250, 400, 500, 1000))
        failed = rng.randint(1, total)
        yield {"failed": str(failed), "total": str(total)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(failed, total):
    return f"{Decimal(failed) * 100 / Decimal(total):.2f}"


SCHEMA = Schema(
    id="observability_error_rate",
    tool_names=("calculate_error_rate", "compute_failure_percentage", "calculate_request_failure_rate", "compute_error_percentage", "calculate_failed_request_percentage", "derive_request_error_rate", "compute_request_failure_rate", "get_error_rate_percentage", "calculate_failure_percentage", "compute_failed_request_percentage"),
    descriptions=("Calculate failed requests as a percentage of total requests.", "Compute failure rate to two decimal places.", "Divide failed requests by total requests and return a percentage to two decimals.", "Calculate the request error percentage rounded to two decimal places.", "Compute failed divided by total times 100, to two decimal places.", "Return the failure percentage from failed and total request counts.", "Derive the error rate percentage from request counts, rounded to two decimals.", "Compute the percentage of requests that failed to two decimal places.", "Calculate the failure rate as a percentage of total requests.", "Find the percentage of failed requests, rounded to two decimal places."),
    parameters=(Parameter(names=("failed", "failed_requests")), Parameter(names=("total", "total_requests"))),
    tasks=(Task(id="rate", prompts=("Of {total} requests, {failed} failed. What is the error rate as a percentage, rounded to two decimal places?", "Calculate failed / total × 100 to two decimal places: failed {failed}, total {total}.", "We had {failed} failures out of {total} requests. Give the error percentage to two decimal places.", "What percentage of {total} requests failed if {failed} failed? Round to two decimals.", "Compute the failure rate as a percentage: {failed} failed requests, {total} total, two decimal places.", "For {total} total requests and {failed} failed requests, report the error rate rounded to hundredths of a percent.", "Please calculate {failed} divided by {total} as a percentage, to two decimal places; these are failed and total requests.", "Out of {total} requests, {failed} were errors. What's the percentage failure rate to two decimal places?", "Give me the request error rate, rounded to two decimal places, for {failed} failures in {total} requests.", "The request count is {total} and the failed count is {failed}; calculate their failure percentage to two decimals.", "How many percent of the {total} requests failed when the failure count was {failed}? Use two decimal places.", "Convert the fraction {failed} failed out of {total} requests into a percentage rounded to two decimal places."), answers=("Error rate: {result}%.", "The failure rate is {result}%."), cases=cases),),
)
