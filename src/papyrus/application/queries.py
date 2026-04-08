from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from papyrus.application.impact_flow import (
    calculate_blast_radius,
    docs_knowledge_like_warnings,
    documents_missing_list_field,
    find_possible_duplicate_documents,
    missing_owner_documents,
    relationless_documents,
)
from papyrus.application.posture import build_posture_summary
from papyrus.application.validation_flow import orphaned_files
from papyrus.domain.entities import SearchHit
from papyrus.domain.policies import citation_health_label, searchable_statuses, status_rank_map
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    collect_source_paths,
    load_current_runtime_documents,
    load_knowledge_documents,
    load_policy,
    load_taxonomies,
)
from papyrus.infrastructure.markdown.parser import collect_broken_markdown_links
from papyrus.jobs.stale_scan import stale_runtime_objects


CONTENT_HEALTH_SECTIONS = (
    "duplicates",
    "orphaned-files",
    "broken-links",
    "missing-owners",
    "missing-services",
    "missing-systems",
    "missing-tags",
    "isolated-articles",
    "citation-health",
    "suspect-objects",
    "knowledge-like-docs",
)


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


def search_projection(
    query: str,
    limit: int,
    database_path: str | Path = DB_PATH,
    statuses: list[str] | None = None,
) -> list[SearchHit]:
    policy = load_policy()
    requested_statuses = list(statuses or searchable_statuses(policy))
    status_rank = status_rank_map(policy)
    status_clause, status_values = build_status_filter_clause(requested_statuses)

    connection = sqlite3.connect(str(database_path))
    connection.row_factory = sqlite3.Row
    try:
        has_fts = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
        ).fetchone()
        case_sql = "CASE " + " ".join(
            f"WHEN d.status = '{status}' THEN {rank}" for status, rank in status_rank.items()
        ) + " ELSE 999 END"
        governance_sql = (
            "CASE d.approval_state "
            "WHEN 'approved' THEN 0 "
            "WHEN 'in_review' THEN 1 "
            "WHEN 'draft' THEN 2 "
            "WHEN 'rejected' THEN 3 "
            "ELSE 4 END, "
            "CASE d.trust_state "
            "WHEN 'trusted' THEN 0 "
            "WHEN 'weak_evidence' THEN 1 "
            "WHEN 'suspect' THEN 2 "
            "WHEN 'stale' THEN 3 "
            "ELSE 4 END, "
            "d.citation_health_rank, d.freshness_rank, d.ownership_rank"
        )
        if has_fts:
            rows = connection.execute(
                f"""
                SELECT d.object_id, d.title, d.summary, d.object_type, d.status, d.path
                FROM knowledge_search AS s
                JOIN search_documents AS d ON d.object_id = s.object_id
                WHERE knowledge_search MATCH ?
                  AND d.status IN {status_clause}
                ORDER BY {case_sql}, {governance_sql}, bm25(knowledge_search), d.title
                LIMIT ?
                """,
                (query, *status_values, limit),
            ).fetchall()
        else:
            like_query = f"%{query}%"
            rows = connection.execute(
                f"""
                SELECT object_id, title, summary, object_type, status, path
                FROM search_documents AS d
                WHERE search_text LIKE ?
                  AND status IN {status_clause}
                ORDER BY {case_sql}, {governance_sql}, title
                LIMIT ?
                """,
                (like_query, *status_values, limit),
            ).fetchall()
    finally:
        connection.close()

    return [
        SearchHit(
            object_id=row["object_id"],
            title=row["title"],
            summary=row["summary"],
            content_type=row["object_type"],
            status=row["status"],
            path=row["path"],
        )
        for row in rows
    ]


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


def _trust_priority(trust_state: str) -> int:
    order = {
        "trusted": 0,
        "weak_evidence": 1,
        "suspect": 2,
        "stale": 3,
    }
    return order.get(trust_state, 9)


def _triage_trust_priority(trust_state: str) -> int:
    order = {
        "stale": 0,
        "weak_evidence": 1,
        "suspect": 2,
        "trusted": 3,
    }
    return order.get(trust_state, 9)


def _approval_priority(approval_state: str | None) -> int:
    order = {
        "approved": 0,
        "in_review": 1,
        "draft": 2,
        "rejected": 3,
        "superseded": 4,
    }
    return order.get(str(approval_state or ""), 9)


def _triage_approval_priority(approval_state: str | None) -> int:
    order = {
        "in_review": 0,
        "rejected": 1,
        "draft": 2,
        "approved": 3,
        "superseded": 4,
    }
    return order.get(str(approval_state or ""), 9)


def _queue_reasons(row: sqlite3.Row) -> list[str]:
    reasons: list[str] = []
    if row["approval_state"] != "approved":
        reasons.append(f"approval:{row['approval_state']}")
    if int(row["freshness_rank"] or 0) > 0:
        reasons.append("review_due")
    citation_rank = int(row["citation_health_rank"] or 0)
    if citation_rank > 0:
        reasons.append(f"citation:{citation_health_label(citation_rank)}")
    if int(row["ownership_rank"] or 0) > 0:
        reasons.append("ownership_unclear")
    if row["trust_state"] != "trusted":
        reasons.append(f"trust:{row['trust_state']}")
    return reasons


def _load_service_links(
    connection: sqlite3.Connection,
    object_ids: list[str],
) -> dict[str, list[dict[str, str]]]:
    if not object_ids:
        return {}
    placeholders = ", ".join("?" for _ in object_ids)
    rows = connection.execute(
        f"""
        SELECT r.source_entity_id AS object_id, s.service_id, s.service_name
        FROM relationships AS r
        JOIN services AS s ON s.service_id = r.target_entity_id
        WHERE r.source_entity_type = 'knowledge_object'
          AND r.target_entity_type = 'service'
          AND r.source_entity_id IN ({placeholders})
        ORDER BY s.service_name
        """,
        tuple(object_ids),
    ).fetchall()
    mapping: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        mapping.setdefault(str(row["object_id"]), []).append(
            {
                "service_id": str(row["service_id"]),
                "service_name": str(row["service_name"]),
            }
        )
    return mapping


def _load_relationship_counts(
    connection: sqlite3.Connection,
    object_ids: list[str],
) -> dict[str, int]:
    if not object_ids:
        return {}
    placeholders = ", ".join("?" for _ in object_ids)
    rows = connection.execute(
        f"""
        SELECT object_id, COUNT(*) AS item_count
        FROM (
            SELECT source_entity_id AS object_id
            FROM relationships
            WHERE source_entity_type = 'knowledge_object'
              AND source_entity_id IN ({placeholders})
            UNION ALL
            SELECT target_entity_id AS object_id
            FROM relationships
            WHERE target_entity_type = 'knowledge_object'
              AND target_entity_id IN ({placeholders})
        )
        GROUP BY object_id
        """,
        tuple(object_ids) + tuple(object_ids),
    ).fetchall()
    return {str(row["object_id"]): int(row["item_count"] or 0) for row in rows}


def _load_latest_object_audit_events(
    connection: sqlite3.Connection,
    object_ids: list[str],
) -> dict[str, dict[str, dict[str, Any]]]:
    if not object_ids:
        return {}
    placeholders = ", ".join("?" for _ in object_ids)
    rows = connection.execute(
        f"""
        SELECT object_id, event_type, occurred_at, actor, revision_id, details_json
        FROM audit_events
        WHERE object_id IN ({placeholders})
        ORDER BY occurred_at DESC
        """,
        tuple(object_ids),
    ).fetchall()
    mapping: dict[str, dict[str, dict[str, Any]]] = {}
    for row in rows:
        object_id = str(row["object_id"])
        event_type = str(row["event_type"])
        object_events = mapping.setdefault(object_id, {})
        if event_type in object_events:
            continue
        object_events[event_type] = {
            "event_type": event_type,
            "occurred_at": str(row["occurred_at"]),
            "actor": str(row["actor"]),
            "revision_id": str(row["revision_id"]) if row["revision_id"] is not None else None,
            "details": _json_dict(row["details_json"]),
        }
    return mapping


def _build_item_posture(
    *,
    object_id: str,
    trust_state: str,
    approval_state: str | None,
    freshness_rank: int,
    citation_health_rank: int,
    ownership_rank: int,
    owner: str,
    current_revision_id: str | None,
    audit_events: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    object_events = audit_events.get(object_id, {})
    return build_posture_summary(
        trust_state=trust_state,
        approval_state=approval_state,
        freshness_rank=freshness_rank,
        citation_health_rank=citation_health_rank,
        ownership_rank=ownership_rank,
        owner=owner,
        current_revision_id=current_revision_id,
        latest_suspect_event=object_events.get("object_marked_suspect_due_to_change"),
    )


def _augment_queue_items(connection: sqlite3.Connection, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    object_ids = [str(item["object_id"]) for item in items]
    service_links = _load_service_links(connection, object_ids)
    relationship_counts = _load_relationship_counts(connection, object_ids)
    audit_events = _load_latest_object_audit_events(connection, object_ids)
    for item in items:
        object_id = str(item["object_id"])
        item["linked_services"] = service_links.get(object_id, [])
        item["relationship_count"] = relationship_counts.get(object_id, 0)
        item["posture"] = _build_item_posture(
            object_id=object_id,
            trust_state=str(item["trust_state"]),
            approval_state=item.get("approval_state"),
            freshness_rank=int(item.get("freshness_rank") or 0),
            citation_health_rank=int(item.get("citation_health_rank") or 0),
            ownership_rank=int(item.get("ownership_rank") or 0),
            owner=str(item.get("owner") or ""),
            current_revision_id=str(item["current_revision_id"]) if item.get("current_revision_id") else None,
            audit_events=audit_events,
        )
    return items


def knowledge_queue(
    *,
    limit: int = 200,
    database_path: str | Path = DB_PATH,
    ranking: str = "operator",
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                object_id,
                revision_id,
                title,
                object_type,
                status,
                owner,
                team,
                path,
                trust_state,
                approval_state,
                freshness_rank,
                citation_health_rank,
                ownership_rank
            FROM search_documents
            """,
        ).fetchall()
        items = [
            {
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "object_type": str(row["object_type"]),
                "status": str(row["status"]),
                "owner": str(row["owner"]),
                "team": str(row["team"]),
                "path": str(row["path"]),
                "trust_state": str(row["trust_state"]),
                "approval_state": str(row["approval_state"]),
                "freshness_rank": int(row["freshness_rank"]),
                "citation_health_rank": int(row["citation_health_rank"]),
                "ownership_rank": int(row["ownership_rank"]),
                "current_revision_id": str(row["revision_id"]),
                "reasons": _queue_reasons(row),
            }
            for row in rows
        ]
        _augment_queue_items(connection, items)
        if ranking == "triage":
            items.sort(
                key=lambda item: (
                    _triage_approval_priority(item["approval_state"]),
                    _triage_trust_priority(item["trust_state"]),
                    -int(item["citation_health_rank"]),
                    -int(item["freshness_rank"]),
                    -int(item["ownership_rank"]),
                    item["title"],
                    item["object_id"],
                )
            )
        else:
            items.sort(
                key=lambda item: (
                    _approval_priority(item["approval_state"]),
                    _trust_priority(item["trust_state"]),
                    int(item["citation_health_rank"]),
                    int(item["freshness_rank"]),
                    int(item["ownership_rank"]),
                    0 if item["linked_services"] else 1,
                    0 if int(item["relationship_count"]) > 0 else 1,
                    item["title"],
                    item["object_id"],
                )
            )
        return items[:limit]
    finally:
        connection.close()


def search_knowledge_objects(
    query: str,
    *,
    limit: int = 50,
    database_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        candidate_limit = max(limit * 5, 100)
        has_fts = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
        ).fetchone()
        rows_by_object_id: dict[str, sqlite3.Row] = {}
        if has_fts:
            try:
                fts_rows = connection.execute(
                    """
                    SELECT
                        d.object_id,
                        d.title,
                        d.object_type,
                        d.status,
                        d.owner,
                        d.team,
                        d.path,
                        d.trust_state,
                        d.approval_state,
                        d.freshness_rank,
                        d.citation_health_rank,
                        d.ownership_rank
                    FROM knowledge_search AS s
                    JOIN search_documents AS d ON d.object_id = s.object_id
                    WHERE knowledge_search MATCH ?
                    ORDER BY
                        CASE d.approval_state
                            WHEN 'approved' THEN 0
                            WHEN 'in_review' THEN 1
                            WHEN 'draft' THEN 2
                            WHEN 'rejected' THEN 3
                            ELSE 4
                        END,
                        CASE d.trust_state
                            WHEN 'trusted' THEN 0
                            WHEN 'weak_evidence' THEN 1
                            WHEN 'suspect' THEN 2
                            WHEN 'stale' THEN 3
                            ELSE 4
                        END,
                        d.citation_health_rank,
                        d.freshness_rank,
                        d.ownership_rank,
                        bm25(knowledge_search),
                        d.title
                    LIMIT ?
                    """,
                    (query, candidate_limit),
                ).fetchall()
            except sqlite3.OperationalError:
                fts_rows = []
            for row in fts_rows:
                rows_by_object_id[str(row["object_id"])] = row

        like_query = f"%{query}%"
        like_rows = connection.execute(
            """
            SELECT
                object_id,
                title,
                object_type,
                status,
                owner,
                team,
                path,
                trust_state,
                approval_state,
                freshness_rank,
                citation_health_rank,
                ownership_rank
            FROM search_documents
            WHERE search_text LIKE ?
               OR object_id LIKE ?
               OR title LIKE ?
            ORDER BY
                CASE approval_state
                    WHEN 'approved' THEN 0
                    WHEN 'in_review' THEN 1
                    WHEN 'draft' THEN 2
                    WHEN 'rejected' THEN 3
                    ELSE 4
                END,
                CASE trust_state
                    WHEN 'trusted' THEN 0
                    WHEN 'weak_evidence' THEN 1
                    WHEN 'suspect' THEN 2
                    WHEN 'stale' THEN 3
                    ELSE 4
                END,
                citation_health_rank,
                freshness_rank,
                ownership_rank,
                title
            LIMIT ?
            """,
            (like_query, like_query, like_query, candidate_limit),
        ).fetchall()
        for row in like_rows:
            rows_by_object_id.setdefault(str(row["object_id"]), row)
        rows = list(rows_by_object_id.values())
        items = [
            {
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "object_type": str(row["object_type"]),
                "status": str(row["status"]),
                "owner": str(row["owner"]),
                "team": str(row["team"]),
                "path": str(row["path"]),
                "trust_state": str(row["trust_state"]),
                "approval_state": str(row["approval_state"]),
                "freshness_rank": int(row["freshness_rank"]),
                "citation_health_rank": int(row["citation_health_rank"]),
                "ownership_rank": int(row["ownership_rank"]),
                "current_revision_id": None,
                "reasons": _queue_reasons(row),
            }
            for row in rows
        ]
        _augment_queue_items(connection, items)
        items.sort(
            key=lambda item: (
                _approval_priority(item["approval_state"]),
                _trust_priority(item["trust_state"]),
                int(item["citation_health_rank"]),
                int(item["freshness_rank"]),
                int(item["ownership_rank"]),
                0 if item["linked_services"] else 1,
                0 if int(item["relationship_count"]) > 0 else 1,
                item["title"],
            )
        )
        return items[:limit]
    finally:
        connection.close()


def knowledge_object_detail(
    object_id: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        object_row = connection.execute(
            """
            SELECT
                o.*,
                d.approval_state,
                d.freshness_rank,
                d.citation_health_rank,
                d.ownership_rank,
                d.path
            FROM knowledge_objects AS o
            LEFT JOIN search_documents AS d ON d.object_id = o.object_id
            WHERE o.object_id = ?
            """,
            (object_id,),
        ).fetchone()
        if object_row is None:
            raise KnowledgeObjectNotFoundError(f"knowledge object not found: {object_id}")

        current_revision = None
        metadata: dict[str, Any] = {}
        citations: list[dict[str, Any]] = []
        if object_row["current_revision_id"]:
            current_revision = connection.execute(
                """
                SELECT revision_id, revision_number, revision_state, imported_at, change_summary, body_markdown, normalized_payload_json
                FROM knowledge_revisions
                WHERE revision_id = ?
                """,
                (object_row["current_revision_id"],),
            ).fetchone()
        if current_revision is not None:
            metadata = _json_dict(current_revision["normalized_payload_json"])
            citations = [
                {
                    "citation_id": str(row["citation_id"]),
                    "claim_anchor": str(row["claim_anchor"]) if row["claim_anchor"] is not None else None,
                    "source_type": str(row["source_type"]),
                    "source_ref": str(row["source_ref"]),
                    "source_title": str(row["source_title"]),
                    "note": str(row["note"]) if row["note"] is not None else None,
                    "excerpt": str(row["excerpt"]) if row["excerpt"] is not None else None,
                    "captured_at": str(row["captured_at"]) if row["captured_at"] is not None else None,
                    "validity_status": str(row["validity_status"]),
                    "integrity_hash": str(row["integrity_hash"]) if row["integrity_hash"] is not None else None,
                    "evidence_snapshot_path": (
                        str(row["evidence_snapshot_path"]) if row["evidence_snapshot_path"] is not None else None
                    ),
                    "evidence_expiry_at": (
                        str(row["evidence_expiry_at"]) if row["evidence_expiry_at"] is not None else None
                    ),
                    "evidence_last_validated_at": (
                        str(row["evidence_last_validated_at"])
                        if row["evidence_last_validated_at"] is not None
                        else None
                    ),
                }
                for row in connection.execute(
                    """
                    SELECT *
                    FROM citations
                    WHERE revision_id = ?
                    ORDER BY citation_id
                    """,
                    (current_revision["revision_id"],),
                ).fetchall()
            ]
        evidence_status = {
            "total_citations": len(citations),
            "snapshot_count": sum(1 for item in citations if item["evidence_snapshot_path"]),
            "missing_snapshot_count": sum(1 for item in citations if not item["evidence_snapshot_path"]),
            "stale_count": sum(1 for item in citations if item["validity_status"] in {"stale", "broken"}),
            "revalidation_count": sum(
                1 for item in citations if item["validity_status"] != "verified" or not item["evidence_last_validated_at"]
            ),
        }
        evidence_status["summary"] = (
            f"{evidence_status['snapshot_count']} snapshot(s), "
            f"{evidence_status['stale_count']} stale or broken, "
            f"{evidence_status['revalidation_count']} needing revalidation"
        )

        related_services = [
            {
                "service_id": str(row["service_id"]),
                "service_name": str(row["service_name"]),
                "status": str(row["status"]),
                "service_criticality": str(row["service_criticality"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT s.service_id, s.service_name, s.status, s.service_criticality
                FROM relationships AS r
                JOIN services AS s ON s.service_id = r.target_entity_id
                WHERE r.source_entity_type = 'knowledge_object'
                  AND r.source_entity_id = ?
                  AND r.target_entity_type = 'service'
                ORDER BY s.service_name
                """,
                (object_id,),
            ).fetchall()
        ]
        outbound_relationships = [
            {
                "relationship_type": str(row["relationship_type"]),
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "status": str(row["status"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT r.relationship_type, o.object_id, o.title, o.canonical_path, o.status
                FROM relationships AS r
                JOIN knowledge_objects AS o ON o.object_id = r.target_entity_id
                WHERE r.source_entity_type = 'knowledge_object'
                  AND r.source_entity_id = ?
                  AND r.target_entity_type = 'knowledge_object'
                ORDER BY r.relationship_type, o.title
                """,
                (object_id,),
            ).fetchall()
        ]
        inbound_relationships = [
            {
                "relationship_type": str(row["relationship_type"]),
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "status": str(row["status"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT r.relationship_type, o.object_id, o.title, o.canonical_path, o.status
                FROM relationships AS r
                JOIN knowledge_objects AS o ON o.object_id = r.source_entity_id
                WHERE r.target_entity_type = 'knowledge_object'
                  AND r.target_entity_id = ?
                ORDER BY r.relationship_type, o.title
                """,
                (object_id,),
            ).fetchall()
        ]
        unresolved_relationships = [
            {
                "relationship_type": str(row["relationship_type"]),
                "target_entity_type": str(row["target_entity_type"]),
                "target_entity_id": str(row["target_entity_id"]),
            }
            for row in connection.execute(
                """
                SELECT r.relationship_type, r.target_entity_type, r.target_entity_id
                FROM relationships AS r
                LEFT JOIN knowledge_objects AS o
                  ON r.target_entity_type = 'knowledge_object'
                 AND o.object_id = r.target_entity_id
                LEFT JOIN services AS s
                  ON r.target_entity_type = 'service'
                 AND s.service_id = r.target_entity_id
                WHERE r.source_entity_type = 'knowledge_object'
                  AND r.source_entity_id = ?
                  AND (
                    (r.target_entity_type = 'knowledge_object' AND o.object_id IS NULL)
                    OR (r.target_entity_type = 'service' AND s.service_id IS NULL)
                  )
                ORDER BY r.relationship_type, r.target_entity_id
                """,
                (object_id,),
            ).fetchall()
        ]
        audit_events = [
            {
                "event_type": str(row["event_type"]),
                "actor": str(row["actor"]),
                "occurred_at": str(row["occurred_at"]),
                "details": _json_dict(row["details_json"]),
            }
            for row in connection.execute(
                """
                SELECT event_type, actor, occurred_at, details_json
                FROM audit_events
                WHERE object_id = ?
                ORDER BY occurred_at DESC
                LIMIT 20
                """,
                (object_id,),
            ).fetchall()
        ]
        posture = build_posture_summary(
            trust_state=str(object_row["trust_state"]),
            approval_state=str(object_row["approval_state"]) if object_row["approval_state"] is not None else None,
            freshness_rank=int(object_row["freshness_rank"] or 0),
            citation_health_rank=int(object_row["citation_health_rank"] or 0),
            ownership_rank=int(object_row["ownership_rank"] or 0),
            owner=str(object_row["owner"]),
            current_revision_id=str(object_row["current_revision_id"]) if object_row["current_revision_id"] is not None else None,
            latest_suspect_event=next(
                (event for event in audit_events if event["event_type"] == "object_marked_suspect_due_to_change"),
                None,
            ),
        )

        return {
            "object": {
                "object_id": str(object_row["object_id"]),
                "object_type": str(object_row["object_type"]),
                "legacy_type": str(object_row["legacy_type"]) if object_row["legacy_type"] is not None else None,
                "title": str(object_row["title"]),
                "summary": str(object_row["summary"]),
                "status": str(object_row["status"]),
                "owner": str(object_row["owner"]),
                "team": str(object_row["team"]),
                "canonical_path": str(object_row["canonical_path"]),
                "source_type": str(object_row["source_type"]),
                "source_system": str(object_row["source_system"]),
                "source_title": str(object_row["source_title"]),
                "created_date": str(object_row["created_date"]),
                "updated_date": str(object_row["updated_date"]),
                "last_reviewed": str(object_row["last_reviewed"]),
                "review_cadence": str(object_row["review_cadence"]),
                "trust_state": str(object_row["trust_state"]),
                "approval_state": str(object_row["approval_state"]) if object_row["approval_state"] is not None else None,
                "freshness_rank": int(object_row["freshness_rank"] or 0),
                "citation_health_rank": int(object_row["citation_health_rank"] or 0),
                "ownership_rank": int(object_row["ownership_rank"] or 0),
                "tags": [str(item) for item in _json_list(object_row["tags_json"])],
                "systems": [str(item) for item in _json_list(object_row["systems_json"])],
                "path": str(object_row["path"]) if object_row["path"] is not None else str(object_row["canonical_path"]),
            },
            "posture": posture,
            "current_revision": (
                {
                    "revision_id": str(current_revision["revision_id"]),
                    "revision_number": int(current_revision["revision_number"]),
                    "revision_state": str(current_revision["revision_state"]),
                    "imported_at": str(current_revision["imported_at"]),
                    "change_summary": str(current_revision["change_summary"]) if current_revision["change_summary"] is not None else None,
                    "body_markdown": str(current_revision["body_markdown"]),
                }
                if current_revision is not None
                else None
            ),
            "metadata": metadata,
            "citations": citations,
            "evidence_status": evidence_status,
            "related_services": related_services,
            "outbound_relationships": outbound_relationships,
            "inbound_relationships": inbound_relationships,
            "unresolved_relationships": unresolved_relationships,
            "audit_events": audit_events,
        }
    finally:
        connection.close()


def revision_history(
    object_id: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        object_row = connection.execute(
            "SELECT object_id, title, canonical_path, current_revision_id FROM knowledge_objects WHERE object_id = ?",
            (object_id,),
        ).fetchone()
        if object_row is None:
            raise KnowledgeObjectNotFoundError(f"knowledge object not found: {object_id}")

        revisions = connection.execute(
            """
            SELECT revision_id, revision_number, revision_state, imported_at, change_summary, source_path
            FROM knowledge_revisions
            WHERE object_id = ?
            ORDER BY revision_number DESC
            """,
            (object_id,),
        ).fetchall()
        assignments = connection.execute(
            """
            SELECT revision_id, reviewer, state, assigned_at, due_at, notes
            FROM review_assignments
            WHERE object_id = ?
            ORDER BY assigned_at DESC
            """,
            (object_id,),
        ).fetchall()
        assignment_map: dict[str, list[dict[str, Any]]] = {}
        for row in assignments:
            revision_id = str(row["revision_id"]) if row["revision_id"] is not None else ""
            assignment_map.setdefault(revision_id, []).append(
                {
                    "reviewer": str(row["reviewer"]),
                    "state": str(row["state"]),
                    "assigned_at": str(row["assigned_at"]),
                    "due_at": str(row["due_at"]) if row["due_at"] is not None else None,
                    "notes": str(row["notes"]) if row["notes"] is not None else None,
                }
            )
        citation_counts_rows = connection.execute(
            """
            SELECT revision_id, validity_status, COUNT(*) AS item_count
            FROM citations
            WHERE revision_id IN (
                SELECT revision_id FROM knowledge_revisions WHERE object_id = ?
            )
            GROUP BY revision_id, validity_status
            """,
            (object_id,),
        ).fetchall()
        citation_map: dict[str, dict[str, int]] = {}
        for row in citation_counts_rows:
            revision_id = str(row["revision_id"])
            counts = citation_map.setdefault(
                revision_id,
                {"verified": 0, "unverified": 0, "stale": 0, "broken": 0},
            )
            counts[str(row["validity_status"])] = int(row["item_count"])
        audit_events = [
            {
                "event_type": str(row["event_type"]),
                "occurred_at": str(row["occurred_at"]),
                "actor": str(row["actor"]),
                "revision_id": str(row["revision_id"]) if row["revision_id"] is not None else None,
                "details": _json_dict(row["details_json"]),
            }
            for row in connection.execute(
                """
                SELECT event_type, occurred_at, actor, revision_id, details_json
                FROM audit_events
                WHERE object_id = ?
                ORDER BY occurred_at DESC
                LIMIT 50
                """,
                (object_id,),
            ).fetchall()
        ]
        return {
            "object": {
                "object_id": str(object_row["object_id"]),
                "title": str(object_row["title"]),
                "canonical_path": str(object_row["canonical_path"]),
                "current_revision_id": str(object_row["current_revision_id"]) if object_row["current_revision_id"] is not None else None,
            },
            "revisions": [
                {
                    "revision_id": str(row["revision_id"]),
                    "revision_number": int(row["revision_number"]),
                    "revision_state": str(row["revision_state"]),
                    "imported_at": str(row["imported_at"]),
                    "change_summary": str(row["change_summary"]) if row["change_summary"] is not None else None,
                    "source_path": str(row["source_path"]),
                    "is_current": str(row["revision_id"]) == str(object_row["current_revision_id"]),
                    "citations": citation_map.get(
                        str(row["revision_id"]),
                        {"verified": 0, "unverified": 0, "stale": 0, "broken": 0},
                    ),
                    "review_assignments": assignment_map.get(str(row["revision_id"]), []),
                }
                for row in revisions
            ],
            "audit_events": audit_events,
        }
    finally:
        connection.close()


def service_detail(
    service_id_or_name: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        service_row = connection.execute(
            """
            SELECT *
            FROM services
            WHERE service_id = ? OR service_name = ?
            ORDER BY CASE WHEN service_id = ? THEN 0 ELSE 1 END
            LIMIT 1
            """,
            (service_id_or_name, service_id_or_name, service_id_or_name),
        ).fetchone()
        if service_row is None:
            raise ServiceNotFoundError(f"service not found: {service_id_or_name}")

        linked_objects = [
            {
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "status": str(row["status"]),
                "trust_state": str(row["trust_state"]),
                "approval_state": str(row["approval_state"]) if row["approval_state"] is not None else None,
                "citation_health_rank": int(row["citation_health_rank"] or 0),
                "freshness_rank": int(row["freshness_rank"] or 0),
                "relationship_type": str(row["relationship_type"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT
                    o.object_id,
                    o.title,
                    o.canonical_path,
                    o.status,
                    o.trust_state,
                    d.approval_state,
                    d.citation_health_rank,
                    d.freshness_rank,
                    r.relationship_type
                FROM relationships AS r
                JOIN knowledge_objects AS o ON o.object_id = r.source_entity_id
                LEFT JOIN search_documents AS d ON d.object_id = o.object_id
                WHERE r.target_entity_type = 'service'
                  AND r.target_entity_id = ?
                ORDER BY o.title
                """,
                (service_row["service_id"],),
            ).fetchall()
        ]
        canonical_object = None
        if service_row["canonical_object_id"] is not None:
            canonical_object_row = connection.execute(
                "SELECT object_id, title, canonical_path, status FROM knowledge_objects WHERE object_id = ?",
                (service_row["canonical_object_id"],),
            ).fetchone()
            if canonical_object_row is not None:
                canonical_object = {
                    "object_id": str(canonical_object_row["object_id"]),
                    "title": str(canonical_object_row["title"]),
                    "path": str(canonical_object_row["canonical_path"]),
                    "status": str(canonical_object_row["status"]),
                }

        return {
            "service": {
                "service_id": str(service_row["service_id"]),
                "service_name": str(service_row["service_name"]),
                "canonical_object_id": str(service_row["canonical_object_id"]) if service_row["canonical_object_id"] is not None else None,
                "owner": str(service_row["owner"]) if service_row["owner"] is not None else None,
                "team": str(service_row["team"]) if service_row["team"] is not None else None,
                "status": str(service_row["status"]),
                "service_criticality": str(service_row["service_criticality"]),
                "support_entrypoints": [str(item) for item in _json_list(service_row["support_entrypoints_json"])],
                "dependencies": [str(item) for item in _json_list(service_row["dependencies_json"])],
                "common_failure_modes": [str(item) for item in _json_list(service_row["common_failure_modes_json"])],
                "source": str(service_row["source"]),
            },
            "canonical_object": canonical_object,
            "linked_objects": linked_objects,
            "service_posture": {
                "linked_object_count": len(linked_objects),
                "non_approved_count": sum(1 for item in linked_objects if item["approval_state"] != "approved"),
                "degraded_count": sum(1 for item in linked_objects if item["trust_state"] != "trusted"),
            },
        }
    finally:
        connection.close()


def service_catalog(
    *,
    database_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                s.service_id,
                s.service_name,
                s.status,
                s.service_criticality,
                s.owner,
                s.team,
                s.canonical_object_id,
                COUNT(DISTINCT r.source_entity_id) AS linked_object_count
            FROM services AS s
            LEFT JOIN relationships AS r
              ON r.target_entity_type = 'service'
             AND r.target_entity_id = s.service_id
            GROUP BY
                s.service_id,
                s.service_name,
                s.status,
                s.service_criticality,
                s.owner,
                s.team,
                s.canonical_object_id
            ORDER BY
                CASE s.service_criticality
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'moderate' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END,
                s.service_name
            """
        ).fetchall()
        return [
            {
                "service_id": str(row["service_id"]),
                "service_name": str(row["service_name"]),
                "status": str(row["status"]),
                "service_criticality": str(row["service_criticality"]),
                "owner": str(row["owner"]) if row["owner"] is not None else "",
                "team": str(row["team"]) if row["team"] is not None else "",
                "canonical_object_id": str(row["canonical_object_id"]) if row["canonical_object_id"] is not None else None,
                "linked_object_count": int(row["linked_object_count"] or 0),
            }
            for row in rows
        ]
    finally:
        connection.close()


def trust_dashboard(
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        object_count = int(
            connection.execute("SELECT COUNT(*) FROM knowledge_objects").fetchone()[0]
        )
        trust_counts = {
            str(row["trust_state"]): int(row["item_count"])
            for row in connection.execute(
                "SELECT trust_state, COUNT(*) AS item_count FROM knowledge_objects GROUP BY trust_state"
            ).fetchall()
        }
        approval_counts = {
            str(row["approval_state"]): int(row["item_count"])
            for row in connection.execute(
                "SELECT approval_state, COUNT(*) AS item_count FROM search_documents GROUP BY approval_state"
            ).fetchall()
        }
        citation_health_counts = {
            citation_health_label(int(row["citation_health_rank"])): int(row["item_count"])
            for row in connection.execute(
                "SELECT citation_health_rank, COUNT(*) AS item_count FROM search_documents GROUP BY citation_health_rank"
            ).fetchall()
        }
        validation_runs = [
            {
                "run_type": str(row["run_type"]),
                "status": str(row["status"]),
                "finding_count": int(row["finding_count"]),
                "completed_at": str(row["completed_at"]),
                "details": _json_dict(row["details_json"]),
            }
            for row in connection.execute(
                """
                SELECT run_type, status, finding_count, completed_at, details_json
                FROM validation_runs
                ORDER BY completed_at DESC
                LIMIT 20
                """
            ).fetchall()
        ]
        evidence_counts = {
            str(row["validity_status"]): int(row["item_count"])
            for row in connection.execute(
                "SELECT validity_status, COUNT(*) AS item_count FROM citations GROUP BY validity_status"
            ).fetchall()
        }
        latest_validation = validation_runs[0] if validation_runs else None
        validation_posture = {
            "summary": "No validation runs recorded",
            "detail": "Papyrus cannot prove the runtime was recently validated.",
            "action": "Rebuild the runtime or record a validation run before using the manage surface for governance decisions.",
            "severity": "serious",
        }
        if latest_validation is not None:
            validation_posture = {
                "summary": f"Latest validation: {latest_validation['run_type']}",
                "detail": (
                    f"Most recent validation finished with status '{latest_validation['status']}' "
                    f"and {latest_validation['finding_count']} finding(s)."
                ),
                "action": "Inspect validation run history for the exact findings before approving risky changes.",
                "severity": "informational" if latest_validation["status"] == "passed" else "serious",
            }
        return {
            "object_count": object_count,
            "trust_counts": trust_counts,
            "approval_counts": approval_counts,
            "citation_health_counts": citation_health_counts,
            "evidence_counts": evidence_counts,
            "queue": knowledge_queue(limit=25, database_path=database_path, ranking="triage"),
            "validation_runs": validation_runs,
            "validation_posture": validation_posture,
        }
    finally:
        connection.close()


def manage_queue(
    *,
    limit: int = 200,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                o.object_id,
                o.object_type,
                o.title,
                o.status,
                o.owner,
                o.team,
                o.canonical_path,
                o.trust_state,
                o.current_revision_id,
                COALESCE(r.revision_id, '') AS revision_id,
                COALESCE(r.revision_number, 0) AS revision_number,
                COALESCE(r.revision_state, 'none') AS revision_state,
                COALESCE(r.imported_at, '') AS imported_at,
                COALESCE(r.change_summary, '') AS change_summary,
                COALESCE(d.approval_state, CASE
                    WHEN r.revision_state = 'in_review' THEN 'in_review'
                    WHEN r.revision_state = 'draft' THEN 'draft'
                    WHEN r.revision_state = 'rejected' THEN 'rejected'
                    WHEN r.revision_state = 'approved' THEN 'approved'
                    ELSE 'unknown'
                END) AS approval_state,
                COALESCE(d.freshness_rank, 0) AS freshness_rank,
                COALESCE(d.citation_health_rank, 0) AS citation_health_rank,
                COALESCE(d.ownership_rank, CASE WHEN TRIM(o.owner) = '' THEN 1 ELSE 0 END) AS ownership_rank,
                COALESCE(d.path, o.canonical_path) AS path
            FROM knowledge_objects AS o
            LEFT JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
            LEFT JOIN search_documents AS d ON d.object_id = o.object_id
            ORDER BY
                CASE COALESCE(r.revision_state, 'none')
                    WHEN 'in_review' THEN 0
                    WHEN 'draft' THEN 1
                    WHEN 'rejected' THEN 2
                    WHEN 'none' THEN 3
                    ELSE 4
                END,
                CASE o.trust_state
                    WHEN 'stale' THEN 0
                    WHEN 'weak_evidence' THEN 1
                    WHEN 'suspect' THEN 2
                    ELSE 3
                END,
                freshness_rank DESC,
                citation_health_rank DESC,
                o.title
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        assignment_rows = connection.execute(
            """
            SELECT revision_id, reviewer, state, assigned_at, due_at, notes
            FROM review_assignments
            WHERE revision_id IS NOT NULL
            ORDER BY assigned_at DESC
            """
        ).fetchall()
        assignment_map: dict[str, dict[str, Any]] = {}
        for row in assignment_rows:
            revision_id = str(row["revision_id"])
            if revision_id in assignment_map:
                continue
            assignment_map[revision_id] = {
                "reviewer": str(row["reviewer"]),
                "state": str(row["state"]),
                "assigned_at": str(row["assigned_at"]),
                "due_at": str(row["due_at"]) if row["due_at"] is not None else None,
                "notes": str(row["notes"]) if row["notes"] is not None else None,
            }

        items: list[dict[str, Any]] = []
        for row in rows:
            item = {
                "object_id": str(row["object_id"]),
                "object_type": str(row["object_type"]),
                "title": str(row["title"]),
                "status": str(row["status"]),
                "owner": str(row["owner"]),
                "team": str(row["team"]),
                "path": str(row["path"]),
                "trust_state": str(row["trust_state"]),
                "approval_state": str(row["approval_state"]),
                "freshness_rank": int(row["freshness_rank"]),
                "citation_health_rank": int(row["citation_health_rank"]),
                "ownership_rank": int(row["ownership_rank"]),
                "current_revision_id": str(row["current_revision_id"]) if row["current_revision_id"] is not None else None,
                "revision_id": str(row["revision_id"]) or None,
                "revision_number": int(row["revision_number"] or 0),
                "revision_state": str(row["revision_state"]),
                "change_summary": str(row["change_summary"]) if row["change_summary"] else None,
                "imported_at": str(row["imported_at"]) if row["imported_at"] else None,
                "assignment": assignment_map.get(str(row["revision_id"])),
                "reasons": [],
            }
            if item["current_revision_id"] is None:
                item["reasons"].append("no_revision")
            if item["revision_state"] in {"draft", "rejected"}:
                item["reasons"].append(f"revision:{item['revision_state']}")
            if item["revision_state"] == "in_review":
                item["reasons"].append("awaiting_review")
            if item["approval_state"] != "approved":
                item["reasons"].append(f"approval:{item['approval_state']}")
            if item["freshness_rank"] > 0:
                item["reasons"].append("review_due")
            if item["citation_health_rank"] > 0:
                item["reasons"].append(f"citation:{citation_health_label(item['citation_health_rank'])}")
            if item["ownership_rank"] > 0 or not item["owner"].strip():
                item["reasons"].append("ownership_unclear")
            if item["trust_state"] != "trusted":
                item["reasons"].append(f"trust:{item['trust_state']}")
            items.append(item)
        _augment_queue_items(connection, items)

        return {
            "items": items,
            "review_required": [item for item in items if item["revision_state"] == "in_review"],
            "stale_items": [item for item in items if item["freshness_rank"] > 0],
            "suspect_items": [item for item in items if item["trust_state"] != "trusted" or item["approval_state"] != "approved"],
            "weak_evidence_items": [item for item in items if item["citation_health_rank"] > 0],
            "ownership_items": [item for item in items if item["ownership_rank"] > 0 or not item["owner"].strip()],
            "draft_items": [item for item in items if item["current_revision_id"] is None or item["revision_state"] in {"draft", "rejected"}],
        }
    finally:
        connection.close()


def review_detail(
    object_id: str,
    revision_id: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        detail = knowledge_object_detail(object_id, database_path=database_path)
        history = revision_history(object_id, database_path=database_path)
        revision = next((item for item in history["revisions"] if item["revision_id"] == revision_id), None)
        if revision is None:
            raise KnowledgeObjectNotFoundError(f"revision not found for {object_id}: {revision_id}")
        revision_row = connection.execute(
            """
            SELECT revision_id, object_id, revision_number, revision_state, imported_at, change_summary, body_markdown, normalized_payload_json
            FROM knowledge_revisions
            WHERE revision_id = ?
            """,
            (revision_id,),
        ).fetchone()
        if revision_row is None:
            raise KnowledgeObjectNotFoundError(f"revision not found for {object_id}: {revision_id}")
        citations = [
            {
                "citation_id": str(row["citation_id"]),
                "source_title": str(row["source_title"]),
                "source_type": str(row["source_type"]),
                "source_ref": str(row["source_ref"]),
                "note": str(row["note"]) if row["note"] is not None else None,
                "validity_status": str(row["validity_status"]),
            }
            for row in connection.execute(
                """
                SELECT citation_id, source_title, source_type, source_ref, note, validity_status
                FROM citations
                WHERE revision_id = ?
                ORDER BY citation_id
                """,
                (revision_id,),
            ).fetchall()
        ]
        revision_audit = [
            {
                "event_type": str(row["event_type"]),
                "occurred_at": str(row["occurred_at"]),
                "actor": str(row["actor"]),
                "details": _json_dict(row["details_json"]),
            }
            for row in connection.execute(
                """
                SELECT event_type, occurred_at, actor, details_json
                FROM audit_events
                WHERE object_id = ? AND revision_id = ?
                ORDER BY occurred_at DESC
                LIMIT 25
                """,
                (object_id, revision_id),
            ).fetchall()
        ]
        return {
            "object": detail["object"],
            "current_revision": detail["current_revision"],
            "revision": {
                **revision,
                "body_markdown": str(revision_row["body_markdown"]),
                "metadata": _json_dict(revision_row["normalized_payload_json"]),
            },
            "assignments": revision["review_assignments"],
            "citations": citations,
            "audit_events": revision_audit,
        }
    finally:
        connection.close()


def audit_view(
    *,
    object_id: str | None = None,
    limit: int = 100,
    database_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        if object_id:
            rows = connection.execute(
                """
                SELECT event_id, event_type, occurred_at, actor, object_id, revision_id, details_json
                FROM audit_events
                WHERE object_id = ?
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (object_id, limit),
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT event_id, event_type, occurred_at, actor, object_id, revision_id, details_json
                FROM audit_events
                ORDER BY occurred_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            {
                "event_id": str(row["event_id"]),
                "event_type": str(row["event_type"]),
                "occurred_at": str(row["occurred_at"]),
                "actor": str(row["actor"]),
                "object_id": str(row["object_id"]) if row["object_id"] is not None else None,
                "revision_id": str(row["revision_id"]) if row["revision_id"] is not None else None,
                "details": _json_dict(row["details_json"]),
            }
            for row in rows
        ]
    finally:
        connection.close()


def validation_run_history(
    *,
    limit: int = 50,
    database_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT run_id, run_type, started_at, completed_at, status, finding_count, details_json
            FROM validation_runs
            ORDER BY completed_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {
                "run_id": str(row["run_id"]),
                "run_type": str(row["run_type"]),
                "started_at": str(row["started_at"]),
                "completed_at": str(row["completed_at"]),
                "status": str(row["status"]),
                "finding_count": int(row["finding_count"]),
                "details": _json_dict(row["details_json"]),
            }
            for row in rows
        ]
    finally:
        connection.close()


def _recent_events(
    connection: sqlite3.Connection,
    *,
    entity_type: str,
    entity_ids: list[str],
    limit: int = 10,
) -> list[dict[str, Any]]:
    if not entity_ids:
        return []
    placeholders = ", ".join("?" for _ in entity_ids)
    rows = connection.execute(
        f"""
        SELECT event_id, event_type, source, entity_type, entity_id, occurred_at, actor, payload_json
        FROM events
        WHERE entity_type = ?
          AND entity_id IN ({placeholders})
        ORDER BY occurred_at DESC, event_id DESC
        LIMIT ?
        """,
        (entity_type, *entity_ids, limit),
    ).fetchall()
    return [
        {
            "event_id": str(row["event_id"]),
            "event_type": str(row["event_type"]),
            "source": str(row["source"]),
            "entity_type": str(row["entity_type"]),
            "entity_id": str(row["entity_id"]),
            "occurred_at": str(row["occurred_at"]),
            "actor": str(row["actor"]),
            "payload": _json_dict(row["payload_json"]),
        }
        for row in rows
    ]


def impact_view_for_object(
    object_id: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        object_row = connection.execute(
            "SELECT object_id, title, canonical_path, trust_state FROM knowledge_objects WHERE object_id = ?",
            (object_id,),
        ).fetchone()
        if object_row is None:
            raise KnowledgeObjectNotFoundError(f"knowledge object not found: {object_id}")

        inbound_relationships = [
            {
                "relationship_type": str(row["relationship_type"]),
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "trust_state": str(row["trust_state"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT r.relationship_type, o.object_id, o.title, o.canonical_path, o.trust_state
                FROM relationships AS r
                JOIN knowledge_objects AS o ON o.object_id = r.source_entity_id
                WHERE r.target_entity_type = 'knowledge_object'
                  AND r.target_entity_id = ?
                ORDER BY r.relationship_type, o.title
                """,
                (object_id,),
            ).fetchall()
        ]
        citation_dependents = [
            {
                "object_id": str(row["object_id"]),
                "title": str(row["title"]),
                "path": str(row["canonical_path"]),
                "trust_state": str(row["trust_state"]),
                "citation_status": str(row["validity_status"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT o.object_id, o.title, o.canonical_path, o.trust_state, c.validity_status
                FROM citations AS c
                JOIN knowledge_revisions AS r ON r.revision_id = c.revision_id
                JOIN knowledge_objects AS o ON o.object_id = r.object_id
                WHERE o.current_revision_id = r.revision_id
                  AND c.source_ref = ?
                  AND o.object_id != ?
                ORDER BY o.title
                """,
                (object_row["canonical_path"], object_id),
            ).fetchall()
        ]
        service_links = [
            {
                "service_id": str(row["service_id"]),
                "service_name": str(row["service_name"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT s.service_id, s.service_name
                FROM relationships AS r
                JOIN services AS s ON s.service_id = r.target_entity_id
                WHERE r.source_entity_type = 'knowledge_object'
                  AND r.source_entity_id = ?
                  AND r.target_entity_type = 'service'
                ORDER BY s.service_name
                """,
                (object_id,),
            ).fetchall()
        ]

        blast_radius = [
            item
            for item in calculate_blast_radius(
                connection,
                changed_entity_type="knowledge_object",
                changed_entity_id=object_id,
            )
            if item["object_id"] != object_id
        ]
        recent_events = _recent_events(connection, entity_type="knowledge_object", entity_ids=[object_id])
        current_impact = {
            "what_changed": (
                recent_events[0]["payload"].get("summary")
                if recent_events
                else "No direct change event recorded. Structural impact is inferred from current relationships and citations."
            ),
            "why_impacted": (
                recent_events[0]["payload"].get("reason")
                if recent_events
                else "Objects that depend on or cite this object would require revalidation if it changes."
            ),
            "propagation_path": [f"object:{object_id}"],
            "revalidate": [
                "Review dependent runbooks, known errors, and service records for stale assumptions.",
                "Revalidate any citations that point at this canonical path.",
            ],
        }

        return {
            "entity_type": "knowledge_object",
            "entity": {
                "object_id": str(object_row["object_id"]),
                "title": str(object_row["title"]),
                "path": str(object_row["canonical_path"]),
                "trust_state": str(object_row["trust_state"]),
            },
            "current_impact": current_impact,
            "recent_events": recent_events,
            "inbound_relationships": inbound_relationships,
            "citation_dependents": citation_dependents,
            "related_services": service_links,
            "impacted_objects": blast_radius,
        }
    finally:
        connection.close()


def impact_view_for_service(
    service_id_or_name: str,
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    connection = require_runtime_connection(database_path)
    try:
        detail = service_detail(service_id_or_name, database_path=database_path)
        entity_ids = [detail["service"]["service_id"], detail["service"]["service_name"]]
        recent_events = _recent_events(connection, entity_type="service", entity_ids=entity_ids)
        current_impact = {
            "what_changed": (
                recent_events[0]["payload"].get("summary")
                if recent_events
                else "No direct service change event recorded. Impact is inferred from linked knowledge and dependency relationships."
            ),
            "why_impacted": (
                recent_events[0]["payload"].get("reason")
                if recent_events
                else "Knowledge linked to this service is in blast radius when the service changes."
            ),
            "propagation_path": [f"service:{detail['service']['service_name']}"],
            "revalidate": [
                "Review linked runbooks, known errors, and service records against the changed service state.",
            ],
        }
        return {
            "entity_type": "service",
            "entity": detail["service"],
            "current_impact": current_impact,
            "recent_events": recent_events,
            "impacted_objects": calculate_blast_radius(
                connection,
                changed_entity_type="service",
                changed_entity_id=service_id_or_name,
            ),
        }
    finally:
        connection.close()


def stale_projection(
    *,
    as_of,
    include_deprecated: bool = False,
    database_path: str | Path = DB_PATH,
) -> list[tuple[int, str, str, str, object]]:
    taxonomies = load_taxonomies()
    statuses = {"active"}
    if include_deprecated:
        statuses.add("deprecated")

    connection = runtime_connection(database_path)
    if connection is None:
        documents = load_knowledge_documents(load_policy())
        from papyrus.jobs.stale_scan import stale_documents

        return [
            (days_overdue, document.metadata["id"], document.metadata["title"], document.relative_path, due_date)
            for days_overdue, document, due_date in stale_documents(documents, taxonomies, as_of, statuses)
        ]

    try:
        return [
            (row.days_overdue, row.object_id, row.title, row.path, row.due_date)
            for row in stale_runtime_objects(connection, taxonomies, as_of, statuses)
        ]
    finally:
        connection.close()


def collect_content_health_sections(
    selected: list[str] | None = None,
    database_path: str | Path = DB_PATH,
) -> dict[str, list[str]]:
    policy = load_policy()
    source_documents = load_knowledge_documents(policy)
    selected_sections = selected or list(CONTENT_HEALTH_SECTIONS)
    outputs: dict[str, list[str]] = {}
    connection = runtime_connection(database_path)
    runtime_documents = load_current_runtime_documents(connection) if connection is not None else source_documents

    try:
        if "duplicates" in selected_sections:
            duplicates = find_possible_duplicate_documents(
                runtime_documents,
                float(policy["duplicate_detection"]["title_similarity_threshold"]),
            )
            outputs["duplicates"] = [
                (
                    f"{duplicate.similarity:.2f} | {duplicate.left_title} | {duplicate.left_path} | "
                    f"{duplicate.right_title} | {duplicate.right_path}"
                )
                for duplicate in duplicates
            ]

        if "orphaned-files" in selected_sections:
            outputs["orphaned-files"] = orphaned_files(policy, source_documents)

        if "broken-links" in selected_sections:
            markdown_paths = (
                collect_root_markdown_paths()
                + collect_docs_source_paths()
                + collect_decision_paths()
                + collect_source_paths(policy)
            )
            broken_links = collect_broken_markdown_links(markdown_paths)
            outputs["broken-links"] = [
                f"{item.source_path} | {item.target} | {item.reason}" for item in broken_links
            ]

        if "missing-owners" in selected_sections:
            outputs["missing-owners"] = [
                f"{document.metadata['id']} | {document.relative_path}"
                for document in missing_owner_documents(runtime_documents)
            ]

        if "missing-services" in selected_sections:
            outputs["missing-services"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "services")
            ]

        if "missing-systems" in selected_sections:
            outputs["missing-systems"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "systems")
            ]

        if "missing-tags" in selected_sections:
            outputs["missing-tags"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in documents_missing_list_field(runtime_documents, "tags")
            ]

        if "isolated-articles" in selected_sections:
            outputs["isolated-articles"] = [
                f"{document.metadata['id']} | {document.metadata['title']} | {document.relative_path}"
                for document in relationless_documents(runtime_documents)
            ]

        if "citation-health" in selected_sections:
            outputs["citation-health"] = []
            if connection is not None:
                rows = connection.execute(
                    """
                    SELECT
                        o.object_id,
                        o.title,
                        o.canonical_path,
                        SUM(CASE WHEN c.validity_status = 'verified' THEN 1 ELSE 0 END) AS verified_count,
                        SUM(CASE WHEN c.validity_status = 'unverified' THEN 1 ELSE 0 END) AS unverified_count,
                        SUM(CASE WHEN c.validity_status = 'stale' THEN 1 ELSE 0 END) AS stale_count,
                        SUM(CASE WHEN c.validity_status = 'broken' THEN 1 ELSE 0 END) AS broken_count
                    FROM knowledge_objects AS o
                    JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
                    LEFT JOIN citations AS c ON c.revision_id = r.revision_id
                    GROUP BY o.object_id, o.title, o.canonical_path
                    HAVING SUM(CASE WHEN c.validity_status = 'unverified' THEN 1 ELSE 0 END) > 0
                        OR SUM(CASE WHEN c.validity_status = 'stale' THEN 1 ELSE 0 END) > 0
                        OR SUM(CASE WHEN c.validity_status = 'broken' THEN 1 ELSE 0 END) > 0
                    ORDER BY broken_count DESC, stale_count DESC, unverified_count DESC, o.title
                    """
                ).fetchall()
                outputs["citation-health"] = [
                    (
                        f"{row['object_id']} | {row['title']} | {row['canonical_path']} | "
                        f"verified={int(row['verified_count'] or 0)} | "
                        f"unverified={int(row['unverified_count'] or 0)} | "
                        f"stale={int(row['stale_count'] or 0)} | "
                        f"broken={int(row['broken_count'] or 0)}"
                    )
                    for row in rows
                ]

        if "suspect-objects" in selected_sections:
            outputs["suspect-objects"] = []
            if connection is not None:
                rows = connection.execute(
                    """
                    SELECT object_id, title, path, status, approval_state, trust_state, freshness_rank, citation_health_rank, ownership_rank
                    FROM search_documents
                    WHERE trust_state != 'trusted'
                       OR approval_state != 'approved'
                       OR freshness_rank > 0
                       OR citation_health_rank > 0
                       OR ownership_rank > 0
                    ORDER BY
                        CASE trust_state
                            WHEN 'stale' THEN 0
                            WHEN 'weak_evidence' THEN 1
                            WHEN 'suspect' THEN 2
                            ELSE 3
                        END,
                        title
                    """
                ).fetchall()
                outputs["suspect-objects"] = [
                    (
                        f"{row['object_id']} | {row['title']} | {row['path']} | "
                        f"status={row['status']} | approval={row['approval_state']} | trust={row['trust_state']} | "
                        f"freshness_rank={row['freshness_rank']} | citation_health_rank={row['citation_health_rank']} | "
                        f"ownership_rank={row['ownership_rank']}"
                    )
                    for row in rows
                ]

        if "knowledge-like-docs" in selected_sections:
            outputs["knowledge-like-docs"] = [
                (
                    f"{warning.score} | {warning.path} | may contain operational-knowledge signals | "
                    f"{'; '.join(warning.signals)}"
                )
                for warning in docs_knowledge_like_warnings()
            ]

        return outputs
    finally:
        if connection is not None:
            connection.close()
