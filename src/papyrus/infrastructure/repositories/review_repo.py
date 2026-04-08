from __future__ import annotations

import sqlite3


def insert_review_assignment(
    connection: sqlite3.Connection,
    *,
    assignment_id: str,
    object_id: str,
    revision_id: str | None,
    reviewer: str,
    state: str,
    assigned_at: str,
    due_at: str | None,
    notes: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO review_assignments (
            assignment_id,
            object_id,
            revision_id,
            reviewer,
            state,
            assigned_at,
            due_at,
            notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            assignment_id,
            object_id,
            revision_id,
            reviewer,
            state,
            assigned_at,
            due_at,
            notes,
        ),
    )
