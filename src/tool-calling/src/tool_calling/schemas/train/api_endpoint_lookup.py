from ...schema_types import Decision, Parameter, Schema, Task


ENDPOINTS = {'users': '/v1/users', 'orders': '/v1/orders', 'products': '/v1/products', 'invoices': '/v1/invoices'}


def cases(rng, count):
    for _ in range(count):
        yield {'resource': rng.choice(tuple(ENDPOINTS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(resource):
    return f'{resource}: {ENDPOINTS[resource]}'


SCHEMA = Schema(
    id='api_endpoint_lookup',
    tool_names=('lookup_api_endpoint', 'get_resource_endpoint', 'find_sample_resource_endpoint', 'read_api_registry_endpoint', 'retrieve_resource_path', 'query_sample_api_endpoint', 'resolve_resource_endpoint', 'get_registry_resource_path', 'find_endpoint_by_resource', 'lookup_sample_resource_path'),
    descriptions=('Look up a resource endpoint in the sample API registry.', 'Find the endpoint for a sample resource.', 'Return the registered sample endpoint for the named resource.', 'Retrieve a resource and its path from the sample registry.', 'Query the sample endpoint mapping by resource name.', 'Find the API path associated with a sample resource.', 'Resolve the supplied resource to its sample endpoint.', 'Read the endpoint associated with a resource in the sample registry.', 'Look up the named resource in the fixed sample endpoint table.', 'Return the sample registry entry for a resource and its endpoint.'),
    parameters=(Parameter(names=('resource', 'resource_name')),),
    tasks=(Task(id='endpoint', prompts=('What is the sample API endpoint for {resource}?', 'Look up the endpoint for the {resource} resource in the sample API.', 'Resource: {resource}. Look up its sample API endpoint?', 'Resource: {resource}. What is its endpoint in the sample API?', 'Resource: {resource}. Find the sample endpoint for this resource?', 'Resource: {resource}. Identify the resource’s sample API endpoint?', 'Resource: {resource}. Give the sample API endpoint for the resource?', 'Resource: {resource}. Retrieve the endpoint associated with this resource in the sample API?', 'Resource: {resource}. Which sample API endpoint belongs to this resource?', 'Resource: {resource}. Determine the sample endpoint for the named resource?', 'Resource: {resource}. Report the resource endpoint from the sample API?', 'Resource: {resource}. Locate the sample API endpoint for this resource?'), answers=('{result}.', '{result}.'), cases=cases),),
)
