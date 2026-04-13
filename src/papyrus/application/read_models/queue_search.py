from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.posture import build_posture_summary
from papyrus.application.role_visibility import filter_queue_items_for_role, normalize_role
from papyrus.application.runtime_projection import RuntimeStateSnapshot
from papyrus.application.ui_projection import build_object_actions, build_ui_projection, ui_projection_payload
from papyrus.domain.entities import SearchHit
from papyrus.domain.policies import citation_health_label, searchable_statuses, status_rank_map
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import load_policy

from .support import (
    _json_dict,
    _object_lifecycle_value,
    _policy_authority,
    _source_sync_value,
    build_status_filter_clause,
    require_runtime_connection,
)

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
            f"WHEN d.object_lifecycle_state = '{status}' THEN {rank}" for status, rank in status_rank.items()
        ) + " ELSE 999 END"
        governance_sql = (
            "CASE d.revision_review_state "
            "WHEN 'approved' THEN 0 "
            "WHEN 'in_review' THEN 1 "
            "WHEN 'draft' THEN 2 "
            "WHEN 'rejected' THEN 3 "
            "WHEN 'superseded' THEN 4 "
            "ELSE 5 END, "
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
                SELECT d.object_id, d.title, d.summary, d.object_type, d.object_lifecycle_state, d.path
                FROM knowledge_search AS s
                JOIN search_documents AS d ON d.object_id = s.object_id
                WHERE knowledge_search MATCH ?
                  AND d.object_lifecycle_state IN {status_clause}
                ORDER BY {case_sql}, {governance_sql}, bm25(knowledge_search), d.title
                LIMIT ?
                """,
                (query, *status_values, limit),
            ).fetchall()
        else:
            like_query = f"%{query}%"
            rows = connection.execute(
                f"""
                SELECT object_id, title, summary, object_type, object_lifecycle_state, path
                FROM search_documents AS d
                WHERE search_text LIKE ?
                  AND object_lifecycle_state IN {status_clause}
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
            object_lifecycle_state=row["object_lifecycle_state"],
            path=row["path"],
        )
        for row in rows
    ]

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

def _review_priority(revision_review_state: str | None) -> int:
    order = {
        "approved": 0,
        "in_review": 1,
        "draft": 2,
        "rejected": 3,
        "superseded": 4,
    }
    return order.get(str(revision_review_state or ""), 9)

def _triage_review_priority(revision_review_state: str | None) -> int:
    order = {
        "in_review": 0,
        "rejected": 1,
        "draft": 2,
        "approved": 3,
        "superseded": 4,
    }
    return order.get(str(revision_review_state or ""), 9)

def _queue_reasons(row: sqlite3.Row) -> list[str]:
    reasons: list[str] = []
    if row["revision_review_state"] != "approved":
        reasons.append(f"review:{row['revision_review_state']}")
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
    revision_review_state: str | None,
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
        revision_review_state=revision_review_state,
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
            revision_review_state=item.get("revision_review_state"),
            freshness_rank=int(item.get("freshness_rank") or 0),
            citation_health_rank=int(item.get("citation_health_rank") or 0),
            ownership_rank=int(item.get("ownership_rank") or 0),
            owner=str(item.get("owner") or ""),
            current_revision_id=str(item["current_revision_id"]) if item.get("current_revision_id") else None,
            audit_events=audit_events,
        )
    return items

def _queue_projection_select() -> str:
    return """
        SELECT
            o.object_id,
            o.current_revision_id,
            o.title,
            o.summary,
            o.object_type,
            o.object_lifecycle_state,
            o.owner,
            o.team,
            o.last_reviewed,
            o.review_cadence,
            COALESCE(d.path, o.canonical_path) AS path,
            o.trust_state,
            o.source_sync_state,
            COALESCE(d.revision_review_state, r.revision_review_state, CASE WHEN o.current_revision_id IS NULL THEN 'draft' ELSE 'unknown' END) AS revision_review_state,
            COALESCE(d.draft_progress_state, r.draft_progress_state, 'ready_for_review') AS draft_progress_state,
            COALESCE(d.freshness_rank, 0) AS freshness_rank,
            COALESCE(d.citation_health_rank, 0) AS citation_health_rank,
            COALESCE(d.ownership_rank, CASE WHEN TRIM(o.owner) = '' THEN 1 ELSE 0 END) AS ownership_rank,
            COALESCE(d.search_text, '') AS search_text
        FROM knowledge_objects AS o
        LEFT JOIN search_documents AS d ON d.object_id = o.object_id
        LEFT JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
    """

def _queue_item_from_projection_row(row: sqlite3.Row) -> dict[str, Any]:
    current_revision_id = str(row["current_revision_id"]) if row["current_revision_id"] is not None else None
    reasons = _queue_reasons(row)
    if current_revision_id is None:
        reasons.insert(0, "no_revision")
    return {
        "object_id": str(row["object_id"]),
        "title": str(row["title"]),
        "summary": str(row["summary"]),
        "object_type": str(row["object_type"]),
        "object_lifecycle_state": _object_lifecycle_value(row),
        "owner": str(row["owner"]),
        "team": str(row["team"]),
        "last_reviewed": str(row["last_reviewed"]),
        "review_cadence": str(row["review_cadence"]),
        "path": str(row["path"]),
        "trust_state": str(row["trust_state"]),
        "revision_review_state": str(row["revision_review_state"]),
        "draft_progress_state": str(row["draft_progress_state"]),
        "source_sync_state": _source_sync_value(row),
        "freshness_rank": int(row["freshness_rank"]),
        "citation_health_rank": int(row["citation_health_rank"]),
        "ownership_rank": int(row["ownership_rank"]),
        "current_revision_id": current_revision_id,
        "reasons": reasons,
    }

def knowledge_queue(
    *,
    limit: int = 200,
    database_path: str | Path = DB_PATH,
    ranking: str = "operator",
    authority: PolicyAuthority | None = None,
    role: str | None = None,
) -> list[dict[str, Any]]:
    current_authority = _policy_authority(authority)
    resolved_role = normalize_role(role)
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            _queue_projection_select(),
        ).fetchall()
        items = [_queue_item_from_projection_row(row) for row in rows]
        _augment_queue_items(connection, items)
        items = filter_queue_items_for_role(items, resolved_role)
        for item in items:
            snapshot = RuntimeStateSnapshot(
                object_lifecycle_state=str(item["object_lifecycle_state"]),
                revision_review_state=str(item["revision_review_state"]),
                draft_progress_state=str(item["draft_progress_state"]),
                source_sync_state=str(item["source_sync_state"]),
                trust_state=str(item["trust_state"]),
            )
            item["ui_projection"] = ui_projection_payload(
                build_ui_projection(
                    state=snapshot,
                    posture=item["posture"],
                    reasons=item["reasons"],
                    actions=build_object_actions(
                        authority=current_authority,
                        state=snapshot,
                        current_revision_id=item["current_revision_id"],
                    ),
                )
            )
        if ranking == "triage":
            items.sort(
                key=lambda item: (
                    _triage_review_priority(item["revision_review_state"]),
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
                    _review_priority(item["revision_review_state"]),
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
    authority: PolicyAuthority | None = None,
    role: str | None = None,
) -> list[dict[str, Any]]:
    current_authority = _policy_authority(authority)
    resolved_role = normalize_role(role)
    connection = require_runtime_connection(database_path)
    try:
        candidate_limit = max(limit * 5, 100)
        has_fts = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'"
        ).fetchone()
        rows_by_object_id: dict[str, sqlite3.Row] = {}
        projection_sql = _queue_projection_select()
        if has_fts:
            try:
                fts_rows = connection.execute(
                    f"""
                    {projection_sql}
                    JOIN knowledge_search AS s ON s.object_id = o.object_id
                    WHERE knowledge_search MATCH ?
                    ORDER BY
                        CASE COALESCE(
                            d.revision_review_state,
                            r.revision_review_state,
                            CASE WHEN o.current_revision_id IS NULL THEN 'draft' ELSE 'unknown' END
                        )
                            WHEN 'approved' THEN 0
                            WHEN 'in_review' THEN 1
                            WHEN 'draft' THEN 2
                            WHEN 'rejected' THEN 3
                            ELSE 4
                        END,
                        CASE o.trust_state
                            WHEN 'trusted' THEN 0
                            WHEN 'weak_evidence' THEN 1
                            WHEN 'suspect' THEN 2
                            WHEN 'stale' THEN 3
                            ELSE 4
                        END,
                        COALESCE(d.citation_health_rank, 0),
                        COALESCE(d.freshness_rank, 0),
                        COALESCE(d.ownership_rank, CASE WHEN TRIM(o.owner) = '' THEN 1 ELSE 0 END),
                        bm25(knowledge_search),
                        o.title
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
            f"""
            {projection_sql}
            WHERE search_text LIKE ?
               OR o.object_id LIKE ?
               OR o.title LIKE ?
               OR o.summary LIKE ?
               OR o.canonical_path LIKE ?
            ORDER BY
                CASE COALESCE(
                    d.revision_review_state,
                    r.revision_review_state,
                    CASE WHEN o.current_revision_id IS NULL THEN 'draft' ELSE 'unknown' END
                )
                    WHEN 'approved' THEN 0
                    WHEN 'in_review' THEN 1
                    WHEN 'draft' THEN 2
                    WHEN 'rejected' THEN 3
                    ELSE 4
                END,
                CASE o.trust_state
                    WHEN 'trusted' THEN 0
                    WHEN 'weak_evidence' THEN 1
                    WHEN 'suspect' THEN 2
                    WHEN 'stale' THEN 3
                    ELSE 4
                END,
                COALESCE(d.citation_health_rank, 0),
                COALESCE(d.freshness_rank, 0),
                COALESCE(d.ownership_rank, CASE WHEN TRIM(o.owner) = '' THEN 1 ELSE 0 END),
                o.title
            LIMIT ?
            """,
            (like_query, like_query, like_query, like_query, like_query, candidate_limit),
        ).fetchall()
        for row in like_rows:
            rows_by_object_id.setdefault(str(row["object_id"]), row)
        rows = list(rows_by_object_id.values())
        items = [_queue_item_from_projection_row(row) for row in rows]
        _augment_queue_items(connection, items)
        items = filter_queue_items_for_role(items, resolved_role)
        for item in items:
            snapshot = RuntimeStateSnapshot(
                object_lifecycle_state=str(item["object_lifecycle_state"]),
                revision_review_state=str(item["revision_review_state"]),
                draft_progress_state=str(item["draft_progress_state"]),
                source_sync_state=str(item["source_sync_state"]),
                trust_state=str(item["trust_state"]),
            )
            item["ui_projection"] = ui_projection_payload(
                build_ui_projection(
                    state=snapshot,
                    posture=item["posture"],
                    reasons=item["reasons"],
                    actions=build_object_actions(
                        authority=current_authority,
                        state=snapshot,
                        current_revision_id=item["current_revision_id"],
                    ),
                )
            )
        items.sort(
            key=lambda item: (
                _review_priority(item["revision_review_state"]),
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
