from __future__ import annotations

import datetime as dt
import hashlib
import sqlite3
from pathlib import Path

from papyrus.application.validation_flow import validate_knowledge_documents
from papyrus.infrastructure.db import recreate_database
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.markdown.serializer import date_to_iso, json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.citation_repo import insert_citation
from papyrus.infrastructure.repositories.knowledge_repo import (
    insert_knowledge_object,
    insert_knowledge_revision,
    load_knowledge_documents,
    load_object_schemas,
    load_policy,
    load_schema,
    load_taxonomies,
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


def _insert_relationship(
    connection: sqlite3.Connection,
    *,
    source_entity_type: str,
    source_entity_id: str,
    target_entity_type: str,
    target_entity_id: str,
    relationship_type: str,
    provenance: str,
) -> None:
    connection.execute(
        """
        INSERT INTO relationships (
            relationship_id,
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            relationship_type,
            provenance
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            _relationship_id(source_entity_type, source_entity_id, target_entity_type, target_entity_id, relationship_type),
            source_entity_type,
            source_entity_id,
            target_entity_type,
            target_entity_id,
            relationship_type,
            provenance,
        ),
    )


def _insert_search_document(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    title: str,
    summary: str,
    object_type: str,
    legacy_type: str | None,
    status: str,
    owner: str,
    team: str,
    trust_state: str,
    approval_state: str,
    freshness_rank: int,
    citation_health_rank: int,
    ownership_rank: int,
    path: str,
    search_text: str,
    body: str,
    tags: list[str],
    systems: list[str],
    services: list[str],
    has_fts5: bool,
) -> None:
    connection.execute(
        """
        INSERT INTO search_documents (
            object_id,
            revision_id,
            title,
            summary,
            object_type,
            legacy_type,
            status,
            owner,
            team,
            trust_state,
            approval_state,
            freshness_rank,
            citation_health_rank,
            ownership_rank,
            path,
            search_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            object_id,
            revision_id,
            title,
            summary,
            object_type,
            legacy_type,
            status,
            owner,
            team,
            trust_state,
            approval_state,
            freshness_rank,
            citation_health_rank,
            ownership_rank,
            path,
            search_text,
        ),
    )

    if has_fts5:
        connection.execute(
            """
            INSERT INTO knowledge_search (object_id, title, summary, body, tags, systems, services)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                object_id,
                title,
                summary,
                body,
                " ".join(tags),
                " ".join(systems),
                " ".join(services),
            ),
        )


def build_search_projection(database_path: Path) -> tuple[int, str]:
    policy = load_policy()
    documents = load_knowledge_documents(policy)
    object_schemas = load_object_schemas()
    legacy_schema = load_schema()
    taxonomies = load_taxonomies()
    issues = validate_knowledge_documents(documents, object_schemas, legacy_schema, taxonomies, policy)
    if issues:
        raise ValueError("index build aborted because validation failed")

    connection = recreate_database(database_path)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    try:
        has_fts5 = fts5_available(connection)
        apply_runtime_schema(connection, has_fts5=has_fts5)
        connection.execute("INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)", (1, now))

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

        insert_validation_run(
            connection,
            run_id="validation-sync-build",
            run_type="sync_preflight_validation",
            started_at=now,
            completed_at=now,
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
            revision_state = parsed.approval_state
            change_log = parsed.metadata.get("change_log") or []
            latest_change = change_log[-1]["summary"] if change_log else None

            insert_knowledge_object(
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
                trust_state=parsed.trust_state,
                current_revision_id=revision_id,
                tags_json=json_dump(parsed.metadata.get("tags", [])),
                systems_json=json_dump(parsed.metadata.get("systems", [])),
            )
            insert_knowledge_revision(
                connection,
                revision_id=revision_id,
                object_id=document.knowledge_object_id,
                revision_number=1,
                revision_state=revision_state,
                source_path=document.relative_path,
                content_hash=revision_hash,
                body_markdown=document.body,
                normalized_payload_json=normalized_metadata_json,
                legacy_metadata_json=json_dump(document.metadata),
                imported_at=now,
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
                _insert_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="service",
                    target_entity_id=service_id,
                    relationship_type="related_service",
                    provenance="source_sync",
                )

            for related_object_id in parsed.related_object_ids:
                _insert_relationship(
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
                _insert_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(superseded_by),
                    relationship_type="superseded_by",
                    provenance="source_sync",
                )

            for related_runbook in parsed.metadata.get("related_runbooks", []):
                _insert_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(related_runbook),
                    relationship_type="related_runbook",
                    provenance="source_sync",
                )

            for related_known_error in parsed.metadata.get("related_known_errors", []):
                _insert_relationship(
                    connection,
                    source_entity_type="knowledge_object",
                    source_entity_id=document.knowledge_object_id,
                    target_entity_type="knowledge_object",
                    target_entity_id=str(related_known_error),
                    relationship_type="related_known_error",
                    provenance="source_sync",
                )

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

            _insert_search_document(
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
                trust_state=parsed.trust_state,
                approval_state=parsed.approval_state,
                freshness_rank=parsed.freshness_rank,
                citation_health_rank=parsed.citation_health_rank,
                ownership_rank=parsed.ownership_rank,
                path=document.relative_path,
                search_text=summarize_for_search(document),
                body=document.body,
                tags=list(parsed.metadata.get("tags", [])),
                systems=list(parsed.metadata.get("systems", [])),
                services=object_services,
                has_fts5=has_fts5,
            )

            insert_audit_event(
                connection,
                event_id=f"sync-{document.knowledge_object_id}",
                event_type="source_synced",
                occurred_at=now,
                actor="sync_flow",
                object_id=document.knowledge_object_id,
                revision_id=revision_id,
                details_json=json_dump(
                    {
                        "object_type": parsed.object_type,
                        "source_path": document.relative_path,
                        "citation_count": len(parsed.citations),
                        "service_count": len(object_services),
                    }
                ),
            )

        insert_audit_event(
            connection,
            event_id="audit-validation-sync-build",
            event_type="validation_recorded",
            occurred_at=now,
            actor="sync_flow",
            object_id=None,
            revision_id=None,
            details_json=json_dump({"run_id": "validation-sync-build"}),
        )
        connection.commit()
    finally:
        connection.close()

    return len(documents), "fts5" if has_fts5 else "like-fallback"
