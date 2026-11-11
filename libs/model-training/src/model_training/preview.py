from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual_image.widget import Image

from model_training.progress import ImageGenerationPreview


class ImageGenerationPanel(Vertical):
    """Display three labeled images from the latest model-generated example."""

    def compose(self) -> ComposeResult:
        """Reserve a stable row of image slots above the training metrics."""
        yield Static("Waiting for a generated example.", id="preview-caption")
        with Horizontal(id="preview-images"):
            for index in range(3):
                with Vertical(classes="preview-slot"):
                    yield Static("—", id=f"preview-label-{index}", markup=False)
                    yield Image(id=f"preview-image-{index}")

    def on_mount(self) -> None:
        """Label the panel without depending on a particular model project."""
        self.border_title = "Current model example"

    def show_preview(self, preview: ImageGenerationPreview) -> None:
        """Replace all three images and captions with the supplied example."""
        self.query_one("#preview-caption", Static).update(
            f"Training step {preview.step:,}"
        )

        # Update the existing widgets rather than rebuilding the image row.
        for index, (image, label) in enumerate(
            zip(preview.images, preview.labels, strict=True)
        ):
            self.query_one(f"#preview-label-{index}", Static).update(label)
            self.query_one(f"#preview-image-{index}", Image).image = image

    def reset_preview(self) -> None:
        """Clear the previous run's example before starting another run."""
        self.query_one("#preview-caption", Static).update(
            "Waiting for a generated example."
        )
        for index in range(3):
            self.query_one(f"#preview-label-{index}", Static).update("—")
            self.query_one(f"#preview-image-{index}", Image).image = None
