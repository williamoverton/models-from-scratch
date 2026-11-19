from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        sent = rng.choice((100, 200, 500, 1000))
        received = rng.randint(0, sent)
        yield {"sent": str(sent), "received": str(received)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(sent, received):
    loss = (Decimal(sent) - Decimal(received)) * 100 / Decimal(sent)
    return f"{loss:.1f}%"


SCHEMA = Schema(
    id="network_packet_loss_percentage",
    tool_names=("calculate_packet_loss", "compute_packet_loss_percent", "calculate_lost_packet_percentage", "determine_packet_loss_rate", "compute_network_loss_percentage", "calculate_loss_from_counts", "find_packet_loss_percent", "derive_packet_loss_rate", "compute_lost_traffic_percentage", "calculate_packet_loss_ratio"),
    descriptions=("Calculate packet loss percentage to one decimal place.", "Compute lost packets as a percentage of packets sent.", "Calculate (sent minus received) divided by sent as a percentage to one decimal place.", "Determine the percentage of sent packets that did not arrive, to one decimal.", "Compute packet loss from sent and received counts and format it to one decimal place.", "Find the lost share of sent packets as a percentage rounded to one decimal.", "Calculate the difference between sent and received packets as a percentage of sent.", "Express packet loss relative to packets sent with one decimal place.", "Use sent and received packet counts to calculate the lost percentage.", "Return the packet loss percentage from the sent and received counts to one decimal."),
    parameters=(Parameter(names=("sent", "packets_sent")), Parameter(names=("received", "packets_received"))),
    tasks=(Task(id="loss", prompts=("Of {sent} packets sent, {received} arrived. Calculate packet loss as (sent - received) / sent × 100, to one decimal place.", "Calculate the lost percentage for {sent} sent and {received} received packets: (sent - received) / sent × 100, one decimal place.", "A total of {sent} packets were sent and {received} received. What percentage was lost? Use (sent - received) / sent × 100 and one decimal place.", "Find packet loss for {sent} sent and {received} received, calculating (sent - received) / sent × 100 to one decimal place.", "With {sent} packets transmitted and {received} arriving, express loss as (sent - received) / sent × 100, to one decimal place.", "What is the packet loss percentage if {sent} were sent and {received} received? Compute (sent - received) / sent × 100 to one decimal.", "For {sent} sent packets and {received} received packets, calculate (sent - received) / sent × 100 and give the loss to one decimal place.", "Determine the percentage lost when {sent} packets are sent and {received} arrive. Use (sent - received) / sent × 100, one decimal place.", "Out of {sent} packets sent, {received} were received. Report loss to one decimal using (sent - received) / sent × 100.", "Compute the loss rate for {sent} sent and {received} received packets as (sent - received) / sent × 100, rounded to one decimal place.", "How much packet loss occurred with {sent} sent and {received} received? Give (sent - received) / sent × 100 to one decimal place.", "Using (sent - received) / sent × 100, calculate the packet loss percentage to one decimal for {sent} sent and {received} received."), answers=("Packet loss: {result}.", "Loss is {result}."), cases=cases),),
)
