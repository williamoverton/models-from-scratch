from ...schema_types import Decision, Parameter, Schema, Task


HEALTH = {"api": "healthy", "worker": "degraded", "billing": "healthy", "search": "unhealthy", "auth": "healthy", "gateway": "degraded"}


def cases(rng, count):
    for _ in range(count):
        yield {"service": rng.choice(tuple(HEALTH))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(service):
    return f"{service}: {HEALTH[service]}"


SCHEMA = Schema(
    id="operations_service_health",
    tool_names=("get_service_health", "lookup_service_health", "read_service_health", "fetch_sample_service_health", "find_service_health_status", "retrieve_service_health", "get_sample_health_status", "lookup_service_status", "read_sample_service_status", "check_sample_service_health"),
    descriptions=("Look up sample service health.", "Get the health of a sample service.", "Retrieve the sample health status for a named service.", "Look up a service's health in the sample data.", "Return the recorded sample health of the specified service.", "Read the sample health status associated with a service name.", "Find the named service's sample health status.", "Fetch the health value for a service from sample data.", "Get the sample status of the specified service.", "Read the recorded sample health for a service."),
    parameters=(Parameter(names=("service", "service_name")),),
    tasks=(Task(id="health", prompts=("What is the health of service {service}?", "Look up the health status for {service}.", "Check the sample health status of {service}.", "How healthy is {service} in the sample data?", "Find the recorded health for service {service}.", "Can you retrieve {service}'s sample health?", "Give me the health value for {service}.", "What status is recorded for the {service} service?", "Please read the sample health for {service}.", "Look up {service} in the service health data.", "I'd like the health status associated with {service}.", "Show the recorded sample health of service {service}."), answers=("{result}", "Health: {result}."), cases=cases),),
)
