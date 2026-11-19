from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        total = rng.choice((4, 5, 10, 20, 25, 50, 100))
        yield {"surveyed": rng.randint(0, total), "total": total}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments={key: str(value) for key, value in case.items()})


def resolve(surveyed, total):
    return f"{int(surveyed) * 100 // int(total)}%"


SCHEMA = Schema(
    id="conservation_survey_coverage",
    tool_names=("calculate_survey_coverage", "survey_coverage_percent", "compute_surveyed_site_percentage", "find_survey_area_coverage", "calculate_site_survey_percent", "derive_survey_coverage", "compute_surveyed_area_percent", "determine_site_coverage_percent", "find_surveyed_percentage", "calculate_coverage_from_areas"),
    descriptions=("Calculate surveyed area as a percentage of site area.", "Compute survey area coverage percentage.", "Divide surveyed area by total site area and express the result as a percentage.", "Find what percentage of the site area has been surveyed.", "Compute surveyed area times 100 divided by total area using integer division.", "Determine the surveyed proportion of the site as a whole-number percentage.", "Calculate percentage coverage from surveyed and total site areas.", "Return the surveyed share of the total area as a percentage.", "Compute site survey coverage using surveyed hectares and total hectares.", "Find the whole-number percentage of site area surveyed."),
    parameters=(Parameter(names=("surveyed", "surveyed_area")), Parameter(names=("total", "site_area"))),
    tasks=(Task(id="coverage", prompts=('A site covers {total} hectares, of which {surveyed} hectares were surveyed. Calculate surveyed area divided by site area as a percentage.', 'What percentage of a {total}-hectare site was surveyed if {surveyed} hectares were covered?', 'Of {total} hectares in the site, {surveyed} hectares have been surveyed. Express that coverage as a percentage.', 'Divide the surveyed {surveyed} hectares by the total {total} hectares and calculate the percentage covered.', 'How much of the site, in percent, has been surveyed? Its total area is {total} hectares and the survey covered {surveyed} hectares.', 'A survey covered {surveyed} hectares within a {total}-hectare site. Determine the surveyed share as a percentage.', 'Compute survey coverage in percent for {surveyed} hectares surveyed out of {total} hectares overall.', 'The surveyed footprint is {surveyed} hectares; the entire site measures {total} hectares. Find the percentage surveyed.', 'For a site of {total} hectares, turn the {surveyed} hectares surveyed into a percentage of the total area.', 'Calculate the ratio of {surveyed} surveyed hectares to {total} site hectares as a percentage.', 'A conservation team surveyed {surveyed} hectares of a {total}-hectare site. What is its percentage coverage?', 'Express the surveyed fraction as a percentage: {surveyed} hectares covered, {total} hectares in the site.'), answers=("Coverage: {result}.", "{result} of the site."), cases=cases),),
)
