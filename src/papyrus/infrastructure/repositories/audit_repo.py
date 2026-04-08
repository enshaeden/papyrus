from __future__ import annotations

import sqlite3


def insert_audit_event(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    event_type: str,
    occurred_at: str,
    actor: str,
    object_id: str | None,
    revision_id: str | None,
    details_json: str,
) -> None:
    connection.execute(
        """
        INSERT INTO audit_events (
            event_id,
            event_type,
            occurred_at,
            actor,
            object_id,
            revision_id,
            details_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            occurred_at,
            actor,
            object_id,
            revision_id,
            details_json,
        ),
    )
