from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        services = rng.sample(("api", "worker", "billing", "search", "auth", "gateway"), 3)
        chosen = rng.randrange(3)
        rows = [(service, "unhealthy" if i == chosen else rng.choice(("healthy", "degraded")), "yes" if i == chosen else rng.choice(("yes", "no"))) for i, service in enumerate(services)]
        yield {"rows": rows, "services": "; ".join(f"{service}: {health}, restart allowed={allowed}" for service, health, allowed in rows)}


def prepare(*, task_id, case):
    service = next(service for service, health, allowed in case["rows"] if health == "unhealthy" and allowed == "yes")
    return Decision(fields=case, arguments={"service": service})


def resolve(service):
    return f"Restart requested for service: {service}."


SCHEMA = Schema(
    id="operations_restart_service",
    tool_names=("restart_service", "request_service_restart", "submit_service_restart", "record_service_restart_request", "request_restart_for_service", "create_service_restart_request", "register_service_restart", "submit_restart_request", "initiate_service_restart_request", "record_restart_for_service"),
    descriptions=("Request a simulated restart for a service.", "Record a service restart request.", "Submit a simulated restart request for the specified service.", "Register a restart request using the selected service name.", "Request a service restart without actually restarting it.", "Record the chosen service for a simulated restart.", "Create a restart request for the named service.", "Submit the specified service as a simulated restart request.", "Register a simulated request to restart the selected service.", "Record a request to restart the service identified by name."),
    parameters=(Parameter(names=("service", "service_name")),),
    tasks=(Task(id="restart", prompts=("Request a restart for the service that is unhealthy and has restart allowed=yes: {services}.", "Restart the service meeting both conditions: unhealthy and restart allowed=yes. Services: {services}.", "Submit a simulated restart request for the unhealthy service with restart allowed=yes: {services}.", "From {services}, request a restart of the service that is unhealthy and allowed to restart.", "Which service is unhealthy with restart allowed=yes? Request its restart: {services}.", "Record a restart request for the service satisfying both unhealthy and restart allowed=yes: {services}.", "Please request a simulated restart for the eligible unhealthy service in this list: {services}. Eligibility means restart allowed=yes.", "Among these services, select the unhealthy one whose restart is allowed and request its restart: {services}.", "Services: {services}. Submit a restart request only for the unhealthy service marked restart allowed=yes.", "Find the service with unhealthy health and restart allowed=yes in {services}, then request its restart.", "For {services}, register a simulated restart of the service that is unhealthy and permitted to restart.", "Request a restart for whichever service in {services} is both unhealthy and marked restart allowed=yes."), answers=("{result}", "{result}"), cases=cases),),
)
