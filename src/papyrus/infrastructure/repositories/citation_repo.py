from __future__ import annotations

import sqlite3


def insert_citation(
    connection: sqlite3.Connection,
    *,
    citation_id: str,
    revision_id: str,
    claim_anchor: str | None,
    source_type: str,
    source_ref: str,
    source_title: str,
    note: str | None,
    excerpt: str | None,
    captured_at: str | None,
    validity_status: str,
    integrity_hash: str | None,
) -> None:
    connection.execute(
        """
        INSERT INTO citations (
            citation_id,
            revision_id,
            claim_anchor,
            source_type,
            source_ref,
            source_title,
            note,
            excerpt,
            captured_at,
            validity_status,
            integrity_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            citation_id,
            revision_id,
            claim_anchor,
            source_type,
            source_ref,
            source_title,
            note,
            excerpt,
            captured_at,
            validity_status,
            integrity_hash,
        ),
    )
