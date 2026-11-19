from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        piece = rng.randint(10, 40)
        kerf = rng.randint(1, 3)
        stock = rng.randint(2, 8) * (piece + kerf) + rng.randint(0, piece + kerf - 1)
        yield {"stock": str(stock), "piece": str(piece), "kerf": str(kerf)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(stock, piece, kerf):
    return str(int(stock) // (int(piece) + int(kerf)))


SCHEMA = Schema(
    id="workshop_cut_plan",
    tool_names=('calculate_cut_pieces', 'plan_stock_cuts', 'count_complete_pieces', 'calculate_stock_yield', 'compute_cut_count', 'estimate_piece_count', 'determine_cut_capacity', 'calculate_piece_yield', 'count_pieces_with_kerf', 'compute_stock_pieces'),
    descriptions=('Calculate complete pieces with one saw cut per piece.', 'Divide stock length by piece length plus kerf and round down.', 'Count complete pieces from stock including kerf for every cut.', 'Compute the maximum pieces when each piece consumes its length plus kerf.', 'Determine how many pieces fit with one cut per piece.', 'Calculate piece yield from stock length, piece length, and saw kerf.', 'Find the whole-piece count including the final cut’s kerf.', 'Return the floor of stock length divided by piece length plus kerf.', 'Compute stock capacity for complete pieces with a cut per piece.', 'Count pieces allowing for saw kerf on every piece.'),
    parameters=(Parameter(names=("stock", "stock_length")), Parameter(names=("piece", "piece_length")), Parameter(names=("kerf", "saw_kerf"))),
    tasks=(Task(id="cut_plan", prompts=("A {stock} mm stock is cut into {piece} mm pieces. Each piece requires one saw cut, including the last, and each cut consumes {kerf} mm of stock. What is the maximum number of complete pieces?", "Plan cuts from {stock} mm stock for {piece} mm pieces. Use one cut per piece, even the final piece; each cut loses {kerf} mm as kerf. How many complete pieces fit?", 'With {stock} mm of stock, how many complete {piece} mm pieces fit if every piece, including the last, needs a cut consuming {kerf} mm?', 'Calculate whole-piece yield from {stock} mm stock and {piece} mm pieces, allowing {kerf} mm kerf for each cut, including the final cut.', 'Stock length is {stock} mm; each {piece} mm piece requires one {kerf} mm kerf cut, even the last. Find the maximum complete pieces.', 'How many complete {piece} mm lengths can be cut from {stock} mm if every piece uses one cut losing {kerf} mm, including the final piece?', 'Divide {stock} mm stock into {piece} mm pieces, counting a {kerf} mm saw cut per piece including the last; report the maximum whole-piece count.', 'Find the maximum number of complete pieces from {stock} mm stock, with {piece} mm per piece and {kerf} mm lost to each piece’s cut, including the last.', 'Each {piece} mm piece takes one cut of {kerf} mm kerf, even the final piece. What is the whole-piece capacity of {stock} mm stock?', 'For {stock} mm stock, count complete {piece} mm pieces assuming one {kerf} mm kerf cut for every piece, last included.', 'What is the largest whole number of {piece} mm pieces from {stock} mm stock when each requires a {kerf} mm cut, including the final piece?', 'Plan the yield of {stock} mm stock: pieces are {piece} mm and each, including the last, requires a saw cut consuming {kerf} mm. Give the maximum complete count.'), answers=("{result} pieces.", "Maximum: {result} pieces."), cases=cases),),
)
