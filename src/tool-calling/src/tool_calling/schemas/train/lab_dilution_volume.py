from decimal import Decimal

from ...schema_types import Decision, Parameter, Schema, Task


def cases(rng, count):
    for _ in range(count):
        factor = rng.choice((2, 4, 5, 10, 20))
        stock_volume = rng.randint(1, 20)
        yield {"stock": str(factor), "target": "1", "final_volume": str(factor * stock_volume)}


def prepare(*, task_id, case):
    return Decision(fields=case, arguments=case)


def resolve(stock, target, final_volume):
    volume = Decimal(target) * Decimal(final_volume) / Decimal(stock)
    return f"{volume} mL stock and {Decimal(final_volume) - volume} mL diluent"


SCHEMA = Schema(
    id="lab_dilution_volume",
    tool_names=("calculate_stock_volume", "calculate_dilution_volume", "calculate_stock_and_diluent", "compute_dilution_volumes", "find_stock_and_diluent_volumes", "determine_dilution_volumes", "compute_stock_volume_for_dilution", "calculate_solution_dilution", "derive_stock_and_diluent", "compute_stock_and_diluent_ml"),
    descriptions=("Calculate stock and diluent volumes in mL using C1 V1 = C2 V2 and diluent = final volume minus stock.", "Find stock and diluent volumes for a dilution.", "Compute mL of stock from target concentration and final volume, and subtract it from final volume for diluent.", "Use the stock and target concentrations and final volume to calculate stock and diluent in mL.", "Determine the stock and diluent volumes for a requested final dilution.", "Apply C1 V1 = C2 V2 and return the required stock and remaining diluent in mL.", "Calculate the amount of stock solution and diluent needed to make the final volume.", "Find stock volume as target concentration times final volume divided by stock concentration, then find diluent by subtraction.", "Work out both solution volumes in mL for the given concentrations and final volume.", "Compute stock and diluent quantities for a dilution using the concentration-volume equation."),
    parameters=(Parameter(names=("stock", "stock_concentration")), Parameter(names=("target", "target_concentration")), Parameter(names=("final_volume", "final_volume_ml"))),
    tasks=(Task(id="volume", prompts=("Stock concentration is {stock} mg/mL, target is {target} mg/mL, and final volume is {final_volume} mL. Using C1 V1 = C2 V2, calculate mL of stock and diluent; diluent is final volume minus stock volume.", "For {final_volume} mL at {target} mg/mL from {stock} mg/mL stock, calculate stock and diluent volumes in mL using C1 V1 = C2 V2 and diluent = final volume minus stock.", "Make {final_volume} mL at {target} mg/mL from {stock} mg/mL stock. Use C1 V1 = C2 V2 for stock volume and subtract it from final volume for diluent; report both in mL.", "How many mL of stock and diluent are needed for {final_volume} mL at {target} mg/mL from {stock} mg/mL stock? Apply C1 V1 = C2 V2; diluent equals final volume minus stock volume.", "Calculate stock and diluent in mL for a {final_volume} mL final solution at {target} mg/mL using {stock} mg/mL stock. Use C1 V1 = C2 V2 and subtract stock volume from final volume for diluent.", "The stock is {stock} mg/mL, the target {target} mg/mL, and the final volume {final_volume} mL. Using C1 V1 = C2 V2, find stock mL and diluent mL, with diluent equal to final volume minus stock volume.", "Use C1 V1 = C2 V2 to prepare {final_volume} mL at {target} mg/mL from stock at {stock} mg/mL. Give mL of stock and diluent, taking diluent as final volume minus stock volume.", "For a dilution from {stock} mg/mL to {target} mg/mL with {final_volume} mL final volume, calculate stock and diluent mL using C1 V1 = C2 V2; diluent is final volume less stock volume.", "What stock and diluent volumes in mL yield {final_volume} mL of {target} mg/mL solution from {stock} mg/mL stock? Use C1 V1 = C2 V2 and subtract stock volume from final volume for diluent.", "Find the mL of {stock} mg/mL stock and mL of diluent for {final_volume} mL at {target} mg/mL. Use C1 V1 = C2 V2; diluent volume equals final volume minus stock volume.", "Using stock at {stock} mg/mL, target {target} mg/mL, and final volume {final_volume} mL, work out stock and diluent mL via C1 V1 = C2 V2 and final volume minus stock volume.", "Determine the mL of stock and diluent for {final_volume} mL at {target} mg/mL from {stock} mg/mL stock. Calculate stock using C1 V1 = C2 V2 and diluent as final volume minus stock volume."), answers=("Use {result}.", "Required: {result}."), cases=cases),),
)
