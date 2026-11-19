from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        capacity = rng.randint(20, 500)
        yield {"capacity": capacity, "reserved": rng.randint(0, capacity)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(capacity, reserved):
    return f"{int(capacity) - int(reserved)} seats"


SCHEMA = Schema(
    id="events_seat_availability",
    tool_names=("calculate_available_seats", "remaining_event_seats", "compute_unreserved_seats", "subtract_reserved_seats", "find_venue_seat_availability", "count_remaining_seats", "calculate_open_seats", "determine_seats_available", "compute_venue_seat_remainder", "find_unreserved_capacity"),
    descriptions=("Subtract reserved seats from capacity.", "Calculate the number of unreserved seats.", "Find available seats as total capacity minus reservations.", "Compute how many venue seats remain unreserved.", "Subtract the reserved count from the total seat count.", "Determine the remaining seats from capacity and reserved seats.", "Calculate open seats by removing reservations from capacity.", "Find the difference between total seats and reserved seats.", "Count available seats using capacity less reserved seats.", "Compute the unreserved portion of venue seating."),
    parameters=(Parameter(names=("capacity", "total_seats")), Parameter(names=("reserved", "reserved_seats"))),
    tasks=(Task(id="availability", prompts=("A venue has {capacity} seats, of which {reserved} are reserved. How many are available?", "Calculate available seats as {capacity} total minus {reserved} reserved.", "Of {capacity} venue seats, {reserved} are reserved. How many remain unreserved?", "Find open seats when capacity is {capacity} and {reserved} seats are reserved.", "The venue holds {capacity} people and has {reserved} reserved seats. Calculate the available seats.", "Subtract {reserved} reserved seats from the venue's {capacity} seats. How many are left?", "How many seats are available out of {capacity} if {reserved} are already reserved?", "There are {capacity} seats in total and {reserved} reservations. Determine the unreserved seat count.", "Compute remaining venue capacity in seats: {capacity} total, {reserved} reserved.", "With {reserved} of {capacity} seats reserved, how many seats are still available?", "A venue has capacity for {capacity} seats; {reserved} are reserved. Find the number of open seats.", "What is the number of unreserved seats if the total is {capacity} and the reserved count is {reserved}?"), answers=("Available: {result}.", "{result} available."), cases=cases),),
)
