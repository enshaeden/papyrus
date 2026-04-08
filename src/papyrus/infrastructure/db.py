from __future__ import annotations

import sqlite3
from pathlib import Path


def recreate_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-shm", "-wal"):
        candidate = database_path.with_name(database_path.name + suffix)
        if candidate.exists():
            candidate.unlink()
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA journal_mode=WAL")
    return connection

