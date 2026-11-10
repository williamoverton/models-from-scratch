from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingProgress:
    """A model-independent snapshot of training progress.

    Step counts completed parameter updates, starting at one. Metrics may
    describe the calculation used for that update. When present, "loss" is
    used for the dashboard's loss graph.
    Each snapshot owns a fresh metrics dictionary that producers and consumers
    must not modify after publication.
    """

    step: int
    total_steps: int
    metrics: dict[str, float]


type ProgressCallback = Callable[[TrainingProgress], None]
