from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        names = rng.sample(("Aces", "Bears", "Comets", "Dragons", "Eagles"), 2)
        seeds = rng.sample(range(1, 9), 2)
        scores = [rng.randint(0, 5), rng.randint(0, 5)]
        yield {"team_a": names[0], "team_b": names[1], "score_a": str(scores[0]), "score_b": str(scores[1]), "seed_a": str(seeds[0]), "seed_b": str(seeds[1])}


def prepare(*, task_id, case):
    a = (int(case["score_a"]), -int(case["seed_a"]))
    b = (int(case["score_b"]), -int(case["seed_b"]))
    return Decision(fields=case, arguments={"team": case["team_a"] if a > b else case["team_b"]})


def resolve(team):
    return f"Advanced team: {team}."


SCHEMA = Schema(
    id="sports_tournament_advancement",
    tool_names=("advance_tournament_team", "record_advancing_team", "report_advancing_team", "submit_advancing_team", "register_advancing_team", "announce_advancing_team", "declare_advancing_team", "save_advancing_team", "set_advancing_team", "mark_team_advanced"),
    descriptions=("Advance the selected team by name.", "Record the selected team as advancing.", "Report the name of the advancing team.", "Submit the chosen team as the team that advanced.", "Register the selected team for advancement.", "Announce which named team advances.", "Declare the selected team as advancing.", "Save the name of the team advancing.", "Set the advancing team to the supplied name.", "Mark the specified team as having advanced."),
    parameters=(Parameter(names=("team", "team_id")),),
    tasks=(Task(id="advance", prompts=("Tournament match: {team_a} scored {score_a} with seed {seed_a}; {team_b} scored {score_b} with seed {seed_b}. Advance the higher-scoring team. If scores tie, advance the team with the lower seed number. Which team advances?", "Who advances between {team_a} ({score_a}, seed {seed_a}) and {team_b} ({score_b}, seed {seed_b})? Higher score wins; a tie goes to the lower seed number.", "Select the advancing team: {team_a} scored {score_a} and is seed {seed_a}; {team_b} scored {score_b} and is seed {seed_b}. Use higher score, then lower seed number on a tie.", "In this tournament, {team_a} has {score_a} points and seed {seed_a}, while {team_b} has {score_b} points and seed {seed_b}. Advance the higher scorer, breaking ties by lower seed number.", "Determine who advances: {team_a}, score {score_a}, seed {seed_a}; {team_b}, score {score_b}, seed {seed_b}. Higher score takes precedence; tied scores favor the lower seed number.", "A match ends {team_a} {score_a}, {team_b} {score_b}; their seeds are {seed_a} and {seed_b}, respectively. Which advances on higher score, or lower seed number if tied?", "Choose the team to advance from {team_a} (score {score_a}, seed {seed_a}) and {team_b} (score {score_b}, seed {seed_b}). Highest score wins; tied scores go to the lower seed number.", "With {team_a} at {score_a} and seed {seed_a}, and {team_b} at {score_b} and seed {seed_b}, identify the advancing team. Higher score advances, with lower seed number deciding ties.", "Tournament result: {team_a} scored {score_a} as seed {seed_a}; {team_b} scored {score_b} as seed {seed_b}. Advance the higher score, or the lower seed number if tied.", "Which team progresses? {team_a}: {score_a}, seed {seed_a}; {team_b}: {score_b}, seed {seed_b}. The higher score advances, and a score tie favors the lower seed number.", "Apply the advancement rule to {team_a} ({score_a}, seed {seed_a}) versus {team_b} ({score_b}, seed {seed_b}): higher score first, then lower seed number if tied."), answers=("{result}",), cases=cases),),
)
