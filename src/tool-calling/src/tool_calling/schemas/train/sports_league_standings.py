from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        win_points = rng.randint(2, 5)
        draw_points = rng.randint(0, win_points - 1)
        yield {"wins": str(rng.randint(0, 15)), "draws": str(rng.randint(0, 8)), "win_points": str(win_points), "draw_points": str(draw_points)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(wins, draws, win_points, draw_points):
    return str(int(wins) * int(win_points) + int(draws) * int(draw_points))


SCHEMA = Schema(
    id="sports_league_standings",
    tool_names=("calculate_league_points", "compute_standings_points", "calculate_standings_points", "compute_league_points", "total_league_points", "calculate_team_points", "compute_team_points", "sum_standings_points", "derive_league_points", "determine_team_points"),
    descriptions=("Calculate points from wins, draws, and the supplied points per result.", "Compute league points using the given scoring system.", "Multiply wins and draws by their respective point values and add them.", "Find a team's total points from wins and draws using the supplied rates.", "Calculate standings points from the counts and points per result.", "Determine league points under the specified win and draw values.", "Sum points earned for wins and draws.", "Compute a team's points using its wins, draws, and scoring rates.", "Derive the points total from win and draw counts and their values.", "Return the total points awarded for the given wins and draws."),
    parameters=(Parameter(names=("wins", "win_count")), Parameter(names=("draws", "draw_count")), Parameter(names=("win_points", "points_per_win")), Parameter(names=("draw_points", "points_per_draw"))),
    tasks=(Task(id="points", prompts=("A team has {wins} wins and {draws} draws. A win earns {win_points} points and a draw earns {draw_points}; losses earn zero. Calculate its points.", "Calculate league points for {wins} wins and {draws} draws, at {win_points} per win and {draw_points} per draw; losses score zero.", "What is the team's total with {wins} wins worth {win_points} points each and {draws} draws worth {draw_points} each? Losses earn zero.", "A team's record includes {wins} wins and {draws} draws. Wins give {win_points}, draws {draw_points}, and losses zero points. Find its total.", "Using {win_points} points per win, {draw_points} per draw, and zero per loss, total the points for {wins} wins and {draws} draws.", "Work out the standings points: {wins} wins, {draws} draws, {win_points} points for a win, {draw_points} for a draw, zero for a loss.", "How many points does a team with {wins} wins and {draws} draws have if wins are worth {win_points}, draws {draw_points}, and losses zero?", "Find the league total for {wins} wins at {win_points} points and {draws} draws at {draw_points} points; losses have no points.", "The scoring system gives {win_points} for a win, {draw_points} for a draw, and zero for a loss. Calculate points for {wins} wins and {draws} draws.", "For {wins} wins and {draws} draws, sum the points at {win_points} per win and {draw_points} per draw; losses earn zero.", "Determine the team's points from {wins} wins and {draws} draws, with {win_points} points per win, {draw_points} per draw, and none for losses."), answers=("The team has {result} points.",), cases=cases),),
)
