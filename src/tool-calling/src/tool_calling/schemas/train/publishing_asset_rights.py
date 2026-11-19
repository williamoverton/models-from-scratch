from ...schema_types import Decision, Parameter, Schema, Task


LICENSES = {
    "Aster": ("web", "print"),
    "Birch": ("web",),
    "Cove": ("print",),
    "Dune": ("social", "web"),
    "Elm": ("social",),
}


def cases(rng, count):
    for _ in range(count):
        yield {"asset": rng.choice(tuple(LICENSES)), "use": rng.choice(("web", "print", "social"))}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(asset, use):
    return "permitted" if use in LICENSES[asset] else "not permitted"


SCHEMA = Schema(
    id="publishing_asset_rights",
    tool_names=("check_asset_rights", "check_license_use", "verify_asset_license", "check_permitted_use", "assess_asset_usage_rights", "lookup_license_permission", "verify_intended_use", "determine_asset_permission", "inspect_asset_rights", "check_use_against_license"),
    descriptions=("Check whether a recorded asset license permits the requested use.", "Look up an asset license and check the specified use.", "Determine if the asset's recorded license allows the intended use.", "Verify a requested use against the asset rights registry.", "Assess whether the specified asset is licensed for the given use.", "Check the recorded permissions for an asset and use.", "Find whether an asset's license permits its intended use.", "Compare the requested use with the asset's licensed uses.", "Determine permission for a use from the recorded asset license.", "Inspect the rights registry for the asset's specified use."),
    parameters=(Parameter(names=("asset", "asset_id")), Parameter(names=("use", "intended_use"))),
    tasks=(Task(id="rights", prompts=("Does the recorded license for asset {asset} permit {use} use? Check the rights registry.", "Check the rights registry: is {use} use permitted for asset {asset}?", "Look up asset {asset} in the rights registry and check permission for {use}.", "Is {asset} licensed for {use} use according to the registry?", "Verify the recorded license permits {use} for asset {asset}.", "Consult the asset rights registry: can {asset} be used for {use}?", "Determine whether {use} is an allowed use of asset {asset} under its recorded license.", "Check if the registry authorizes {use} use of {asset}.", "For asset {asset}, does the registered license allow {use}?", "Assess {use} permission for {asset} using its recorded rights.", "Find whether {asset}'s rights permit the intended {use} use.", "Compare requested {use} use for asset {asset} against the rights registry."), answers=("The use is {result}.", "License: {result}."), cases=cases),),
)
