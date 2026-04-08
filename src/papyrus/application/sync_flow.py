from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
import uuid

from papyrus.application.validation_flow import validate_knowledge_documents
from papyrus.domain.policies import bootstrap_revision_state, runtime_trust_state
from papyrus.domain.value_objects import RevisionReviewStatus
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.markdown.serializer import date_to_iso, json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.citation_repo import delete_citations_for_revision, insert_citation
from papyrus.infrastructure.repositories.knowledge_repo import (
    delete_source_sync_relationships,
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
    upsert_relationship,
    upsert_search_document,
)
from papyrus.infrastructure.repositories.service_repo import upsert_service
from papyrus.infrastructure.repositories.validation_repo import insert_validation_run
from papyrus.infrastructure.search.indexer import fts5_available, summarize_for_search
from papyrus.jobs.stale_scan import cadence_to_days


def _content_hash(normalized_metadata_json: str, body: str) -> str:
    return hashlib.sha256(f"{normalized_metadata_json}\n{body}".encode("utf-8")).hexdigest()


def _relationship_id(source_type: str, source_id: str, target_type: str, target_id: str, rel_type: str) -> str:
    return hashlib.sha256(f"{source_type}|{source_id}|{target_type}|{target_id}|{rel_type}".encode("utf-8")).hexdigest()[:24]


def _service_id(service_name: str) -> str:
    return hashlib.sha256(service_name.encode("utf-8")).hexdigest()[:24]


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
        return str(existing_revision["revision_state"])
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


def _sync_relationship(
    connection,
    *,
    source_entity_type: str,
    source_entity_id: str,
    target_entity_type: str,
    target_entity_id: str,
    relationship_type: str,
    provenance: str,
) -> None:
    upsert_relationship(
        connection,
        relationship_id=_relationship_id(
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            relationship_type,
        ),
        source_entity_type=source_entity_type,
        source_entity_id=source_entity_id,
        target_entity_type=target_entity_type,
        target_entity_id=target_entity_id,
        relationship_type=relationship_type,
        provenance=provenance,
    )


def _seed_services(connection, taxonomies: dict[str, dict[str, object]]) -> dict[str, str]:
    seeded_services: dict[str, str] = {}
    for service_name in taxonomies.get("services", {}).get("allowed_values", []):
        service_id = _service_id(service_name)
        seeded_services[service_name] = service_id
        upsert_service(
            connection,
            service_id=service_id,
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
                current_revision_id=revision_id,
                tags_json=json_dump(parsed.metadata.get("tags", [])),
                systems_json=json_dump(parsed.metadata.get("systems", [])),
            )

            if existing_revision is None:
                insert_knowledge_revision(
                    connection,
                    revision_id=revision_id,
                    object_id=document.knowledge_object_id,
                    revision_number=revision_number,
                    revision_state=revision_state,
                    source_path=document.relative_path,
                    content_hash=revision_hash,
                    body_markdown=document.body,
                    normalized_payload_json=normalized_metadata_json,
                    legacy_metadata_json=json_dump(document.metadata),
                    imported_at=now_iso,
                    change_summary=latest_change,
                )

            object_services = parsed.related_services
            if parsed.object_type == "service_record":
                service_name = str(parsed.metadata["service_name"])
                object_services = list(dict.fromkeys([service_name, *object_services]))
                upsert_service(
                    connection,
                    service_id=_service_id(service_name),
                    service_name=service_name,
                    canonical_object_id=document.knowledge_object_id,
                    owner=str(parsed.metadata["owner"]),
                    team=str(parsed.metadata["team"]),
                    status=str(parsed.metadata["status"]),
                    service_criticality=str(parsed.metadata["service_criticality"]),
                    support_entrypoints_json=json_dump(parsed.metadata.get("support_entrypoints", [])),
                    dependencies_json=json_dump(parsed.metadata.get("dependencies", [])),
                    common_failure_modes_json=json_dump(parsed.metadata.get("common_failure_modes", [])),
                    source="service_record",
                )

            delete_source_sync_relationships(connection, document.knowledge_object_id)
            for service_name in object_services:
                service_id = seeded_services.get(service_name, _service_id(service_name))
                if service_name not in seeded_services:
                    upsert_service(
                        connection,
                        service_id=service_id,
                        service_name=service_name,
                        canonical_object_id=None,
                        owner=None,
                        team=None,
                        status="active",
                        service_criticality="not_classified",
                        support_entrypoints_json=json_dump([]),
                        dependencies_json=json_dump([]),
                        common_failure_modes_json=json_dump([]),
                        source="observed_relationship",
                    )
                _sync_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="service",
                    target_entity_id=service_id,
                    relationship_type="related_service",
                    provenance="source_sync",
                )

            for related_object_id in parsed.related_object_ids:
                _sync_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=related_object_id,
                    relationship_type="related_object",
                    provenance="source_sync",
                )

            superseded_by = parsed.metadata.get("superseded_by")
            if superseded_by:
                _sync_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(superseded_by),
                    relationship_type="superseded_by",
                    provenance="source_sync",
                )

            for related_runbook in parsed.metadata.get("related_runbooks", []):
                _sync_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(related_runbook),
                    relationship_type="related_runbook",
                    provenance="source_sync",
                )

            for related_known_error in parsed.metadata.get("related_known_errors", []):
                _sync_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(related_known_error),
                    relationship_type="related_known_error",
                    provenance="source_sync",
                )

            delete_citations_for_revision(connection, revision_id)
            for index, citation in enumerate(parsed.citations, start=1):
                insert_citation(
                    connection,
                    citation_id=f"{revision_id}-citation-{index}",
                    revision_id=revision_id,
                    claim_anchor=None,
                    source_type=str(citation.get("source_type", "document")),
                    source_ref=str(citation.get("source_ref", "")),
                    source_title=str(citation.get("source_title", "")),
                    note=str(citation.get("note")) if citation.get("note") is not None else None,
                    excerpt=str(citation.get("excerpt")) if citation.get("excerpt") is not None else None,
                    captured_at=str(citation.get("captured_at")) if citation.get("captured_at") is not None else None,
                    validity_status=str(citation.get("validity_status", "unverified")),
                    integrity_hash=str(citation.get("integrity_hash")) if citation.get("integrity_hash") is not None else None,
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
                owner=str(parsed.metadata["owner"]),
                team=str(parsed.metadata["team"]),
                trust_state=trust_state,
                approval_state=revision_state,
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
