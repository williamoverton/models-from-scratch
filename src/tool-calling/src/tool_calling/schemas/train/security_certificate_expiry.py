from ...schema_types import Decision, Parameter, Schema, Task


CERTIFICATES = {"CERT-101": "2027-02-18", "CERT-102": "2027-07-09", "CERT-103": "2028-01-22", "CERT-104": "2028-10-05"}


def cases(rng, count):
    for _ in range(count):
        yield {"certificate": rng.choice(tuple(CERTIFICATES))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(certificate):
    return f"{certificate} expires {CERTIFICATES[certificate]}"


SCHEMA = Schema(
    id="security_certificate_expiry",
    tool_names=("get_certificate_expiry", "lookup_cert_expiry", "find_certificate_expiry", "get_cert_expiration_date", "lookup_certificate_expiration", "retrieve_certificate_expiry", "read_cert_expiry_date", "find_cert_expiration", "get_certificate_expiry_date", "lookup_sample_certificate_expiry"),
    descriptions=("Look up a sample certificate's expiry date.", "Retrieve a sample certificate expiry.", "Find the expiry date of a sample certificate.", "Get a certificate's expiration date from the sample registry.", "Look up when a registered sample certificate expires.", "Read the expiration date for a sample certificate ID.", "Retrieve the registered expiry of a certificate.", "Find a sample certificate's expiration date by ID.", "Return the expiry date for the specified sample certificate.", "Check the sample registry for a certificate expiry."),
    parameters=(Parameter(names=("certificate", "certificate_id")),),
    tasks=(Task(id="expiry", prompts=("When does certificate {certificate} expire in the sample registry?", "Look up the expiry date for {certificate} in the sample certificate registry.", "Find the sample registry expiration date of {certificate}.", "Check when {certificate} expires according to the sample certificate registry.", "Retrieve the registered expiry for certificate {certificate} from the sample registry.", "What expiry date does the sample registry list for {certificate}?", "Read the expiration date of {certificate} from the sample certificate registry.", "Consult the sample registry for certificate {certificate}'s expiration.", "Give me the sample registry expiry date for {certificate}.", "For certificate {certificate}, find its expiration in the sample registry.", "Which date is registered as the expiry of {certificate} in the sample registry?", "Get {certificate}'s expiry date from the sample certificate registry."), answers=("{result}.", "{result}."), cases=cases),),
)
