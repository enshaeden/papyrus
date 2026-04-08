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
    evidence_snapshot_path: str | None,
    evidence_expiry_at: str | None,
    evidence_last_validated_at: str | None,
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
            integrity_hash,
            evidence_snapshot_path,
            evidence_expiry_at,
            evidence_last_validated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(citation_id) DO UPDATE SET
            revision_id = excluded.revision_id,
            claim_anchor = excluded.claim_anchor,
            source_type = excluded.source_type,
            source_ref = excluded.source_ref,
            source_title = excluded.source_title,
            note = excluded.note,
            excerpt = excluded.excerpt,
            captured_at = excluded.captured_at,
            validity_status = excluded.validity_status,
            integrity_hash = excluded.integrity_hash,
            evidence_snapshot_path = excluded.evidence_snapshot_path,
            evidence_expiry_at = excluded.evidence_expiry_at,
            evidence_last_validated_at = excluded.evidence_last_validated_at
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
            evidence_snapshot_path,
            evidence_expiry_at,
            evidence_last_validated_at,
        ),
    )


def delete_citations_for_revision(connection: sqlite3.Connection, revision_id: str) -> None:
    connection.execute("DELETE FROM citations WHERE revision_id = ?", (revision_id,))


def update_citation_validity_status(
    connection: sqlite3.Connection,
    citation_id: str,
    validity_status: str,
) -> None:
    connection.execute(
        "UPDATE citations SET validity_status = ? WHERE citation_id = ?",
        (validity_status, citation_id),
    )


def update_citation_evidence_fields(
    connection: sqlite3.Connection,
    *,
    citation_id: str,
    validity_status: str | None = None,
    integrity_hash: str | None = None,
    evidence_snapshot_path: str | None = None,
    evidence_expiry_at: str | None = None,
    evidence_last_validated_at: str | None = None,
) -> None:
    assignments: list[str] = []
    values: list[str | None] = []
    if validity_status is not None:
        assignments.append("validity_status = ?")
        values.append(validity_status)
    if integrity_hash is not None:
        assignments.append("integrity_hash = ?")
        values.append(integrity_hash)
    if evidence_snapshot_path is not None:
        assignments.append("evidence_snapshot_path = ?")
        values.append(evidence_snapshot_path)
    if evidence_expiry_at is not None:
        assignments.append("evidence_expiry_at = ?")
        values.append(evidence_expiry_at)
    if evidence_last_validated_at is not None:
        assignments.append("evidence_last_validated_at = ?")
        values.append(evidence_last_validated_at)
    if not assignments:
        return
    values.append(citation_id)
    connection.execute(
        f"UPDATE citations SET {', '.join(assignments)} WHERE citation_id = ?",
        tuple(values),
    )


def citation_status_counts_for_revision(connection: sqlite3.Connection, revision_id: str) -> dict[str, int]:
    counts = {"verified": 0, "unverified": 0, "stale": 0, "broken": 0}
    rows = connection.execute(
        """
        SELECT validity_status, COUNT(*) AS item_count
        FROM citations
        WHERE revision_id = ?
        GROUP BY validity_status
        """,
        (revision_id,),
    ).fetchall()
    for row in rows:
        status = str(row["validity_status"])
        if status not in counts:
            counts["unverified"] += int(row["item_count"])
            continue
        counts[status] = int(row["item_count"])
    return counts


def list_current_citations(
    connection: sqlite3.Connection,
    object_ids: tuple[str, ...] | None = None,
) -> list[sqlite3.Row]:
    parameters: tuple[str, ...] = ()
    object_filter = ""
    if object_ids:
        placeholders = ", ".join("?" for _ in object_ids)
        object_filter = f" AND o.object_id IN ({placeholders})"
        parameters = tuple(object_ids)
    return connection.execute(
        f"""
        SELECT
            c.*,
            r.object_id,
            r.revision_number,
            o.title AS object_title,
            o.status AS object_status,
            o.canonical_path AS object_path,
            o.last_reviewed AS object_last_reviewed,
            o.review_cadence AS object_review_cadence,
            o.updated_date AS object_updated_date
        FROM citations AS c
        JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
        JOIN knowledge_objects AS o ON o.object_id = r.object_id
        WHERE o.current_revision_id = r.revision_id
        {object_filter}
        ORDER BY o.object_id, c.citation_id
        """,
        parameters,
    ).fetchall()
