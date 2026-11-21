from collections.abc import Callable
from dataclasses import dataclass

from PIL.Image import Image


@dataclass(frozen=True)
class ImageGenerationRow:
    """Three labeled snapshots; published images must not be modified."""

    title: str
    images: tuple[Image, Image, Image]
    labels: tuple[str, str, str]


@dataclass(frozen=True)
class ImageGenerationPreview:
    """Two model-provided generation rows at a completed training step."""

    step: int
    rows: tuple[ImageGenerationRow, ImageGenerationRow]


@dataclass(frozen=True)
class TextGenerationExample:
    """A labeled, display-ready context and completion."""

    label: str
    context: str
    completion: str


@dataclass(frozen=True)
class TextGenerationPreview:
    """A complete snapshot of generated examples at a completed step."""

    step: int
    examples: tuple[TextGenerationExample, ...]


@dataclass(frozen=True)
class TrainingStarted:
    """The restored checkpoint step, or zero when starting from scratch."""

    step: int


@dataclass(frozen=True)
class TrainingProgress:
    """A model-independent snapshot of training progress.

    Step counts completed parameter updates, starting at one. Metrics may
    describe the calculation used for that update. When present, "loss" and
    "validation loss" feed the dashboard's training and validation charts.
    total_steps is None when training runs until stopped.
    Each snapshot owns a fresh metrics dictionary that producers and consumers
    must not modify after publication.
    An optional preview carries display-ready images or text, not model tensors.
    A preview-only report uses an empty metrics dictionary and leaves the
    loss charts and training metrics unchanged.
    """

    step: int
    total_steps: int | None
    metrics: dict[str, float]
    preview: ImageGenerationPreview | TextGenerationPreview | None = None


type ProgressCallback = Callable[[TrainingStarted | TrainingProgress], None]
