from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        targets = rng.sample(("node-a", "node-b", "node-c", "node-d", "node-e", "node-f"), 3)
        version = rng.randint(2, 9)
        chosen = rng.randrange(3)
        rows = []
        for i, target in enumerate(targets):
            if i == chosen:
                rows.append((target, version, "healthy"))
            elif rng.choice((True, False)):
                rows.append((target, version, "unhealthy"))
            else:
                rows.append((target, version + rng.choice((-1, 1)), rng.choice(("healthy", "unhealthy"))))
        yield {"rows": rows, "version": str(version), "targets": "; ".join(f"{target}: version {v}, {health}" for target, v, health in rows)}


def prepare(*, task_id, case):
    target = next(target for target, version, health in case["rows"] if version == int(case["version"]) and health == "healthy")
    return Decision(fields=case, arguments={"target": target})


def resolve(target):
    return f"Deployment requested for target: {target}."


SCHEMA = Schema(
    id="operations_deploy_target",
    tool_names=("deploy_to_target", "request_target_deployment", "submit_target_deployment", "record_target_deployment_request", "request_deployment_for_target", "queue_target_deployment", "initiate_target_deployment_request", "create_target_deployment_request", "register_deployment_for_target", "submit_deployment_to_target"),
    descriptions=("Request a simulated deployment to a target.", "Record a deployment request for a target.", "Submit a simulated deployment request for the specified target.", "Register a deployment request using the chosen target ID.", "Request deployment to the selected target, without performing a real deployment.", "Record the selected target for a simulated deployment.", "Create a deployment request addressed to the given target.", "Submit the chosen target as a simulated deployment request.", "Register a simulated request to deploy to the specified target.", "Record a request to deploy to the target identified by ID."),
    parameters=(Parameter(names=("target", "target_id")),),
    tasks=(Task(id="deploy", prompts=("Deploy to the target that is healthy and currently runs version {version}: {targets}.", "Request deployment to the target meeting both conditions, healthy and version {version}. Targets: {targets}.", "Submit a simulated deployment request to the healthy target running version {version}: {targets}.", "From {targets}, request deployment to the healthy target currently on version {version}.", "Find the target that is both healthy and running version {version}, then request its deployment: {targets}.", "Targets: {targets}. Record a deployment request for the healthy one on version {version}.", "Please choose the healthy version {version} target in {targets} and request a simulated deployment.", "Which target in {targets} is healthy and runs version {version}? Request deployment to it.", "Register a deployment request for the target matching health=healthy and version {version}: {targets}.", "Among {targets}, deploy to the target whose current version is {version} and whose health is healthy.", "Request a simulated deployment to the healthy node running version {version} from this list: {targets}.", "Select the target with both healthy status and version {version} in {targets}, and submit a deployment request."), answers=("{result}", "{result}"), cases=cases),),
)
