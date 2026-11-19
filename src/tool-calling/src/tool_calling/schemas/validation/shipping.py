from ...schema_types import Decision, Schema, Parameter, Task, InvalidCombination


def cases(rng, count):
    for _ in range(count):
        yield {
            "size": rng.choice(("small", "medium", "large", "extra-small", "extra-large", "oversized")),
            "service": rng.choice(("standard", "express", "economy", "priority", "overnight")),
        }


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)

SCHEMA = Schema(
    id="shipping_quote",
    tool_names=('shipping_quote', 'quote_delivery', 'calculate_sample_shipping_fee', 'get_sample_delivery_quote', 'lookup_shipping_fee', 'sample_shipping_quote', 'compute_delivery_fee', 'quote_package_shipping', 'get_shipping_rate', 'calculate_package_delivery_cost'),
    descriptions=('Quote the fixed sample delivery fee for a package size and service; express is unavailable for large packages.', 'Look up a sample shipping fee by size and speed, excluding large express packages.', 'Calculate the sample package delivery fee from size and service; large express is unavailable.', 'Return a sample shipping price for a package size and service, except large express.', 'Find the fixed sample fee for a size and delivery service; large express is invalid.', 'Compute the sample shipping quote for the given size and service, excluding large express.', 'Get the sample delivery charge for a package and service; express cannot be used for large packages.', 'Quote the sample shipping price by package size and service, with large express unavailable.', 'Calculate the sample fee for a size and speed, rejecting large express delivery.', 'Return the fixed sample delivery cost for a size and service other than large express.'),
    parameters=(
        Parameter(names=("size", "package_size")),
        Parameter(names=("service", "speed")),
    ),
    tasks=(
        Task(id="quote", prompts=("What is the {service} shipping fee for a {size} package?", "Quote {service} delivery for a {size} parcel.", 'Find the sample {service} delivery fee for a {size} package.', 'How much is sample shipping for a {size} parcel by {service}?', 'Calculate the sample {service} shipping price for package size {size}.', 'For a {size} package, quote the sample {service} delivery cost.', 'Give the sample delivery fee for {service} service and a {size} parcel.', 'What sample fee applies to a {size} shipment using {service}?', 'Look up the sample shipping quote for a {size} package sent {service}.', 'A parcel is {size} and the service is {service}; determine its sample shipping fee.', 'Quote the sample cost of {service} delivery for a package of size {size}.', 'Determine the sample {size} package shipping charge using {service} service.'), answers=("The shipping fee is {result}.", "That delivery costs {result}."), cases=cases),
    ),
)


def resolve(size, service):
    if size == "large" and service == "express":
        raise InvalidCombination("Express is unavailable for large packages")
    fees = {"extra-small": 3, "small": 5, "medium": 8, "large": 12, "extra-large": 16, "oversized": 22}
    surcharges = {"economy": 0, "standard": 0, "express": 4, "priority": 7, "overnight": 12}
    return f"${fees[size] + surcharges[service]:.2f}"
