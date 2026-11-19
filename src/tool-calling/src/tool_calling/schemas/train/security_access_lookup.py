from ...schema_types import Decision, Parameter, Schema, Task


ACCESS = {
    "vault": {"Ari": "read", "Bea": "none", "Cal": "write"},
    "portal": {"Ari": "write", "Bea": "read", "Cal": "none"},
    "reports": {"Ari": "none", "Bea": "write", "Cal": "read"},
}


def cases(rng, count):
    for _ in range(count):
        yield {"user": rng.choice(("Ari", "Bea", "Cal")), "resource": rng.choice(tuple(ACCESS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(user, resource):
    return f"{user} on {resource}: {ACCESS[resource][user]}"


SCHEMA = Schema(
    id="security_access_lookup",
    tool_names=("get_resource_access", "lookup_user_access", "check_resource_access", "retrieve_user_access", "find_user_resource_access", "get_user_access_level", "lookup_resource_permission", "read_sample_access", "get_access_for_user", "find_resource_access_level"),
    descriptions=("Look up sample resource access.", "Retrieve a user's sample access level.", "Find a user's access to a sample resource.", "Check the sample registry for a user's resource access.", "Get the registered access level for a user and resource.", "Look up a user-resource pair in the sample registry.", "Read a user's access level for a resource.", "Retrieve resource access for the specified user.", "Find the sample access entry for a user and resource.", "Return the registered access level for a resource user."),
    parameters=(Parameter(names=("user", "user_name")), Parameter(names=("resource", "resource_id"))),
    tasks=(Task(id="access", prompts=("What access does {user} have to {resource} in the sample access registry?", "Look up {user}'s access to {resource} in the sample registry.", "Check the sample registry: what is {user}'s access level for {resource}?", "Find the registered permission for {user} on {resource}.", "Retrieve {user}'s sample access level to {resource}.", "In the sample access registry, check {resource} for user {user}.", "For user {user} and resource {resource}, return the sample access level.", "Which access level is recorded for {user} on {resource} in the sample registry?", "Consult the sample registry for {user}'s permission on {resource}.", "Read the sample access entry for {resource} and {user}.", "Give the registered access for {user} to {resource} from the sample registry.", "Use the sample access registry to determine {user}'s access to {resource}."), answers=("{result}.", "{result}."), cases=cases),),
)
