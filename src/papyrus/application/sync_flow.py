from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import uuid

from papyrus.application.authoring_flow import compute_completion_state, derive_section_content
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.validation_flow import validate_knowledge_documents
from papyrus.application.runtime_projection import persist_revision_artifacts, refresh_current_object_projection, service_id
from papyrus.domain.lifecycle import DraftProgressState, RevisionReviewState, SourceSyncState
from papyrus.domain.policies import bootstrap_revision_state, runtime_trust_state
from papyrus.domain.value_objects import RevisionReviewStatus
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.markdown.serializer import date_to_iso, json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    get_knowledge_object,
    get_knowledge_revision,
    insert_knowledge_revision,
    load_knowledge_documents,
    load_object_schemas,
    load_policy,
    load_schema,
    load_taxonomies,
    next_revision_number,
    replace_fts_document,
    upsert_knowledge_object,
    upsert_search_document,
)
from papyrus.infrastructure.repositories.service_repo import upsert_service
from papyrus.infrastructure.repositories.validation_repo import insert_validation_run
from papyrus.infrastructure.search.indexer import fts5_available, summarize_for_search
from papyrus.jobs.citation_scan import scan_citations
from papyrus.jobs.stale_scan import cadence_to_days


def _content_hash(normalized_metadata_json: str, body: str) -> str:
    return hashlib.sha256(f"{normalized_metadata_json}\n{body}".encode("utf-8")).hexdigest()


AUTHORITY = PolicyAuthority.from_repository_policy()

def _event_id(prefix: str, object_id: str | None, revision_id: str | None, now_iso: str) -> str:
    del object_id, revision_id, now_iso
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _sync_revision_state(
    *,
    existing_object,
    existing_revision,
    status: str,
) -> str:
    if existing_revision is not None:
        return str(existing_revision["revision_review_state"] or existing_revision["revision_state"])
    if existing_object is None:
        return bootstrap_revision_state(status)
    return RevisionReviewStatus.DRAFT.value


def _sync_trust_state(
    *,
    parsed_trust_state: str,
    revision_state: str,
    existing_object,
    revision_id: str,
) -> str:
    existing_trust_state = None
    preserve_existing_warning = False
    if existing_object is not None and existing_object["current_revision_id"] == revision_id:
        existing_trust_state = str(existing_object["trust_state"])
        preserve_existing_warning = True
    return runtime_trust_state(
        base_trust_state=parsed_trust_state,
        revision_state=revision_state,
        existing_trust_state=existing_trust_state,
        preserve_existing_warning=preserve_existing_warning,
    )

def _seed_services(connection, taxonomies: dict[str, dict[str, object]]) -> dict[str, str]:
    seeded_services: dict[str, str] = {}
    for service_name in taxonomies.get("services", {}).get("allowed_values", []):
        current_service_id = service_id(service_name)
        seeded_services[service_name] = current_service_id
        upsert_service(
            connection,
            service_id=current_service_id,
            service_name=service_name,
            canonical_object_id=None,
            owner=None,
            team=None,
            status="active",
            service_criticality="not_classified",
            support_entrypoints_json=json_dump([]),
            dependencies_json=json_dump([]),
            common_failure_modes_json=json_dump([]),
            source="taxonomy",
        )
    return seeded_services


def build_search_projection(database_path: Path) -> tuple[int, str]:
    policy = load_policy()
    documents = load_knowledge_documents(policy)
    object_schemas = load_object_schemas()
    legacy_schema = load_schema()
    taxonomies = load_taxonomies()
    issues = validate_knowledge_documents(documents, object_schemas, legacy_schema, taxonomies, policy)
    if issues:
        raise ValueError("index build aborted because validation failed")

    connection = open_runtime_database(database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    now_iso = now.isoformat()
    try:
        has_fts5 = fts5_available(connection)
        apply_runtime_schema(connection, has_fts5=has_fts5)
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (RUNTIME_SCHEMA_VERSION, now_iso),
        )

        seeded_services = _seed_services(connection, taxonomies)

        validation_run_id = _event_id("validation-sync-build", None, None, now_iso)
        insert_validation_run(
            connection,
            run_id=validation_run_id,
            run_type="sync_preflight_validation",
            started_at=now_iso,
            completed_at=now_iso,
            status="passed",
            finding_count=0,
            details_json=json_dump({"document_count": len(documents)}),
        )

        for document in documents:
            review_cadence_days = cadence_to_days(str(document.metadata["review_cadence"]), taxonomies)
            parsed = normalize_object_metadata(
                document,
                review_cadence_days=review_cadence_days,
                as_of=dt.date.today(),
            )
            normalized_metadata_json = json_dump(parsed.metadata)
            section_content = derive_section_content(
                blueprint_id=parsed.object_type,
                metadata=parsed.metadata,
                body_markdown=document.body,
            )
            section_completion = compute_completion_state(
                blueprint=get_blueprint(parsed.object_type),
                section_content=section_content,
                taxonomies=taxonomies,
            )
            revision_hash = _content_hash(normalized_metadata_json, document.body)
            revision_id = f"{document.knowledge_object_id}-rev-{revision_hash[:12]}"
            existing_object = get_knowledge_object(connection, document.knowledge_object_id)
            existing_revision = get_knowledge_revision(connection, revision_id)
            revision_state = _sync_revision_state(
                existing_object=existing_object,
                existing_revision=existing_revision,
                status=str(parsed.metadata["status"]),
            )
            trust_state = _sync_trust_state(
                parsed_trust_state=parsed.trust_state,
                revision_state=revision_state,
                existing_object=existing_object,
                revision_id=revision_id,
            )

            change_log = parsed.metadata.get("change_log") or []
            latest_change = change_log[-1]["summary"] if change_log else None
            revision_number = (
                int(existing_revision["revision_number"])
                if existing_revision is not None
                else next_revision_number(connection, document.knowledge_object_id)
            )

            upsert_knowledge_object(
                connection,
                object_id=document.knowledge_object_id,
                object_type=parsed.object_type,
                legacy_type=parsed.legacy_type,
                title=str(parsed.metadata["title"]),
                summary=str(parsed.metadata["summary"]),
                status=str(parsed.metadata["status"]),
                object_lifecycle_state=str(parsed.metadata["status"]),
                owner=str(parsed.metadata["owner"]),
                team=str(parsed.metadata["team"]),
                canonical_path=document.relative_path,
                source_type=str(parsed.metadata["source_type"]),
                source_system=str(parsed.metadata["source_system"]),
                source_title=str(parsed.metadata["source_title"]),
                created_date=date_to_iso(parsed.metadata["created"]),
                updated_date=date_to_iso(parsed.metadata["updated"]),
                last_reviewed=date_to_iso(parsed.metadata["last_reviewed"]),
                review_cadence=str(parsed.metadata["review_cadence"]),
                trust_state=trust_state,
                source_sync_state=SourceSyncState.APPLIED.value,
                source_sync_revision_id=revision_id,
                source_sync_content_hash=revision_hash,
                current_revision_id=revision_id,
                tags_json=json_dump(parsed.metadata.get("tags", [])),
                systems_json=json_dump(parsed.metadata.get("systems", [])),
            )

            if existing_revision is None:
                draft_progress_state = (
                    section_completion["draft_state"]
                    if revision_state == RevisionReviewStatus.DRAFT.value
                    else DraftProgressState.READY_FOR_REVIEW.value
                )
                insert_knowledge_revision(
                    connection,
                    revision_id=revision_id,
                    object_id=document.knowledge_object_id,
                    revision_number=revision_number,
                    revision_state=revision_state,
                    revision_review_state=revision_state,
                    blueprint_id=parsed.object_type,
                    draft_state=draft_progress_state,
                    draft_progress_state=draft_progress_state,
                    source_path=document.relative_path,
                    content_hash=revision_hash,
                    body_markdown=document.body,
                    normalized_payload_json=normalized_metadata_json,
                    section_content_json=json.dumps(section_content, sort_keys=True, ensure_ascii=True),
                    section_completion_json=json.dumps(
                        section_completion["section_completion_map"],
                        sort_keys=True,
                        ensure_ascii=True,
                    ),
                    legacy_metadata_json=json_dump(document.metadata),
                    imported_at=now_iso,
                    change_summary=latest_change,
                )

            object_services = persist_revision_artifacts(
                connection,
                parsed=parsed,
                revision_id=revision_id,
                relationship_provenance="source_sync",
                seeded_services=seeded_services,
            )

            upsert_search_document(
                connection,
                object_id=document.knowledge_object_id,
                revision_id=revision_id,
                title=str(parsed.metadata["title"]),
                summary=str(parsed.metadata["summary"]),
                object_type=parsed.object_type,
                legacy_type=parsed.legacy_type,
                status=str(parsed.metadata["status"]),
                object_lifecycle_state=str(parsed.metadata["status"]),
                owner=str(parsed.metadata["owner"]),
                team=str(parsed.metadata["team"]),
                trust_state=trust_state,
                approval_state=revision_state,
                revision_review_state=revision_state,
                draft_progress_state=(
                    section_completion["draft_state"]
                    if revision_state == RevisionReviewStatus.DRAFT.value
                    else DraftProgressState.READY_FOR_REVIEW.value
                ),
                source_sync_state=SourceSyncState.APPLIED.value,
                freshness_rank=parsed.freshness_rank,
                citation_health_rank=parsed.citation_health_rank,
                ownership_rank=parsed.ownership_rank,
                path=document.relative_path,
                search_text=summarize_for_search(document),
            )
            replace_fts_document(
                connection,
                object_id=document.knowledge_object_id,
                title=str(parsed.metadata["title"]),
                summary=str(parsed.metadata["summary"]),
                body=document.body,
                tags=list(parsed.metadata.get("tags", [])),
                systems=list(parsed.metadata.get("systems", [])),
                services=object_services,
            )

            if existing_object is None:
                insert_audit_event(
                    connection,
                    event_id=_event_id("source-object-ingested", document.knowledge_object_id, revision_id, now_iso),
                    event_type="source_object_ingested",
                    occurred_at=now_iso,
                    actor="sync_flow",
                    object_id=document.knowledge_object_id,
                    revision_id=revision_id,
                    details_json=json_dump(
                        {
                            "object_type": parsed.object_type,
                            "source_path": document.relative_path,
                            "revision_number": revision_number,
                        }
                    ),
                )
            elif existing_object["current_revision_id"] != revision_id:
                insert_audit_event(
                    connection,
                    event_id=_event_id("source-revision-detected", document.knowledge_object_id, revision_id, now_iso),
                    event_type="source_revision_detected",
                    occurred_at=now_iso,
                    actor="sync_flow",
                    object_id=document.knowledge_object_id,
                    revision_id=revision_id,
                    details_json=json_dump(
                        {
                            "source_path": document.relative_path,
                            "previous_revision_id": existing_object["current_revision_id"],
                            "revision_number": revision_number,
                        }
                    ),
                )

        citation_scan = scan_citations(connection, taxonomies=taxonomies, as_of=dt.date.today(), persist=True)
        citation_run_id = _event_id("validation-citation-scan", None, None, now_iso)
        insert_validation_run(
            connection,
            run_id=citation_run_id,
            run_type="citation_scan",
            started_at=now_iso,
            completed_at=now_iso,
            status="passed" if not citation_scan.findings else "warning",
            finding_count=len(citation_scan.findings),
            details_json=json_dump(
                {
                    "scanned_count": citation_scan.scanned_count,
                    "finding_count": len(citation_scan.findings),
                }
            ),
        )
        insert_audit_event(
            connection,
            event_id=_event_id("citation-validation-recorded", None, None, now_iso),
            event_type="citation_validation_recorded",
            occurred_at=now_iso,
            actor="sync_flow",
            object_id=None,
            revision_id=None,
            details_json=json_dump({"run_id": citation_run_id, "finding_count": len(citation_scan.findings)}),
        )

        for document in documents:
            refresh_current_object_projection(
                connection,
                object_id=document.knowledge_object_id,
                taxonomies=taxonomies,
                as_of=dt.date.today(),
            )

        insert_audit_event(
            connection,
            event_id=_event_id("validation-recorded", None, None, now_iso),
            event_type="validation_recorded",
            occurred_at=now_iso,
            actor="sync_flow",
            object_id=None,
            revision_id=None,
            details_json=json_dump({"run_id": validation_run_id}),
        )
        connection.commit()
    finally:
        connection.close()

    return len(documents), "fts5" if has_fts5 else "like-fallback"
