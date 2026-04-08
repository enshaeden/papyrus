from __future__ import annotations

import sqlite3


def insert_event(
    connection: sqlite3.Connection,
    *,
    event_id: str,
    event_type: str,
    source: str,
    entity_type: str,
    entity_id: str,
    payload_json: str,
    occurred_at: str,
    actor: str,
) -> None:
    connection.execute(
        """
        INSERT INTO events (
            event_id,
            event_type,
            source,
            entity_type,
            entity_id,
            payload_json,
            occurred_at,
            actor
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            event_type,
            source,
            entity_type,
            entity_id,
            payload_json,
            occurred_at,
            actor,
        ),
    )


def get_event(connection: sqlite3.Connection, event_id: str) -> sqlite3.Row | None:
    return connection.execute("SELECT * FROM events WHERE event_id = ?", (event_id,)).fetchone()


def list_events(
    connection: sqlite3.Connection,
    *,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 100,
) -> list[sqlite3.Row]:
    clauses: list[str] = []
    parameters: list[str | int] = []
    if entity_type is not None:
        clauses.append("entity_type = ?")
        parameters.append(entity_type)
    if entity_id is not None:
        clauses.append("entity_id = ?")
        parameters.append(entity_id)
    where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    parameters.append(limit)
    return connection.execute(
        f"""
        SELECT *
        FROM events
        {where_sql}
        ORDER BY occurred_at DESC, event_id DESC
        LIMIT ?
        """,
        tuple(parameters),
    ).fetchall()
