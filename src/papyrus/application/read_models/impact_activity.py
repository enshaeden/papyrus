from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from papyrus.application.impact_flow import calculate_blast_radius
from papyrus.infrastructure.paths import DB_PATH

from .services_dashboard import service_detail
from .support import KnowledgeObjectNotFoundError, _json_dict, require_runtime_connection


def _event_group(event_type: str, payload: dict[str, Any]) -> str:
    if event_type == "service_change":
        return "service_changes"
    if event_type.startswith("evidence_"):
        return "evidence_degradation"
    if event_type.startswith("validation_") or event_type == "validation_run_recorded":
        status = str(payload.get("status") or "").strip()
        return (
            "validation_failures"
            if status in {"failed", "error"} or event_type == "validation_failure"
            else "validation_activity"
        )
    if event_type == "object_marked_suspect_due_to_change":
        return "manual_suspect_marks"
    if event_type.startswith("revision_") or event_type == "reviewer_assigned":
        return "review_activity"
    if event_type in {"source_writeback", "source_writeback_restored"}:
        return "writeback_activity"
    return "other"


def _event_summary(
    event_type: str, *, entity_type: str, entity_id: str, payload: dict[str, Any]
) -> str:
    summary = str(payload.get("summary") or "").strip()
    if summary:
        return summary
    if event_type == "service_change":
        return f"Service change recorded for {entity_id}."
    if event_type == "object_marked_suspect_due_to_change":
        return f"Guidance for {entity_id} was marked suspect."
    if event_type == "revision_submitted_for_review":
        return f"Revision for {entity_id} was submitted for review."
    if event_type == "revision_approved":
        return f"Revision for {entity_id} was approved and became canonical guidance."
    if event_type == "revision_rejected":
        return f"Revision for {entity_id} was rejected."
    if event_type == "validation_run_recorded":
        return f"Validation run recorded for {entity_type}:{entity_id}."
    if event_type == "source_writeback":
        return f"Canonical source writeback completed for {entity_id}."
    if event_type == "source_writeback_restored":
        return f"Canonical source was restored for {entity_id}."
    reason = str(payload.get("reason") or "").strip()
    if reason:
        return reason
    return f"{event_type.replace('_', ' ')} for {entity_type}:{entity_id}."


def _event_next_action(group: str, *, entity_type: str, entity_id: str) -> str:
    if group == "service_changes":
        return f"Review the service path for {entity_id} and revalidate linked guidance."
    if group == "evidence_degradation":
        return f"Revalidate evidence for {entity_type}:{entity_id} before relying on it."
    if group == "validation_failures":
        return f"Inspect the validation failure for {entity_type}:{entity_id} before approving changes."
    if group == "validation_activity":
        return f"Review the recorded validation outcome for {entity_type}:{entity_id}."
    if group == "manual_suspect_marks":
        return f"Treat {entity_type}:{entity_id} as unsafe until the reason is reviewed or revised."
    if group == "review_activity":
        return f"Open the review context for {entity_type}:{entity_id} and move it to the next lifecycle step."
    if group == "writeback_activity":
        return f"Inspect canonical source state for {entity_type}:{entity_id} and confirm the live guidance is the intended version."
    return f"Inspect the latest activity for {entity_type}:{entity_id}."


def event_history(
    *,
    limit: int = 100,
    entity_type: str | None = None,
    entity_id: str | None = None,
    event_type: str | None = None,
    database_path: str | Path = DB_PATH,
) -> list[dict[str, Any]]:
    connection = require_runtime_connection(database_path)
    try:
        clauses: list[str] = []
        parameters: list[str | int] = []
        if entity_type:
            clauses.append("entity_type = ?")
            parameters.append(entity_type)
        if entity_id:
            clauses.append("entity_id = ?")
            parameters.append(entity_id)
        if event_type:
            clauses.append("event_type = ?")
            parameters.append(event_type)
        where_sql = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        parameters.append(limit)
        rows = connection.execute(
            f"""
            SELECT event_id, event_type, source, entity_type, entity_id, occurred_at, actor, payload_json
            FROM events
            {where_sql}
            ORDER BY occurred_at DESC, event_id DESC
            LIMIT ?
            """,
            tuple(parameters),
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
                "payload": payload,
                "group": group,
                "what_happened": _event_summary(
                    str(row["event_type"]),
                    entity_type=str(row["entity_type"]),
                    entity_id=str(row["entity_id"]),
                    payload=payload,
                ),
                "next_action": _event_next_action(
                    group,
                    entity_type=str(row["entity_type"]),
                    entity_id=str(row["entity_id"]),
                ),
            }
            for row in rows
            for payload in [_json_dict(row["payload_json"])]
            for group in [_event_group(str(row["event_type"]), payload)]
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
            "payload": payload,
            "group": group,
            "what_happened": _event_summary(
                str(row["event_type"]),
                entity_type=str(row["entity_type"]),
                entity_id=str(row["entity_id"]),
                payload=payload,
            ),
            "next_action": _event_next_action(
                group,
                entity_type=str(row["entity_type"]),
                entity_id=str(row["entity_id"]),
            ),
        }
        for row in rows
        for payload in [_json_dict(row["payload_json"])]
        for group in [_event_group(str(row["event_type"]), payload)]
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
        recent_events = _recent_events(
            connection, entity_type="knowledge_object", entity_ids=[object_id]
        )
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
