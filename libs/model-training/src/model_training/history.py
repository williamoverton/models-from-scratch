"""Store reported training metrics alongside a run's checkpoint."""

import sqlite3
from math import isfinite
from pathlib import Path

from model_training.progress import TrainingProgress


class MetricsHistory:
    """Keep one value per metric and step in a run-local SQLite database."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        try:
            self._connection.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    name TEXT NOT NULL,
                    step INTEGER NOT NULL,
                    value REAL NOT NULL,
                    PRIMARY KEY (name, step)
                ) WITHOUT ROWID
            """)
        except sqlite3.Error:
            self._connection.close()
            raise

    def resume(self, step: int) -> None:
        """Discard reports newer than the checkpoint that actually loaded."""
        with self._connection:
            self._connection.execute("DELETE FROM metrics WHERE step > ?", (step,))

    def record(self, progress: TrainingProgress) -> None:
        """Commit finite scalars from one report without overwriting absent metrics."""
        if not progress.metrics:
            return
        with self._connection:
            self._connection.executemany("""
                INSERT INTO metrics (name, step, value) VALUES (?, ?, ?)
                ON CONFLICT (name, step) DO UPDATE SET value = excluded.value
            """, (
                (name, progress.step, value)
                for name, value in progress.metrics.items()
                if isfinite(value)
            ))

    def series(self, name: str) -> dict[int, float]:
        """Read every reported point for a chart in step order."""
        return dict(self._connection.execute(
            "SELECT step, value FROM metrics WHERE name = ? ORDER BY step", (name,)
        ))

    def close(self) -> None:
        """Release the database connection."""
        self._connection.close()
