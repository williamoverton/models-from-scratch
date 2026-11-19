from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"homework": str(rng.randint(40, 100)), "exam": str(rng.randint(40, 100)), "homework_weight": str(rng.choice((20, 30, 40, 50, 60)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(homework, exam, homework_weight):
    weight = Decimal(homework_weight)
    grade = (Decimal(homework) * weight + Decimal(exam) * (100 - weight)) / 100
    return f"{grade:.2f}"


SCHEMA = Schema(
    id="education_weighted_grade",
    tool_names=('calculate_weighted_grade', 'compute_course_grade', 'compute_weighted_grade', 'calculate_course_grade', 'weighted_homework_exam_grade', 'compute_grade_from_weights', 'calculate_final_weighted_grade', 'derive_course_grade', 'calculate_homework_exam_grade', 'get_weighted_course_grade'),
    descriptions=('Calculate the weighted grade from homework, exam, and homework weight percentages.', 'Compute a weighted course grade using the exam for the remaining weight.', 'Compute the weighted grade with the exam taking the remaining weight.', 'Calculate the course grade from homework, exam, and homework weight percentages.', 'Weight homework by its percentage and the exam by the remaining percentage.', 'Compute the weighted grade from homework, exam, and homework weight.', 'Calculate the grade using the exam for the weight not assigned to homework.', 'Derive a weighted course grade from both scores and homework percentage.', 'Calculate a homework and exam grade with the exam receiving the remaining weight.', 'Get the weighted grade using homework weight and its complement for the exam.'),
    parameters=(Parameter(names=("homework", "homework_score")), Parameter(names=("exam", "exam_score")), Parameter(names=("homework_weight", "homework_percent"))),
    tasks=(Task(id="grade", prompts=("Homework is {homework}% and exam is {exam}%. Homework counts {homework_weight}% and the exam counts the rest. Calculate the weighted grade to two decimals.", "With homework at {homework}% and the exam at {exam}%, weight homework {homework_weight}% and the exam the remainder. Give the grade to two decimals.", "Find the two-decimal course grade for homework {homework}% and exam {exam}% when homework is worth {homework_weight}% and the exam is worth the rest.", "The homework score is {homework}%, the exam score is {exam}%, and homework's weight is {homework_weight}%. The exam gets the remaining weight. Calculate the grade to two decimals.", "Calculate the weighted percentage, rounded to two decimals: homework {homework}% at {homework_weight}%, exam {exam}% at the remaining weight.", "A student earned {homework}% on homework and {exam}% on the exam. Homework is {homework_weight}% of the grade and the exam is the rest. What is the grade to two decimals?", "Use {homework_weight}% for homework scored {homework}% and the balance for an exam scored {exam}%. Report the weighted grade to two decimal places.", "What is the final weighted grade to two decimals if homework is {homework}%, the exam is {exam}%, homework counts {homework_weight}%, and the exam counts the rest?", "Combine a {homework}% homework score with a {exam}% exam score using a {homework_weight}% homework weight and the remaining exam weight. Give two decimals.", "Homework: {homework}%; exam: {exam}%; homework weight: {homework_weight}%. The exam has the remaining weight. Calculate the grade to two decimals.", "Determine the weighted grade to two decimal places from {homework}% homework, {exam}% exam, and {homework_weight}% homework weight; assign the rest to the exam."), answers=("The weighted grade is {result}%.",), cases=cases),),
)
