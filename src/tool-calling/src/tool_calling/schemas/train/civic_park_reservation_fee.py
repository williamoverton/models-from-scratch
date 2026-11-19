from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        yield {"hours": str(rng.randint(1, 8)), "rate": str(rng.choice((10, 15, 20, 25))), "deposit": str(rng.choice((20, 30, 50)))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(hours, rate, deposit):
    total = Decimal(hours) * Decimal(rate) + Decimal(deposit)
    return f"${total:.2f}"


SCHEMA = Schema(
    id="civic_park_reservation_fee",
    tool_names=("calculate_park_reservation_total", "calculate_reservation_fee", "compute_park_booking_upfront", "sum_reservation_rate_and_deposit", "find_park_reservation_charge", "calculate_park_booking_total", "compute_reservation_upfront_total", "determine_park_booking_payment", "calculate_hourly_reservation_total", "compute_park_fee_with_deposit"),
    descriptions=("Calculate the upfront reservation total as hours times hourly rate plus deposit.", "Calculate park reservation charges including the deposit.", "Multiply reservation hours by the hourly rate and add the deposit.", "Find the upfront park booking payment including the refundable deposit.", "Compute the reservation charge plus the specified deposit.", "Determine the total due upfront from hours, rate, and deposit.", "Calculate park reservation cost as hourly charges plus deposit.", "Add the deposit to the product of reservation hours and rate.", "Return the upfront reservation total including the deposit.", "Compute the amount payable for the park reservation and deposit."),
    parameters=(Parameter(names=("hours", "reservation_hours")), Parameter(names=("rate", "hourly_rate")), Parameter(names=("deposit", "deposit_amount"))),
    tasks=(Task(id="fee", prompts=('A park reservation costs ${rate} per hour for {hours} hours plus a ${deposit} refundable deposit. What is the upfront total?', 'Calculate the upfront total for {hours} hours at ${rate}/hour plus a ${deposit} deposit; no other charges apply.', 'How much must be paid initially for a {hours}-hour park booking at ${rate} per hour if a ${deposit} refundable deposit is also due?', 'Add the ${deposit} deposit to the charge for {hours} hours at ${rate} an hour. Give the park reservation total due upfront.', 'A park charges ${rate} hourly and collects a refundable ${deposit} deposit. Work out the upfront payment for {hours} hours.', 'For {hours} hours of park use, the hourly rate is ${rate}; the deposit is ${deposit}. What is the combined amount payable upfront?', 'Compute the initial park booking payment: multiply {hours} hours by ${rate} per hour, then include the ${deposit} deposit.', 'The refundable deposit is ${deposit}, and the park rental lasts {hours} hours at ${rate} per hour. State the total due before the reservation.', 'An applicant reserves a park for {hours} hours. At ${rate}/hour with a ${deposit} deposit added, what is the upfront total?', 'Find the amount collected at booking when the park charges ${rate} for each of {hours} hours plus a refundable ${deposit} deposit.', 'Calculate hours times rate plus deposit for a park reservation: rate ${rate} per hour, deposit ${deposit}, duration {hours} hours. Return the upfront total.', 'What initial payment covers a ${deposit} refundable deposit and {hours} hours of park rental at ${rate} hourly?', 'A ${deposit} deposit accompanies the hourly charges for a {hours}-hour park reservation at ${rate} per hour. Determine the total due upfront.', 'The park booking requires payment for {hours} hours at ${rate}/hour as well as a ${deposit} refundable deposit. How much is due upfront?'), answers=("The upfront total is {result}.", "Pay {result} upfront."), cases=cases),)
)
