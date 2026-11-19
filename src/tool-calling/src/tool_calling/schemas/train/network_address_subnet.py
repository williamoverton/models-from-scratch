from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        a, b, c = rng.randint(1, 223), rng.randint(0, 255), rng.randint(0, 254)
        ids = rng.sample(range(100, 999), 3)
        octets = [c, c + 1, (c + 2) % 256]
        rng.shuffle(octets)
        entries = list(zip(ids, octets))
        rng.shuffle(entries)
        yield {"subnet": f"{a}.{b}.{c}.0/24", "addresses": "; ".join(f"A-{i}={a}.{b}.{octet}.{rng.randint(1, 254)}" for i, octet in entries)}


def prepare(*, task_id, case):
    prefix = case["subnet"].split(".")[:3]
    entries = [entry.strip().split("=") for entry in case["addresses"].split(";")]
    address = next(identifier for identifier, ip in entries if ip.split(".")[:3] == prefix)
    return Decision(fields=case, arguments={"address": address})


def resolve(address):
    return f"Selected address {address}"


SCHEMA = Schema(
    id="network_address_in_subnet",
    tool_names=("select_subnet_address", "report_subnet_address", "record_selected_address_id", "report_selected_address_id", "record_subnet_address_selection", "report_address_identifier", "record_address_identifier", "report_chosen_subnet_address", "record_chosen_address_id", "return_selected_address_id"),
    descriptions=("Report the selected address ID.", "Record the selected address identifier.", "Return the identifier of the selected address.", "Report the chosen address by its ID.", "Record the selected address ID without changing network configuration.", "Return the supplied address identifier as the selection.", "Report an address selection using its identifier.", "Record the ID of the address selected for the subnet.", "Return the selected address ID, not the IPv4 address.", "Report the supplied identifier as the selected address."),
    parameters=(Parameter(names=("address", "address_id")),),
    tasks=(Task(id="subnet", prompts=("Select the address in {subnet} from {addresses}. Entries are ID=IPv4 address; for /24, membership means matching the first three octets.", "Which ID in {addresses} belongs to {subnet}? For this /24 subnet, match the first three IPv4 octets; entries are ID=address.", "Find the address ID in {addresses} that belongs to {subnet}. Entries are ID=IPv4 address, and /24 membership requires matching the first three octets.", "From {addresses} (ID=IPv4 address), select the ID in {subnet} by matching the first three octets of this /24 subnet.", "Which address identifier matches {subnet}? Check {addresses}, where entries are ID=IPv4 address and /24 membership means the first three octets match.", "For {subnet}, pick the matching ID from {addresses}. Each entry is ID=IPv4 address; compare the first three octets for this /24.", "Identify the ID of the IPv4 address in {subnet} among {addresses}. Entries use ID=IPv4 address, and /24 means matching the first three octets.", "Using the first three octets to determine /24 membership, select the ID in {subnet} from {addresses}, formatted ID=IPv4 address.", "Look at {addresses}, listed as ID=IPv4 address. Which ID belongs to {subnet}, matching its first three octets for /24?", "Choose the address identifier whose IPv4 address is in {subnet} from {addresses}; entries are ID=IPv4 address and /24 requires the first three octets to match.", "Report the ID in {addresses} that matches the first three octets of the /24 subnet {subnet}; entries are ID=IPv4 address.", "Among the ID=IPv4 address entries {addresses}, find the one in {subnet}, using the first three octets to check /24 membership."), answers=("{result}.", "{result}."), cases=cases),),
)
