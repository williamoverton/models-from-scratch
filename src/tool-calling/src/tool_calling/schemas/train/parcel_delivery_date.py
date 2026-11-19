from datetime import date, timedelta

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        dispatch = date(2026, 1, 1) + timedelta(days=rng.randrange(365))
        yield {"dispatch": dispatch.isoformat(), "days": str(rng.randrange(1, 31))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


SCHEMA = Schema(
    id="parcel_delivery_estimate",
    tool_names=("estimate_delivery_date", "add_transit_days", "calculate_parcel_arrival", "compute_delivery_date", "project_shipment_arrival", "find_delivery_date", "calculate_transit_arrival", "estimate_parcel_delivery", "add_calendar_transit_days", "determine_arrival_date"),
    descriptions=("Calculate delivery date by adding calendar days to dispatch.", "Estimate arrival from a dispatch date and calendar-day transit duration.", "Add the transit duration in calendar days to the dispatch date.", "Compute the estimated delivery date from dispatch and transit days.", "Determine parcel arrival by adding calendar days to dispatch.", "Project a shipment's delivery date using its calendar-day transit time.", "Find the estimated arrival date after the specified transit days.", "Calculate when delivery is expected by counting calendar days from dispatch.", "Estimate the parcel's arrival from its dispatch date and transit duration.", "Return the dispatch date plus the given number of calendar days."),
    parameters=(Parameter(names=("dispatch", "dispatch_date")), Parameter(names=("days", "transit_days"))),
    tasks=(Task(id="estimate", prompts=("Dispatch is {dispatch} and transit takes {days} calendar days. What is the estimated delivery date?", "Add {days} calendar days to dispatch date {dispatch} to estimate arrival.", "When should a parcel dispatched {dispatch} arrive after {days} calendar days?", "Estimate delivery by adding {days} calendar days to {dispatch}.", "A shipment leaves on {dispatch}; its transit is {days} calendar days. Find the arrival date.", "What date is {days} calendar days after dispatch on {dispatch}?", "Project the delivery date for a {dispatch} dispatch with {days} calendar days in transit.", "Count {days} calendar days from {dispatch} to estimate the parcel's delivery.", "The dispatch date is {dispatch}, with a {days}-calendar-day transit. When is delivery estimated?", "Calculate arrival for dispatch {dispatch} and transit of {days} calendar days.", "For a parcel sent {dispatch}, add {days} calendar days to find estimated delivery.", "Give the estimated delivery date: dispatch {dispatch}, transit {days} calendar days."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(dispatch, days):
    arrival = date.fromisoformat(dispatch) + timedelta(days=int(days))
    return f"Estimated delivery: {arrival.isoformat()}."
