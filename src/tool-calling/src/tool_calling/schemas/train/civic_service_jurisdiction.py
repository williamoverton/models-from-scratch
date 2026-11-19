from ...schema_types import Decision, Parameter, Schema, Task


DEPARTMENTS = {"pothole": "Public Works", "missed waste collection": "Sanitation", "broken park bench": "Parks", "noise complaint": "Code Enforcement"}


def cases(rng, count):
    for _ in range(count):
        yield {"category": rng.choice(tuple(DEPARTMENTS))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(category):
    return DEPARTMENTS[category]


SCHEMA = Schema(
    id="civic_service_jurisdiction",
    tool_names=("lookup_service_department", "identify_responsible_department", "find_civic_service_department", "route_sample_service_category", "get_department_for_service", "lookup_civic_category_owner", "resolve_service_jurisdiction", "find_service_routing_department", "query_sample_service_routing", "identify_service_category_department"),
    descriptions=("Look up the department responsible for a service category in the sample routing table.", "Identify the department handling a service category.", "Find the department assigned to the category in the sample routing table.", "Resolve a civic service category to its sample department.", "Return the responsible department for the given sample service category.", "Query the fixed civic service routing table by category.", "Identify which sample department handles the specified service issue.", "Retrieve the department mapped to a civic service category.", "Find the category's department using the sample jurisdiction mapping.", "Look up the assigned department in the sample service routing."),
    parameters=(Parameter(names=("category", "service_category")),),
    tasks=(Task(id="department", prompts=('Service routing: pothole=Public Works; missed waste collection=Sanitation; broken park bench=Parks; noise complaint=Code Enforcement. Which department handles {category}?', 'Using the routing table pothole: Public Works, missed waste collection: Sanitation, broken park bench: Parks, noise complaint: Code Enforcement, find the department for {category}.', 'Who should receive a {category} report? The sample assigns potholes to Public Works, missed waste collection to Sanitation, broken park benches to Parks, and noise complaints to Code Enforcement.', 'For {category}, name the responsible department from this mapping: Public Works handles pothole; Sanitation handles missed waste collection; Parks handles broken park bench; Code Enforcement handles noise complaint.', 'A resident reports {category}. Route it using pothole → Public Works, missed waste collection → Sanitation, broken park bench → Parks, and noise complaint → Code Enforcement.', 'In the sample, Parks owns broken park bench and Code Enforcement owns noise complaint; pothole belongs to Public Works and missed waste collection to Sanitation. Identify the owner of {category}.', 'Consult this service directory to answer for {category}: pothole/Public Works, missed waste collection/Sanitation, broken park bench/Parks, noise complaint/Code Enforcement. Which department?', 'The issue is {category}. The routing assignments are Public Works for pothole, Sanitation for missed waste collection, Parks for broken park bench, and Code Enforcement for noise complaint. Return its department.', 'Determine the destination for {category} using the following category-to-department pairs: noise complaint—Code Enforcement; broken park bench—Parks; missed waste collection—Sanitation; pothole—Public Works.', 'If the category is {category}, which department is assigned? Sample rules: pothole is Public Works, missed waste collection is Sanitation, broken park bench is Parks, noise complaint is Code Enforcement.', 'Department lookup requested for {category}: Code Enforcement takes noise complaint, Parks takes broken park bench, Sanitation takes missed waste collection, and Public Works takes pothole. Give the matching department.', 'Given the sample service assignments of pothole to Public Works, missed waste collection to Sanitation, broken park bench to Parks, and noise complaint to Code Enforcement, where should {category} be routed?', 'Match {category} to its department: Public Works (pothole), Sanitation (missed waste collection), Parks (broken park bench), Code Enforcement (noise complaint).', 'Our sample routing table lists noise complaint under Code Enforcement, pothole under Public Works, broken park bench under Parks, and missed waste collection under Sanitation. Which entry owns {category}?'), answers=("The department is {result}.", "Responsible department: {result}."), cases=cases),)
)
