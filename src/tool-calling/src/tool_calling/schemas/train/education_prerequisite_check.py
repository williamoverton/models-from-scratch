from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    courses = ("Algebra", "Biology", "Chemistry", "History", "Physics", "Statistics")
    for _ in range(count):
        required = rng.sample(courses, 2)
        completed = rng.sample(courses, rng.randint(1, 5))
        yield {"required": ", ".join(required), "completed": ", ".join(completed)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(required, completed):
    missing = set(required.split(", ")) - set(completed.split(", "))
    return "eligible" if not missing else "not eligible"


SCHEMA = Schema(
    id="education_prerequisite_check",
    tool_names=('check_prerequisites', 'check_course_eligibility', 'verify_prerequisites', 'determine_course_eligibility', 'assess_prerequisite_completion', 'evaluate_course_eligibility', 'compare_required_courses', 'check_required_courses', 'verify_course_requirements', 'assess_course_prerequisites'),
    descriptions=('Check whether every required course is among the completed courses.', 'Determine eligibility from required and completed course lists.', 'Check that all required courses are completed.', 'Determine eligibility by whether every required course is completed.', 'Assess whether completed courses include every required course.', 'Evaluate eligibility from the required and completed course lists.', 'Compare required courses with completed courses for eligibility.', 'Check whether each required course appears in the completed list.', 'Verify that all course requirements are in the completed list.', 'Assess prerequisite eligibility using required and completed courses.'),
    parameters=(Parameter(names=("required", "required_courses")), Parameter(names=("completed", "completed_courses"))),
    tasks=(Task(id="check", prompts=("Required courses: {required}. Completed courses: {completed}. Is the student eligible? Eligibility requires completing every required course.", "A student completed {completed}; the requirements are {required}. Is the student eligible if every required course must be completed?", "Check eligibility: prerequisites are {required}, and completed courses are {completed}. All required courses must be complete.", "Does {completed} satisfy all required courses {required}? A student is eligible only after completing every requirement.", "Determine whether the student is eligible. They completed {completed} and must have completed every course in {required}.", "The course requires {required}; the student has taken {completed}. Eligibility means all required courses are completed. Are they eligible?", "Compare required courses {required} against completed courses {completed}. Is every requirement met for eligibility?", "For eligibility, all prerequisites must be completed. Required: {required}. Completed: {completed}. Is the student eligible?", "Has the student completed every required course in {required}, given the completed list {completed}? Report eligibility.", "A student needs all of {required} and has completed {completed}. Determine whether they are eligible.", "Evaluate course eligibility for completed courses {completed} and required courses {required}, requiring every listed prerequisite."), answers=("The student is {result}.",), cases=cases),),
)
