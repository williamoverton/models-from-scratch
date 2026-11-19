from ...schema_types import Decision, Parameter, Schema, Task

DESTINATIONS = {
    "P100": "Oslo", "P101": "Lima", "P102": "Kyoto", "P103": "Accra",
    "P104": "Perth", "P105": "Riga", "P106": "Quito", "P107": "Dublin",
}


def cases(rng, count):
    for _ in range(count):
        shipment = rng.choice(tuple(DESTINATIONS))
        yield {"shipment": shipment}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={"shipment": case["shipment"]})


SCHEMA = Schema(
    id="parcel_destination_lookup",
    tool_names=("lookup_shipment_destination", "show_parcel_destination", "find_shipment_destination", "get_parcel_destination", "retrieve_shipment_destination", "query_parcel_destination", "identify_shipment_destination", "get_shipment_city", "find_parcel_destination", "read_shipment_destination"),
    descriptions=("Look up a shipment's destination in the shipment records.", "Show the destination associated with a shipment identifier.", "Find the recorded destination for a shipment ID.", "Retrieve the destination city assigned to a shipment.", "Identify where a shipment is going from its record.", "Query shipment records for the destination of a parcel.", "Return the destination associated with the given shipment.", "Read the destination city for a shipment identifier.", "Find a parcel's recorded destination using its shipment ID.", "Get the shipment's destination from the shipment records."),
    parameters=(Parameter(names=("shipment", "shipment_id")),),
    tasks=(Task(id="lookup", prompts=("What is the destination of shipment {shipment}?", "Look up where shipment {shipment} is going.", "Find the recorded destination for shipment {shipment}.", "Which city is shipment {shipment} destined for?", "Check the shipment records for {shipment}'s destination.", "Where is parcel shipment {shipment} headed?", "Retrieve the destination associated with shipment ID {shipment}.", "Identify the destination city recorded for {shipment}.", "Show me where shipment {shipment} is going.", "Consult the shipment records: destination of {shipment}?", "What destination is assigned to shipment {shipment}?", "Read the destination for parcel {shipment} from its shipment record."), answers=("{result}", "{result}"), cases=cases),),
)


def resolve(shipment):
    return f"Shipment {shipment} is destined for {DESTINATIONS[shipment]}."
