from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.application.authoring_flow import derive_section_content
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.posture import build_posture_summary
from papyrus.application.runtime_projection import RuntimeStateSnapshot
from papyrus.application.ui_projection import (
    build_object_actions,
    build_reference_candidate_projection,
    build_ui_projection,
    reference_candidate_payload,
    ui_projection_payload,
)
from papyrus.infrastructure.paths import DB_PATH

from .article_projection import build_article_projection
from .support import (
    KnowledgeObjectNotFoundError,
    _draft_progress_value,
    _json_dict,
    _json_list,
    _object_lifecycle_value,
    _policy_authority,
    _revision_review_value,
    _source_sync_value,
    require_runtime_connection,
)

def knowledge_object_detail(
    object_id: str,
    *,
    database_path: str | Path = DB_PATH,
    authority: PolicyAuthority | None = None,
    actor_id: str = "local.operator",
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    connection = require_runtime_connection(database_path)
    try:
        object_row = connection.execute(
            """
            SELECT
                o.*,
                d.object_lifecycle_state,
                d.revision_review_state,
                d.draft_progress_state,
                d.source_sync_state,
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
                SELECT revision_id, revision_number, revision_review_state, blueprint_id, draft_progress_state, imported_at, change_summary, body_markdown, normalized_payload_json, section_content_json, section_completion_json
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
                "object_lifecycle_state": str(row["object_lifecycle_state"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT r.relationship_type, o.object_id, o.title, o.canonical_path, o.object_lifecycle_state
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
                "object_lifecycle_state": str(row["object_lifecycle_state"]),
            }
            for row in connection.execute(
                """
                SELECT DISTINCT r.relationship_type, o.object_id, o.title, o.canonical_path, o.object_lifecycle_state
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
        revision_review_state = (
            str(object_row["revision_review_state"])
            if object_row["revision_review_state"] is not None
            else _revision_review_value(current_revision)
            if current_revision is not None
            else None
        )
        posture = build_posture_summary(
            trust_state=str(object_row["trust_state"]),
            revision_review_state=revision_review_state,
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
        state_snapshot = RuntimeStateSnapshot(
            object_lifecycle_state=_object_lifecycle_value(object_row),
            revision_review_state=revision_review_state,
            draft_progress_state=(
                str(object_row["draft_progress_state"])
                if object_row["draft_progress_state"] is not None
                else _draft_progress_value(current_revision)
                if current_revision is not None
                else None
            ),
            source_sync_state=_source_sync_value(object_row),
            trust_state=str(object_row["trust_state"]),
        )
        ui_projection = ui_projection_payload(
            build_ui_projection(
                state=state_snapshot,
                posture=posture,
                reasons=[],
                actions=build_object_actions(
                    authority=current_authority,
                    state=state_snapshot,
                    current_revision_id=(
                        str(object_row["current_revision_id"]) if object_row["current_revision_id"] is not None else None
                    ),
                    evidence_status=evidence_status,
                ),
            )
        )

        return {
            "article_projection": build_article_projection(
                item={
                    "object_id": str(object_row["object_id"]),
                    "object_type": str(object_row["object_type"]),
                    "title": str(object_row["title"]),
                    "summary": str(object_row["summary"]),
                    "object_lifecycle_state": _object_lifecycle_value(object_row),
                    "owner": str(object_row["owner"]),
                    "team": str(object_row["team"]),
                    "canonical_path": str(object_row["canonical_path"]),
                    "last_reviewed": str(object_row["last_reviewed"]),
                    "review_cadence": str(object_row["review_cadence"]),
                    "trust_state": str(object_row["trust_state"]),
                    "revision_review_state": revision_review_state,
                    "systems": [str(item) for item in _json_list(object_row["systems_json"])],
                    "tags": [str(item) for item in _json_list(object_row["tags_json"])],
                },
                revision=(
                    {
                        "revision_id": str(current_revision["revision_id"]),
                        "revision_number": int(current_revision["revision_number"]),
                        "revision_review_state": _revision_review_value(current_revision),
                        "blueprint_id": str(current_revision["blueprint_id"] or object_row["object_type"]),
                        "imported_at": str(current_revision["imported_at"]),
                        "change_summary": str(current_revision["change_summary"]) if current_revision["change_summary"] is not None else None,
                        "body_markdown": str(current_revision["body_markdown"]),
                    }
                    if current_revision is not None
                    else None
                ),
                metadata=metadata,
                section_content=(
                    _json_dict(current_revision["section_content_json"])
                    if current_revision is not None and str(current_revision["section_content_json"] or "").strip() not in {"", "{}"}
                    else (
                        derive_section_content(
                            blueprint_id=str(current_revision["blueprint_id"] or object_row["object_type"]),
                            metadata=metadata,
                            body_markdown=str(current_revision["body_markdown"]),
                        )
                        if current_revision is not None
                        else {}
                    )
                ),
                related_services=related_services,
                citations=citations,
                evidence_status=evidence_status,
                audit_events=audit_events,
                ui_projection=ui_projection,
                actor_id=actor_id,
            ),
            "object": {
                "object_id": str(object_row["object_id"]),
                "object_type": str(object_row["object_type"]),
                "legacy_type": str(object_row["legacy_type"]) if object_row["legacy_type"] is not None else None,
                "title": str(object_row["title"]),
                "summary": str(object_row["summary"]),
                "object_lifecycle_state": _object_lifecycle_value(object_row),
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
                "revision_review_state": revision_review_state,
                "draft_progress_state": (
                    str(object_row["draft_progress_state"]) if object_row["draft_progress_state"] is not None else None
                ),
                "source_sync_state": _source_sync_value(object_row),
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
                    "revision_review_state": _revision_review_value(current_revision),
                    "blueprint_id": str(current_revision["blueprint_id"] or object_row["object_type"]),
                    "draft_progress_state": _draft_progress_value(current_revision),
                    "imported_at": str(current_revision["imported_at"]),
                    "change_summary": str(current_revision["change_summary"]) if current_revision["change_summary"] is not None else None,
                    "body_markdown": str(current_revision["body_markdown"]),
                    "section_content": (
                        _json_dict(current_revision["section_content_json"])
                        if str(current_revision["section_content_json"] or "").strip() not in {"", "{}"}
                        else derive_section_content(
                            blueprint_id=str(current_revision["blueprint_id"] or object_row["object_type"]),
                            metadata=metadata,
                            body_markdown=str(current_revision["body_markdown"]),
                        )
                    ),
                    "section_completion_map": _json_dict(current_revision["section_completion_json"]),
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
            "ui_projection": ui_projection,
            "reference_projection": reference_candidate_payload(
                build_reference_candidate_projection(
                    current_revision=(
                        {
                            "revision_id": str(current_revision["revision_id"]),
                            "revision_review_state": _revision_review_value(current_revision),
                            "body_markdown": str(current_revision["body_markdown"]),
                        }
                        if current_revision is not None
                        else None
                    ),
                    citations=citations,
                )
            ),
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
            SELECT revision_id, revision_number, revision_review_state, blueprint_id, draft_progress_state, imported_at, change_summary, source_path
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
                    "revision_review_state": _revision_review_value(row),
                    "blueprint_id": str(row["blueprint_id"] or ""),
                    "draft_progress_state": _draft_progress_value(row),
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
