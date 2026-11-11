from collections.abc import Callable
from dataclasses import dataclass

from PIL.Image import Image


@dataclass(frozen=True)
class ImageGenerationPreview:
    """Three labeled images from one model example at a completed training step.

    Published images must not be modified after handing them to the dashboard.
    """

    step: int
    images: tuple[Image, Image, Image]
    labels: tuple[str, str, str]


@dataclass(frozen=True)
class TrainingProgress:
    """A model-independent snapshot of training progress.

    Step counts completed parameter updates, starting at one. Metrics may
    describe the calculation used for that update. When present, "loss" is
    used for the dashboard's loss graph.
    total_steps is None when training runs until stopped.
    Each snapshot owns a fresh metrics dictionary that producers and consumers
    must not modify after publication.
    An optional preview carries model-provided images, not model tensors.
    """

    step: int
    total_steps: int | None
    metrics: dict[str, float]
    preview: ImageGenerationPreview | None = None


type ProgressCallback = Callable[[TrainingProgress], None]
