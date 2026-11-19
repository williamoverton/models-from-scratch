from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static
from textual_image.widget import Image

from model_training.progress import ImageGenerationPreview, TextGenerationPreview


class ImageGenerationPanel(Vertical):
    """Display two rows of three model-provided generation snapshots."""

    def compose(self) -> ComposeResult:
        """Reserve image slots for both generations above the metrics."""
        yield Static("Waiting for generated examples.", id="preview-caption")
        for row in range(2):
            yield Static("—", id=f"preview-row-{row}", classes="preview-row-title")
            with Horizontal(classes="preview-images"):
                for index in range(3):
                    with Vertical(classes="preview-slot"):
                        yield Static("—", id=f"preview-label-{row}-{index}", markup=False)
                        yield Image(id=f"preview-image-{row}-{index}")

    def on_mount(self) -> None:
        """Label the panel without depending on a model project."""
        self.border_title = "Current model examples"

    def show_preview(self, preview: ImageGenerationPreview) -> None:
        """Replace both rows without rebuilding the image widgets."""
        self.query_one("#preview-caption", Static).update(
            f"Training step {preview.step:,}"
        )
        for row_index, row in enumerate(preview.rows):
            self.query_one(f"#preview-row-{row_index}", Static).update(row.title)
            for index, (image, label) in enumerate(zip(row.images, row.labels, strict=True)):
                self.query_one(f"#preview-label-{row_index}-{index}", Static).update(label)
                self.query_one(f"#preview-image-{row_index}-{index}", Image).image = image

    def reset_preview(self) -> None:
        """Clear both generations before starting another run."""
        self.query_one("#preview-caption", Static).update("Waiting for generated examples.")
        for row in range(2):
            self.query_one(f"#preview-row-{row}", Static).update("—")
            for index in range(3):
                self.query_one(f"#preview-label-{row}-{index}", Static).update("—")
                self.query_one(f"#preview-image-{row}-{index}", Image).image = None


class TextGenerationPanel(Static):
    """Display the latest generated text snapshot or a waiting message."""

    def on_mount(self) -> None:
        self.border_title = "Generated examples"
        self.reset_preview()

    def show_preview(self, preview: TextGenerationPreview) -> None:
        """Replace the snapshot with its producing step and labeled text."""
        sections = [f"Sample step {preview.step:,}"]
        sections.extend(
            f"{example.label}\n{example.context}\n{example.completion}"
            for example in preview.examples
        )
        self.update("\n\n".join(sections))

    def reset_preview(self) -> None:
        """Clear the snapshot before starting another run."""
        self.update("Waiting for first example.")
