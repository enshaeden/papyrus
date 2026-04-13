from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.runtime_projection import RuntimeStateSnapshot
from papyrus.application.ui_projection import (
    build_object_actions,
    build_review_actions,
    build_ui_projection,
    ui_projection_payload,
)
from papyrus.domain.policies import citation_health_label
from papyrus.infrastructure.paths import DB_PATH

from .content_health import collect_content_health_sections
from .object_detail import knowledge_object_detail, revision_history
from .queue_search import _augment_queue_items
from .support import (
    KnowledgeObjectNotFoundError,
    _draft_progress_value,
    _json_dict,
    _object_lifecycle_value,
    _policy_authority,
    _revision_review_value,
    _source_sync_value,
    require_runtime_connection,
)


def manage_queue(
    *,
    limit: int = 200,
    database_path: str | Path = DB_PATH,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    cleanup_sections = [
        "placeholder-heavy",
        "legacy-blueprint-fallback",
        "unclear-ownership",
        "weak-evidence",
        "migration-gaps",
    ]
    current_authority = _policy_authority(authority)
    connection = require_runtime_connection(database_path)
    try:
        rows = connection.execute(
            """
            SELECT
                o.object_id,
                o.object_type,
                o.title,
                o.summary,
                o.object_lifecycle_state,
                o.owner,
                o.team,
                o.last_reviewed,
                o.review_cadence,
                o.canonical_path,
                o.trust_state,
                o.source_sync_state,
                o.current_revision_id,
                COALESCE(r.revision_id, '') AS revision_id,
                COALESCE(r.revision_number, 0) AS revision_number,
                COALESCE(r.revision_review_state, 'none') AS revision_review_state,
                COALESCE(r.draft_progress_state, 'ready_for_review') AS draft_progress_state,
                COALESCE(r.imported_at, '') AS imported_at,
                COALESCE(r.change_summary, '') AS change_summary,
                COALESCE(d.freshness_rank, 0) AS freshness_rank,
                COALESCE(d.citation_health_rank, 0) AS citation_health_rank,
                COALESCE(d.ownership_rank, CASE WHEN TRIM(o.owner) = '' THEN 1 ELSE 0 END) AS ownership_rank,
                COALESCE(d.path, o.canonical_path) AS path
            FROM knowledge_objects AS o
            LEFT JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
            LEFT JOIN search_documents AS d ON d.object_id = o.object_id
            ORDER BY
                CASE COALESCE(r.revision_review_state, 'none')
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
            item: dict[str, Any] = {
                "object_id": str(row["object_id"]),
                "object_type": str(row["object_type"]),
                "title": str(row["title"]),
                "summary": str(row["summary"]),
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
                "current_revision_id": str(row["current_revision_id"])
                if row["current_revision_id"] is not None
                else None,
                "revision_id": str(row["revision_id"]) or None,
                "revision_number": int(row["revision_number"] or 0),
                "change_summary": str(row["change_summary"]) if row["change_summary"] else None,
                "imported_at": str(row["imported_at"]) if row["imported_at"] else None,
                "assignment": assignment_map.get(str(row["revision_id"])),
                "reasons": [],
            }
            if item["current_revision_id"] is None:
                item["reasons"].append("no_revision")
            if item["revision_review_state"] in {"draft", "rejected"}:
                item["reasons"].append(f"revision:{item['revision_review_state']}")
            if item["revision_review_state"] == "in_review":
                item["reasons"].append("awaiting_review")
            if item["freshness_rank"] > 0:
                item["reasons"].append("review_due")
            if item["citation_health_rank"] > 0:
                item["reasons"].append(
                    f"citation:{citation_health_label(item['citation_health_rank'])}"
                )
            if item["ownership_rank"] > 0 or not item["owner"].strip():
                item["reasons"].append("ownership_unclear")
            if item["trust_state"] != "trusted":
                item["reasons"].append(f"trust:{item['trust_state']}")
            items.append(item)
        _augment_queue_items(connection, items)
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
                        assignment=item["assignment"],
                    ),
                )
            )

        def unique_by_object_id(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
            seen: set[str] = set()
            ordered: list[dict[str, Any]] = []
            for entry in entries:
                object_id = str(entry["object_id"])
                if object_id in seen:
                    continue
                seen.add(object_id)
                ordered.append(entry)
            return ordered

        review_required = [item for item in items if item["revision_review_state"] == "in_review"]
        ready_for_review = [item for item in review_required if item["assignment"] is None]
        needs_decision = [item for item in review_required if item["assignment"] is not None]
        stale_items = [item for item in items if item["freshness_rank"] > 0]
        weak_evidence_items = [item for item in items if item["citation_health_rank"] > 0]
        ownership_items = [
            item for item in items if item["ownership_rank"] > 0 or not item["owner"].strip()
        ]
        draft_items = [
            item
            for item in items
            if item["current_revision_id"] is None
            or item["revision_review_state"] in {"draft", "rejected"}
        ]
        suspect_items = [
            item
            for item in items
            if item["trust_state"] != "trusted" or item["revision_review_state"] != "approved"
        ]
        needs_revalidation = unique_by_object_id(
            stale_items
            + weak_evidence_items
            + [item for item in items if item["trust_state"] in {"suspect", "stale"}]
        )
        recently_changed = sorted(
            [item for item in items if item["imported_at"]],
            key=lambda item: str(item["imported_at"]),
            reverse=True,
        )
        superseded_items = [
            item
            for item in items
            if item["object_lifecycle_state"] == "deprecated"
            or item["revision_review_state"] == "superseded"
        ]
        needs_attention = unique_by_object_id(
            review_required + needs_revalidation + ownership_items
        )
        cleanup_outputs = collect_content_health_sections(
            cleanup_sections, database_path=database_path
        )

        return {
            "items": items,
            "review_required": review_required,
            "ready_for_review": ready_for_review,
            "needs_decision": needs_decision,
            "stale_items": stale_items,
            "suspect_items": suspect_items,
            "weak_evidence_items": weak_evidence_items,
            "ownership_items": ownership_items,
            "draft_items": draft_items,
            "needs_revalidation": needs_revalidation,
            "recently_changed": recently_changed,
            "superseded_items": superseded_items,
            "needs_attention": needs_attention,
            "cleanup_counts": {
                section: len(cleanup_outputs.get(section, [])) for section in cleanup_sections
            },
        }
    finally:
        connection.close()


def review_detail(
    object_id: str,
    revision_id: str,
    *,
    database_path: str | Path = DB_PATH,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    connection = require_runtime_connection(database_path)
    try:
        detail = knowledge_object_detail(
            object_id, database_path=database_path, authority=current_authority
        )
        history = revision_history(object_id, database_path=database_path)
        revision = next(
            (item for item in history["revisions"] if item["revision_id"] == revision_id), None
        )
        if revision is None:
            raise KnowledgeObjectNotFoundError(f"revision not found for {object_id}: {revision_id}")
        revision_row = connection.execute(
            """
            SELECT revision_id, object_id, revision_number, revision_review_state, blueprint_id, draft_progress_state, imported_at, change_summary, body_markdown, normalized_payload_json, section_content_json, section_completion_json
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
        state_snapshot = RuntimeStateSnapshot(
            object_lifecycle_state=str(detail["object"]["object_lifecycle_state"]),
            revision_review_state=_revision_review_value(revision_row),
            draft_progress_state=_draft_progress_value(revision_row),
            source_sync_state=str(detail["object"]["source_sync_state"]),
            trust_state=str(detail["object"]["trust_state"]),
        )
        ui_projection = ui_projection_payload(
            build_ui_projection(
                state=state_snapshot,
                posture=detail["posture"],
                reasons=[],
                actions=build_review_actions(
                    authority=current_authority,
                    state=state_snapshot,
                    assignments=revision["review_assignments"],
                ),
            )
        )
        return {
            "object": detail["object"],
            "current_revision": detail["current_revision"],
            "posture": detail["posture"],
            "revision": {
                **revision,
                "body_markdown": str(revision_row["body_markdown"]),
                "metadata": _json_dict(revision_row["normalized_payload_json"]),
                "blueprint_id": str(
                    revision_row["blueprint_id"] or detail["object"]["object_type"]
                ),
                "revision_review_state": _revision_review_value(revision_row),
                "draft_progress_state": _draft_progress_value(revision_row),
                "section_content": _json_dict(revision_row["section_content_json"]),
                "section_completion_map": _json_dict(revision_row["section_completion_json"]),
            },
            "assignments": revision["review_assignments"],
            "citations": citations,
            "audit_events": revision_audit,
            "ui_projection": ui_projection,
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
