from __future__ import annotations

import sqlite3


def insert_validation_run(
    connection: sqlite3.Connection,
    *,
    run_id: str,
    run_type: str,
    started_at: str,
    completed_at: str,
    status: str,
    finding_count: int,
    details_json: str,
) -> None:
    connection.execute(
        """
        INSERT INTO validation_runs (
            run_id,
            run_type,
            started_at,
            completed_at,
            status,
            finding_count,
            details_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            run_type,
            started_at,
            completed_at,
            status,
            finding_count,
            details_json,
        ),
    )
