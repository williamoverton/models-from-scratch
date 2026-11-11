# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11", "pyarrow>=19"]
# ///
"""Run: uv run scripts/prepare_dog_images.py /mnt/StorageBox/datasets/SDIP_dog

Keep original shards in data/ and write RGB PNG images to 64x64/ Parquet shards.
Images are resized directly: SDIP dogs are already curated square crops.
"""

import argparse
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps
import pyarrow as pa
import pyarrow.parquet as pq


def convert_shard(source: Path, destination: Path) -> int:
    image_type = pa.struct([("bytes", pa.binary()), ("path", pa.string())])
    schema = pa.schema([("image", image_type)])
    temporary = destination.with_suffix(".parquet.tmp")
    count = 0
    try:
        with pq.ParquetWriter(temporary, schema, compression="snappy") as writer:
            for batch in pq.ParquetFile(source).iter_batches(
                batch_size=128, columns=["image"]
            ):
                images = []
                for record in batch.column(0).to_pylist():
                    if record["bytes"] is None:
                        raise ValueError(f"Expected embedded image bytes in {source}")
                    with Image.open(BytesIO(record["bytes"])) as original:
                        image = ImageOps.exif_transpose(original).convert("RGB")
                        image = image.resize((64, 64), Image.Resampling.LANCZOS)
                        buffer = BytesIO()
                        image.save(buffer, format="PNG")
                    images.append({"bytes": buffer.getvalue(), "path": None})
                writer.write_table(pa.Table.from_pylist([{"image": image} for image in images], schema=schema))
                count += len(images)
        expected = pq.ParquetFile(source).metadata.num_rows
        if count != expected:
            raise ValueError(f"Row count mismatch for {source}: {count} != {expected}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path, help="Downloaded SDIP_dog directory")
    args = parser.parse_args()
    sources = sorted((args.dataset / "data").glob("train-*.parquet"))
    if not sources:
        parser.error(f"No training Parquet shards found in {args.dataset / 'data'}")
    output = args.dataset / "64x64"
    output.mkdir(exist_ok=True)
    if any(output.iterdir()):
        parser.error(f"Output directory must be empty: {output}")
    total = 0
    for index, source in enumerate(sources, start=1):
        count = convert_shard(source, output / source.name)
        total += count
        print(f"[{index}/{len(sources)}] {source.name}: {count:,} images ({total:,} total)", flush=True)
    print(f"Converted {total:,} images to 64×64 RGB PNGs in {output}", flush=True)


if __name__ == "__main__":
    main()
