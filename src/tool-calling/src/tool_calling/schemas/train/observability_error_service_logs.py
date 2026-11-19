from ...schema_types import Decision, Parameter, Schema, Task


LOGS = {"api": "request timeout", "worker": "job failed", "billing": "payment rejected", "search": "index unavailable", "auth": "token expired", "gateway": "upstream reset"}


def cases(rng, count):
    for _ in range(count):
        services = rng.sample(tuple(LOGS), 3)
        errors = rng.sample(("E101", "E102", "E103", "E104", "E105", "E106"), 3)
        rows = list(zip(errors, services))
        yield {"error": rng.choice(errors), "rows": rows, "events": "; ".join(f"{error}: {service}" for error, service in rows)}


def prepare(*, task_id, case):
    service = next(service for error, service in case["rows"] if error == case["error"])
    return Decision(fields=case, arguments={"service": service})


def resolve(service):
    return f"{service}: {LOGS[service]}"


SCHEMA = Schema(
    id="observability_error_service_logs",
    tool_names=("get_service_logs", "lookup_service_logs", "read_sample_service_log", "fetch_service_log", "retrieve_sample_service_logs", "find_service_log", "get_sample_log_for_service", "lookup_sample_service_log", "read_service_log", "fetch_sample_log_by_service"),
    descriptions=("Get sample logs for a service.", "Look up a service's sample log.", "Retrieve the sample log for the specified service.", "Read the sample log associated with a service name.", "Find the named service's sample log entry.", "Fetch the recorded sample log for a service.", "Look up the sample log by service name.", "Return the sample log associated with the given service.", "Get the named service's recorded sample log.", "Read a service's log from the sample data."),
    parameters=(Parameter(names=("service", "service_name")),),
    tasks=(Task(id="logs", prompts=("Get logs for the service associated with error {error}. Error services: {events}.", "Look up the logs of the service for {error}; mappings: {events}.", "Find the service for error {error} in {events}, then retrieve its logs.", "Please fetch the logs for the service linked to {error}. Here are the error-to-service mappings: {events}.", "Using {events}, identify which service has error {error} and look up its logs.", "Error {error} needs investigation. Get its associated service's logs from these mappings: {events}.", "Which service corresponds to {error} in {events}? Retrieve that service's logs.", "Pull the logs for the service named alongside error {error}: {events}.", "For error {error}, read the logs of its service. The mappings are {events}.", "Find logs for the service mapped to {error}; the error-service pairs are {events}.", "Given the associations {events}, get the service logs for error {error}.", "Could you look up the logs of whichever service is associated with {error}? Mappings: {events}."), answers=("{result}", "Logs: {result}."), cases=cases),),
)
