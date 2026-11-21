"""Timestamped file logging with explicit training-segment rotation."""

from logging import Formatter
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


class SegmentLogHandler(RotatingFileHandler):
    """Keep up to 1,000 numbered backups for a single writer's log path."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(path, maxBytes=0, backupCount=1_000, encoding="utf-8", delay=True)
        self.setFormatter(Formatter(LOG_FORMAT))

    def start_segment(self) -> None:
        """Archive an existing nonempty log before recording the new segment."""
        with self.lock:
            try:
                size = Path(self.baseFilename).stat().st_size
            except FileNotFoundError:
                return
            if size:
                self.doRollover()
