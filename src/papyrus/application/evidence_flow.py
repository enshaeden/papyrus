from __future__ import annotations

import datetime as dt
import sqlite3
from dataclasses import dataclass
from pathlib import Path

from papyrus.application.runtime_projection import refresh_current_object_projection
from papyrus.domain.actor import require_actor_id
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.citation_repo import (
    update_citation_evidence_fields,
    update_citation_validity_status,
)
from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies
from papyrus.infrastructure.search.indexer import fts5_available
from papyrus.infrastructure.storage.evidence_store import EvidenceStore


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


@dataclass(frozen=True)
class EvidenceFlowResult:
    object_id: str
    citation_ids: list[str]
    snapshot_path: str | None = None


def _open_connection(database_path: Path) -> sqlite3.Connection:
    connection = open_runtime_database(Path(database_path), minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    apply_runtime_schema(connection, has_fts5=fts5_available(connection))
    connection.execute(
        "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
        (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
    )
    return connection


def _current_citations_for_object(connection: sqlite3.Connection, object_id: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT c.*, o.object_id
        FROM citations AS c
        JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
        JOIN knowledge_objects AS o ON o.object_id = r.object_id
        WHERE o.object_id = ?
          AND o.current_revision_id = r.revision_id
        ORDER BY c.citation_id
        """,
        (object_id,),
    ).fetchall()


def _citation_for_id(connection: sqlite3.Connection, citation_id: str) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT c.*, o.object_id
        FROM citations AS c
        JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
        JOIN knowledge_objects AS o ON o.object_id = r.object_id
        WHERE c.citation_id = ?
          AND o.current_revision_id = r.revision_id
        """,
        (citation_id,),
    ).fetchone()


def _refresh_object(connection: sqlite3.Connection, object_id: str) -> None:
    refresh_current_object_projection(connection, object_id=object_id, taxonomies=load_taxonomies())


def mark_evidence_stale(
    *,
    database_path: Path = DB_PATH,
    actor: str,
    reason: str,
    citation_id: str | None = None,
    object_id: str | None = None,
) -> EvidenceFlowResult:
    actor = require_actor_id(actor)
    if not citation_id and not object_id:
        raise ValueError("citation_id or object_id is required")
    connection = _open_connection(Path(database_path))
    try:
        rows = [_citation_for_id(connection, citation_id)] if citation_id else _current_citations_for_object(connection, object_id or "")
        citations = [row for row in rows if row is not None]
        if not citations:
            raise ValueError("no current citations matched the requested evidence target")
        target_object_id = str(citations[0]["object_id"])
        citation_ids: list[str] = []
        for row in citations:
            current_id = str(row["citation_id"])
            citation_ids.append(current_id)
            update_citation_validity_status(connection, current_id, "stale")
            insert_audit_event(
                connection,
                event_id=f"evidence-stale-{current_id}",
                event_type="evidence_marked_stale",
                occurred_at=_now_utc().isoformat(),
                actor=actor,
                object_id=str(row["object_id"]),
                revision_id=str(row["revision_id"]),
                details_json=json_dump(
                    {
                        "citation_id": current_id,
                        "reason": reason,
                        "source_ref": str(row["source_ref"]),
                    }
                ),
            )
        _refresh_object(connection, target_object_id)
        connection.commit()
        return EvidenceFlowResult(object_id=target_object_id, citation_ids=citation_ids)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def request_evidence_revalidation(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    notes: str | None = None,
) -> EvidenceFlowResult:
    actor = require_actor_id(actor)
    connection = _open_connection(Path(database_path))
    try:
        citations = _current_citations_for_object(connection, object_id)
        citation_ids = [str(row["citation_id"]) for row in citations]
        insert_audit_event(
            connection,
            event_id=f"evidence-revalidate-{object_id}-{_now_utc().strftime('%Y%m%d%H%M%S')}",
            event_type="evidence_revalidation_requested",
            occurred_at=_now_utc().isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=str(citations[0]["revision_id"]) if citations else None,
            details_json=json_dump(
                {
                    "citation_ids": citation_ids,
                    "notes": notes,
                }
            ),
        )
        connection.commit()
        return EvidenceFlowResult(object_id=object_id, citation_ids=citation_ids)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def attach_evidence_snapshot(
    *,
    database_path: Path = DB_PATH,
    citation_id: str,
    snapshot_source_path: str | Path,
    actor: str,
    expires_at: str | dt.datetime | None = None,
    root_path: Path = ROOT,
) -> EvidenceFlowResult:
    actor = require_actor_id(actor)
    connection = _open_connection(Path(database_path))
    try:
        citation = _citation_for_id(connection, citation_id)
        if citation is None:
            raise ValueError(f"citation not found: {citation_id}")
        store = EvidenceStore(root_path=root_path)
        snapshot = store.store_snapshot(citation_id=citation_id, source_path=snapshot_source_path)
        expiry_value = None
        if expires_at is not None:
            if isinstance(expires_at, dt.datetime):
                expiry_value = expires_at.isoformat()
            else:
                expiry_value = str(expires_at)
        validated_at = _now_utc().isoformat()
        update_citation_evidence_fields(
            connection,
            citation_id=citation_id,
            validity_status="verified",
            integrity_hash=snapshot.integrity_hash,
            evidence_snapshot_path=snapshot.relative_path,
            evidence_expiry_at=expiry_value,
            evidence_last_validated_at=validated_at,
        )
        insert_audit_event(
            connection,
            event_id=f"evidence-snapshot-{citation_id}",
            event_type="evidence_snapshot_attached",
            occurred_at=validated_at,
            actor=actor,
            object_id=str(citation["object_id"]),
            revision_id=str(citation["revision_id"]),
            details_json=json_dump(
                {
                    "citation_id": citation_id,
                    "snapshot_path": snapshot.relative_path,
                    "evidence_expiry_at": expiry_value,
                }
            ),
        )
        _refresh_object(connection, str(citation["object_id"]))
        connection.commit()
        return EvidenceFlowResult(
            object_id=str(citation["object_id"]),
            citation_ids=[citation_id],
            snapshot_path=snapshot.relative_path,
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
