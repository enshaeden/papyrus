from __future__ import annotations

import sqlite3
from pathlib import Path


RUNTIME_SCHEMA_VERSION = 6


def connect_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA journal_mode=WAL")
    return connection


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def runtime_schema_version(connection: sqlite3.Connection) -> int:
    if not table_exists(connection, "schema_migrations"):
        return 0
    row = connection.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
    if not row:
        return 0
    value = row[0]
    return int(value or 0)


def open_runtime_database(
    database_path: Path,
    *,
    minimum_schema_version: int = RUNTIME_SCHEMA_VERSION,
) -> sqlite3.Connection:
    connection = connect_database(database_path)
    version = runtime_schema_version(connection)
    if version and version >= minimum_schema_version:
        return connection
    if database_path.exists() and version < minimum_schema_version:
        connection.close()
        return recreate_database(database_path)
    return connection


def recreate_database(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-shm", "-wal"):
        candidate = database_path.with_name(database_path.name + suffix)
        if candidate.exists():
            candidate.unlink()
    return connect_database(database_path)
