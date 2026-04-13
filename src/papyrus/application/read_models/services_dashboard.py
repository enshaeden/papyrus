from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.domain.policies import citation_health_label
from papyrus.infrastructure.paths import DB_PATH

from .content_health import collect_content_health_sections
from .queue_search import knowledge_queue
from .support import ServiceNotFoundError, _json_dict, _json_list, require_runtime_connection


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
                "object_lifecycle_state": str(row["object_lifecycle_state"]),
                "trust_state": str(row["trust_state"]),
                "revision_review_state": str(row["revision_review_state"]),
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
                    o.object_lifecycle_state,
                    o.trust_state,
                    COALESCE(d.revision_review_state, CASE WHEN o.current_revision_id IS NULL THEN 'draft' ELSE 'unknown' END) AS revision_review_state,
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
                "SELECT object_id, title, canonical_path, object_lifecycle_state FROM knowledge_objects WHERE object_id = ?",
                (service_row["canonical_object_id"],),
            ).fetchone()
            if canonical_object_row is not None:
                canonical_object = {
                    "object_id": str(canonical_object_row["object_id"]),
                    "title": str(canonical_object_row["title"]),
                    "path": str(canonical_object_row["canonical_path"]),
                    "object_lifecycle_state": str(canonical_object_row["object_lifecycle_state"]),
                }

        return {
            "service": {
                "service_id": str(service_row["service_id"]),
                "service_name": str(service_row["service_name"]),
                "canonical_object_id": str(service_row["canonical_object_id"])
                if service_row["canonical_object_id"] is not None
                else None,
                "owner": str(service_row["owner"]) if service_row["owner"] is not None else None,
                "team": str(service_row["team"]) if service_row["team"] is not None else None,
                "status": str(service_row["status"]),
                "service_criticality": str(service_row["service_criticality"]),
                "support_entrypoints": [
                    str(item) for item in _json_list(service_row["support_entrypoints_json"])
                ],
                "dependencies": [
                    str(item) for item in _json_list(service_row["dependencies_json"])
                ],
                "common_failure_modes": [
                    str(item) for item in _json_list(service_row["common_failure_modes_json"])
                ],
                "source": str(service_row["source"]),
            },
            "canonical_object": canonical_object,
            "linked_objects": linked_objects,
            "service_posture": {
                "linked_object_count": len(linked_objects),
                "review_required_count": sum(
                    1 for item in linked_objects if item["revision_review_state"] != "approved"
                ),
                "degraded_count": sum(
                    1 for item in linked_objects if item["trust_state"] != "trusted"
                ),
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
                "canonical_object_id": str(row["canonical_object_id"])
                if row["canonical_object_id"] is not None
                else None,
                "linked_object_count": int(row["linked_object_count"] or 0),
            }
            for row in rows
        ]
    finally:
        connection.close()


def oversight_dashboard(
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    cleanup_sections = [
        "placeholder-heavy",
        "legacy-blueprint-fallback",
        "unclear-ownership",
        "weak-evidence",
        "migration-gaps",
    ]
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
        review_counts = {
            str(row["revision_review_state"]): int(row["item_count"])
            for row in connection.execute(
                "SELECT revision_review_state, COUNT(*) AS item_count FROM search_documents GROUP BY revision_review_state"
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
                "severity": "informational"
                if latest_validation["status"] == "passed"
                else "serious",
            }
        cleanup_outputs = collect_content_health_sections(
            cleanup_sections, database_path=database_path
        )
        return {
            "object_count": object_count,
            "trust_counts": trust_counts,
            "review_counts": review_counts,
            "citation_health_counts": citation_health_counts,
            "evidence_counts": evidence_counts,
            "queue": knowledge_queue(limit=25, database_path=database_path, ranking="triage"),
            "validation_runs": validation_runs,
            "validation_posture": validation_posture,
            "cleanup_counts": {
                section: len(cleanup_outputs.get(section, [])) for section in cleanup_sections
            },
        }
    finally:
        connection.close()


def trust_dashboard(
    *,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    """Compatibility alias for older callers."""
    return oversight_dashboard(database_path=database_path)
