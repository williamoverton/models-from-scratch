import random
from collections.abc import Iterator
from io import BytesIO
from pathlib import Path

import pyarrow.parquet as pq
import torch
from PIL import Image
from torch.utils.data import IterableDataset, get_worker_info


class DogImageDataset(IterableDataset):
    """Stream prepared dog images as CPU tensors without loading all images."""

    def __init__(
        self,
        directory: Path,
        shuffle_buffer_size: int = 1_024,
        read_batch_size: int = 128,
    ) -> None:
        """Find Parquet shards and configure bounded reading and shuffling."""
        super().__init__()

        if shuffle_buffer_size < 1:
            raise ValueError("Shuffle buffer size must be positive.")
        if read_batch_size < 1:
            raise ValueError("Parquet read batch size must be positive.")

        self.shards = sorted(directory.glob("train-*.parquet"))
        if not self.shards:
            raise ValueError(f"No training Parquet shards found in {directory}")

        self.shuffle_buffer_size = shuffle_buffer_size
        self.read_batch_size = read_batch_size

    def _read_images(self, shards: list[Path]) -> Iterator[bytes]:
        """Yield embedded PNG bytes from bounded Parquet record batches."""
        for shard in shards:
            with pq.ParquetFile(shard) as parquet:
                for batch in parquet.iter_batches(
                    batch_size=self.read_batch_size,
                    columns=["image"],
                ):
                    for image in batch.column(0).to_pylist():
                        image_bytes = image["bytes"]
                        if image_bytes is None:
                            raise ValueError(
                                f"Expected embedded image bytes in {shard}"
                            )
                        yield image_bytes

    def _shuffle_images(
        self,
        images: Iterator[bytes],
    ) -> Iterator[bytes]:
        """Mix compressed images through a fixed-size replacement buffer."""
        buffer = []

        for image in images:
            # Fill the buffer before yielding randomly selected entries.
            if len(buffer) < self.shuffle_buffer_size:
                buffer.append(image)
                continue

            # Replace a random entry and yield the image it previously held.
            index = random.randrange(len(buffer))
            selected = buffer[index]
            buffer[index] = image
            yield selected

        # Every buffered image must also be yielded when disk input ends.
        random.shuffle(buffer)
        yield from buffer

    def _decode_image(self, image_bytes: bytes) -> torch.Tensor:
        """Decode a PNG into a CPU float32 tensor [3, H, W] in [-1, 1]."""
        with Image.open(BytesIO(image_bytes)) as image:
            rgb = image.convert("RGB")
            pixels = torch.frombuffer(
                bytearray(rgb.tobytes()),
                dtype=torch.uint8,
            )
            pixels = pixels.reshape(rgb.height, rgb.width, 3)

        # Put channels first and scale byte values into the model's image range.
        pixels = pixels.permute(2, 0, 1).to(dtype=torch.float32)
        return pixels.div_(127.5).sub_(1)

    def __iter__(self) -> Iterator[torch.Tensor]:
        """Yield each assigned image once, using a shuffled streaming order."""
        # Partition files before shuffling so workers never duplicate shards.
        worker = get_worker_info()
        shards = (
            self.shards.copy()
            if worker is None
            else self.shards[worker.id :: worker.num_workers]
        )
        random.shuffle(shards)

        # Shuffle compressed records, then decode only the selected images.
        images = self._read_images(shards)
        for image_bytes in self._shuffle_images(images):
            yield self._decode_image(image_bytes)
