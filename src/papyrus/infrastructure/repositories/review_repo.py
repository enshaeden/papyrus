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


def get_review_assignment(connection: sqlite3.Connection, assignment_id: str) -> sqlite3.Row | None:
    return connection.execute(
        "SELECT * FROM review_assignments WHERE assignment_id = ?",
        (assignment_id,),
    ).fetchone()


def list_review_assignments_for_revision(
    connection: sqlite3.Connection,
    revision_id: str,
) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT *
        FROM review_assignments
        WHERE revision_id = ?
        ORDER BY assigned_at, assignment_id
        """,
        (revision_id,),
    ).fetchall()


def update_review_assignment(
    connection: sqlite3.Connection,
    *,
    assignment_id: str,
    state: str,
    notes: str | None = None,
) -> None:
    connection.execute(
        """
        UPDATE review_assignments
        SET state = ?, notes = COALESCE(?, notes)
        WHERE assignment_id = ?
        """,
        (state, notes, assignment_id),
    )
