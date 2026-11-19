from ...schema_types import Decision, Parameter, Schema, Task


PORTS = {"http": "80/tcp", "https": "443/tcp", "ssh": "22/tcp", "dns": "53/udp"}


def cases(rng, count):
    for _ in range(count):
        yield {"service": rng.choice(tuple(PORTS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"service": case["service"]})


def resolve(service):
    return f"{service}: {PORTS[service]}"


SCHEMA = Schema(
    id="network_service_port_lookup",
    tool_names=("lookup_sample_service_port", "get_sample_service_port", "find_sample_service_port", "retrieve_sample_service_transport", "lookup_catalog_service_port", "get_catalog_port_and_transport", "query_sample_service_port", "find_sample_port_and_protocol", "retrieve_catalog_service_port", "lookup_sample_port_and_transport"),
    descriptions=("Look up a service port in the sample catalog.", "Get the sample port and transport for a service.", "Retrieve a service's port and transport from the sample catalog.", "Find the cataloged port and transport for the named sample service.", "Query the sample service catalog for the specified service's port and transport.", "Return the sample catalog's port and transport for a service name.", "Look up the named service in the sample port and transport catalog.", "Get the port and transport associated with a service in the sample catalog.", "Retrieve the sample catalog entry for a service's port and transport.", "Find the sample service's cataloged port number and transport."),
    parameters=(Parameter(names=("service", "service_name")),),
    tasks=(Task(id="port", prompts=("Look up the port and transport for {service} in the sample service catalog.", "What port and transport does the sample catalog list for {service}?", "In the sample catalog, find the port number and transport used by {service}.", "Which port and transport are recorded for {service} in the sample service catalog?", "Give me the sample catalog's port and transport entry for {service}.", "For {service}, retrieve its port and transport from the sample catalog.", "What does the sample catalog say the port and transport for {service} are?", "Find the sample service catalog entry identifying {service}'s port and transport.", "According to the sample service catalog, which transport and port correspond to {service}?", "Report the cataloged transport and port for {service} using the sample catalog.", "I need the port together with the transport for {service} from the sample catalog.", "Consult the sample service catalog and return the port and transport associated with {service}."), answers=("{result}.", "Port: {result}."), cases=cases),),
)
