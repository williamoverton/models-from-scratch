from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    first = date(2020, 1, 1)
    for _ in range(count):
        day = first + timedelta(days=rng.randrange(3652))
        yield {"reading_date": day.isoformat(), "start_day": str(rng.randrange(1, 29))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(reading_date, start_day):
    day = date.fromisoformat(reading_date)
    start = int(start_day)
    year, month = day.year, day.month
    if day.day < start:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
    period_start = date(year, month, start)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
    period_end = date(next_year, next_month, start) - timedelta(days=1)
    return f"{period_start.isoformat()} through {period_end.isoformat()}"


SCHEMA = Schema(
    id="energy_billing_period_for_date",
    tool_names=('find_billing_period', 'calculate_billing_cycle', 'billing_period_for_date', 'get_billing_cycle_dates', 'compute_billing_period', 'monthly_billing_period', 'date_billing_cycle', 'find_cycle_containing_date', 'calculate_cycle_bounds', 'get_period_for_reading'),
    descriptions=('Find the inclusive monthly billing period containing a date, starting on the given day each month.', 'Compute a monthly cycle’s inclusive start and end for a reading date.', 'Return the monthly billing cycle containing the reading date for a start day from 1 to 28.', 'Calculate inclusive cycle boundaries for a date and monthly start day from 1 through 28.', 'Find the start and end of the billing period containing a reading date, given a monthly start day.', 'Determine the inclusive monthly billing interval for a date using the specified start day.', 'Compute the cycle containing a reading date, ending the day before the next monthly start.', 'Return the inclusive dates of the monthly cycle containing a reading date.', 'Calculate the billing interval containing a reading date using a recurring monthly start day.', 'Get the inclusive monthly cycle boundaries for a reading date and start day.'),
    parameters=(Parameter(names=("reading_date", "date")), Parameter(names=("start_day", "cycle_start_day"))),
    tasks=(Task(id="period", prompts=("For the date {reading_date}, find the inclusive monthly billing period when each cycle begins on day {start_day} and ends the day before the next start.", "A billing cycle starts on day {start_day} of every month. What inclusive start and end contain {reading_date}?", 'Find the inclusive billing-cycle start and end containing {reading_date}; cycles start on day {start_day} each month and end the day before the next start.', 'Monthly cycles begin on day {start_day} and end the day before the next start. Which inclusive period contains {reading_date}?', 'For reading date {reading_date}, calculate the inclusive monthly cycle bounds when the start day is {start_day}.', 'Give the inclusive start and end of the monthly billing period covering {reading_date}, with each cycle starting on day {start_day}.', 'A cycle runs from day {start_day} each month through the day before the next start. Find the inclusive period for {reading_date}.', 'What are the inclusive billing dates surrounding {reading_date} if each monthly cycle starts on day {start_day}?', 'Determine the monthly billing interval containing {reading_date}, inclusive at both ends, starting on day {start_day}.', 'Given a monthly cycle start day of {start_day}, return inclusive period boundaries for {reading_date}.', 'The reading is dated {reading_date}; identify its inclusive monthly billing period with start day {start_day}.', 'Which inclusive start and end dates bound {reading_date} when billing cycles begin on day {start_day} every month?'), answers=("The billing period is {result}.", "The date falls in {result}."), cases=cases),),
)
