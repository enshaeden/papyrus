from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.runtime_projection import RuntimeStateSnapshot
from papyrus.infrastructure.paths import DB_PATH

class QueryRuntimeError(RuntimeError):
    """Base query error for operator surfaces."""

class RuntimeUnavailableError(QueryRuntimeError):
    """Raised when the relational runtime has not been built yet."""

class KnowledgeObjectNotFoundError(QueryRuntimeError):
    """Raised when a requested knowledge object does not exist."""

class ServiceNotFoundError(QueryRuntimeError):
    """Raised when a requested service does not exist."""

def build_status_filter_clause(statuses: list[str]) -> tuple[str, tuple[str, ...]]:
    placeholders = ", ".join("?" for _ in statuses)
    return f"({placeholders})", tuple(statuses)

def runtime_connection(database_path: str | Path = DB_PATH) -> sqlite3.Connection | None:
    path = Path(database_path)
    if not path.exists():
        return None
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    has_runtime = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_objects'"
    ).fetchone()
    if has_runtime is None:
        connection.close()
        return None
    return connection

def require_runtime_connection(database_path: str | Path = DB_PATH) -> sqlite3.Connection:
    connection = runtime_connection(database_path)
    if connection is None:
        raise RuntimeUnavailableError(
            "runtime database is not available; run `python3 scripts/build_index.py` first"
        )
    return connection

def _json_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return []
        return loaded if isinstance(loaded, list) else []
    return []

def _json_dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return loaded if isinstance(loaded, dict) else {}
    return {}

def _object_lifecycle_value(row: sqlite3.Row) -> str:
    return str(row["object_lifecycle_state"])

def _revision_review_value(row: sqlite3.Row) -> str:
    return str(row["revision_review_state"] or "draft")

def _draft_progress_value(row: sqlite3.Row) -> str:
    return str(row["draft_progress_state"] or "ready_for_review")

def _source_sync_value(row: sqlite3.Row) -> str:
    return str(row["source_sync_state"] or "not_required")

def _policy_authority(authority: PolicyAuthority | None) -> PolicyAuthority:
    return authority or PolicyAuthority.from_repository_policy()

def _runtime_state_snapshot(
    row: sqlite3.Row,
    *,
    trust_state: str | None = None,
) -> RuntimeStateSnapshot:
    return RuntimeStateSnapshot(
        object_lifecycle_state=_object_lifecycle_value(row),
        revision_review_state=(
            _revision_review_value(row)
            if row["revision_review_state"] is not None
            else None
        ),
        draft_progress_state=(
            _draft_progress_value(row)
            if row["draft_progress_state"] is not None
            else None
        ),
        source_sync_state=_source_sync_value(row),
        trust_state=trust_state,
    )

