from ...schema_types import Decision, Parameter, Schema, Task


VERSIONS = {'billing': 'v2', 'catalog': 'v3', 'identity': 'v1', 'shipping': 'v2'}


def cases(rng, count):
    for _ in range(count):
        yield {'service': rng.choice(tuple(VERSIONS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(service):
    return f'{service}: {VERSIONS[service]}'


SCHEMA = Schema(
    id='api_version_lookup',
    tool_names=('lookup_api_version', 'get_service_api_version', 'find_sample_service_version', 'read_api_registry_version', 'retrieve_service_version', 'query_sample_api_version', 'resolve_service_api_version', 'get_registry_service_version', 'find_api_version_by_service', 'lookup_sample_service_version'),
    descriptions=('Look up a service version in the sample API registry.', 'Find the sample API version for a service.', 'Return the registered sample API version for the named service.', 'Retrieve a service and its version from the sample registry.', 'Query the sample version mapping by service name.', 'Find which API version a sample service uses.', 'Resolve the supplied service to its sample API version.', 'Read the version associated with a service in the sample registry.', 'Look up the named service in the fixed sample version table.', 'Return the sample registry entry for a service and its API version.'),
    parameters=(Parameter(names=('service', 'service_name')),),
    tasks=(Task(id='version', prompts=('What API version does the sample {service} service use?', 'Look up the sample API version for {service}.', 'Service: {service}. Look up its sample API version?', 'Service: {service}. What API version does this sample service use?', 'Service: {service}. Find the sample API version for this service?', 'Service: {service}. Identify the service’s sample API version?', 'Service: {service}. Give the API version used by the sample service?', 'Service: {service}. Retrieve the sample version associated with this service?', 'Service: {service}. Which API version belongs to this sample service?', 'Service: {service}. Determine the sample API version for the named service?', 'Service: {service}. Report the sample service’s API version?', 'Service: {service}. Locate the API version for this sample service?'), answers=('{result}.', '{result}.'), cases=cases),),
)
