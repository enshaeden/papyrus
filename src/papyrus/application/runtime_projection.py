from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3

from papyrus.domain.entities import KnowledgeDocument
from papyrus.domain.lifecycle import DraftProgressState, RevisionReviewState, SourceSyncState
from papyrus.domain.policies import (
    approval_state_for_revision_state,
    citation_health_rank_for_counts,
    freshness_rank,
    ownership_rank,
    runtime_trust_state,
    trust_state,
)
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.markdown.serializer import json_dump, parse_iso_date
from papyrus.infrastructure.repositories.citation_repo import (
    citation_status_counts_for_revision,
    delete_citations_for_revision,
    insert_citation,
)
from papyrus.infrastructure.repositories.knowledge_repo import (
    delete_search_document,
    delete_projected_relationships,
    get_knowledge_object,
    get_knowledge_revision,
    replace_fts_document,
    update_knowledge_object_runtime_state,
    upsert_relationship,
    upsert_search_document,
)
from papyrus.infrastructure.repositories.service_repo import upsert_service
from papyrus.infrastructure.search.indexer import summarize_for_search
from papyrus.jobs.stale_scan import cadence_to_days


def relationship_id(
    source_type: str,
    source_id: str,
    target_type: str,
    target_id: str,
    rel_type: str,
) -> str:
    return hashlib.sha256(f"{source_type}|{source_id}|{target_type}|{target_id}|{rel_type}".encode("utf-8")).hexdigest()[:24]


def service_id(service_name: str) -> str:
    return hashlib.sha256(service_name.encode("utf-8")).hexdigest()[:24]


def persist_revision_artifacts(
    connection: sqlite3.Connection,
    *,
    parsed,
    revision_id: str,
    relationship_provenance: str,
    seeded_services: dict[str, str] | None = None,
) -> list[str]:
    object_id = parsed.document.knowledge_object_id
    service_lookup = dict(seeded_services or {})
    object_services = list(parsed.related_services)

    if parsed.object_type == "service_record":
        service_name = str(parsed.metadata["service_name"])
        object_services = list(dict.fromkeys([service_name, *object_services]))
        upsert_service(
            connection,
            service_id=service_id(service_name),
            service_name=service_name,
            canonical_object_id=object_id,
            owner=str(parsed.metadata["owner"]),
            team=str(parsed.metadata["team"]),
            status=str(parsed.metadata["status"]),
            service_criticality=str(parsed.metadata["service_criticality"]),
            support_entrypoints_json=json_dump(parsed.metadata.get("support_entrypoints", [])),
            dependencies_json=json_dump(parsed.metadata.get("dependencies", [])),
            common_failure_modes_json=json_dump(parsed.metadata.get("common_failure_modes", [])),
            source="service_record",
        )

    delete_projected_relationships(connection, object_id)
    for service_name in object_services:
        current_service_id = service_lookup.get(service_name, service_id(service_name))
        service_lookup[service_name] = current_service_id
        should_seed_service = seeded_services is None or service_name not in seeded_services
        if should_seed_service:
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
                source="observed_relationship",
            )
        upsert_relationship(
            connection,
            relationship_id=relationship_id(
                "knowledge_object",
                object_id,
                "service",
                current_service_id,
                "related_service",
            ),
            source_entity_type="knowledge_object",
            source_entity_id=object_id,
            target_entity_type="service",
            target_entity_id=current_service_id,
            relationship_type="related_service",
            provenance=relationship_provenance,
        )

    for related_object_id in parsed.related_object_ids:
        upsert_relationship(
            connection,
            relationship_id=relationship_id(
                "knowledge_object",
                object_id,
                "knowledge_object",
                str(related_object_id),
                "related_object",
            ),
            source_entity_type="knowledge_object",
            source_entity_id=object_id,
            target_entity_type="knowledge_object",
            target_entity_id=str(related_object_id),
            relationship_type="related_object",
            provenance=relationship_provenance,
        )

    superseded_by = parsed.metadata.get("superseded_by")
    if superseded_by:
        upsert_relationship(
            connection,
            relationship_id=relationship_id(
                "knowledge_object",
                object_id,
                "knowledge_object",
                str(superseded_by),
                "superseded_by",
            ),
            source_entity_type="knowledge_object",
            source_entity_id=object_id,
            target_entity_type="knowledge_object",
            target_entity_id=str(superseded_by),
            relationship_type="superseded_by",
            provenance=relationship_provenance,
        )

    for related_runbook in parsed.metadata.get("related_runbooks", []):
        upsert_relationship(
            connection,
            relationship_id=relationship_id(
                "knowledge_object",
                object_id,
                "knowledge_object",
                str(related_runbook),
                "related_runbook",
            ),
            source_entity_type="knowledge_object",
            source_entity_id=object_id,
            target_entity_type="knowledge_object",
            target_entity_id=str(related_runbook),
            relationship_type="related_runbook",
            provenance=relationship_provenance,
        )

    for related_known_error in parsed.metadata.get("related_known_errors", []):
        upsert_relationship(
            connection,
            relationship_id=relationship_id(
                "knowledge_object",
                object_id,
                "knowledge_object",
                str(related_known_error),
                "related_known_error",
            ),
            source_entity_type="knowledge_object",
            source_entity_id=object_id,
            target_entity_type="knowledge_object",
            target_entity_id=str(related_known_error),
            relationship_type="related_known_error",
            provenance=relationship_provenance,
        )

    delete_citations_for_revision(connection, revision_id)
    for index, citation in enumerate(parsed.citations, start=1):
        insert_citation(
            connection,
            citation_id=f"{revision_id}-citation-{index}",
            revision_id=revision_id,
            claim_anchor=str(citation.get("claim_anchor")).strip() if citation.get("claim_anchor") else None,
            source_type=str(citation.get("source_type", "document")),
            source_ref=str(citation.get("source_ref", "")),
            source_title=str(citation.get("source_title", "")),
            note=str(citation.get("note")).strip() if citation.get("note") else None,
            excerpt=str(citation.get("excerpt")).strip() if citation.get("excerpt") else None,
            captured_at=str(citation.get("captured_at")).strip() if citation.get("captured_at") else None,
            validity_status=str(citation.get("validity_status", "unverified")),
            integrity_hash=str(citation.get("integrity_hash")).strip() if citation.get("integrity_hash") else None,
            evidence_snapshot_path=(
                str(citation.get("evidence_snapshot_path")).strip()
                if citation.get("evidence_snapshot_path")
                else None
            ),
            evidence_expiry_at=str(citation.get("evidence_expiry_at")).strip() if citation.get("evidence_expiry_at") else None,
            evidence_last_validated_at=(
                str(citation.get("evidence_last_validated_at")).strip()
                if citation.get("evidence_last_validated_at")
                else None
            ),
        )

    return object_services


def refresh_current_object_projection(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    taxonomies: dict[str, dict[str, object]],
    as_of: dt.date | None = None,
) -> None:
    object_row = get_knowledge_object(connection, object_id)
    if object_row is None:
        return
    current_revision_id = object_row["current_revision_id"]
    if not current_revision_id:
        delete_search_document(connection, object_id)
        return

    revision_row = get_knowledge_revision(connection, current_revision_id)
    if revision_row is None:
        delete_search_document(connection, object_id)
        return

    metadata = json.loads(revision_row["normalized_payload_json"])
    document = KnowledgeDocument(
        source_path=parsed_source_path(str(object_row["canonical_path"])),
        relative_path=str(object_row["canonical_path"]),
        metadata=metadata,
        body=str(revision_row["body_markdown"]),
    )
    parsed = normalize_object_metadata(
        document,
        review_cadence_days=cadence_to_days(str(metadata["review_cadence"]), taxonomies),
        as_of=as_of or dt.date.today(),
    )
    citation_counts = citation_status_counts_for_revision(connection, str(revision_row["revision_id"]))
    citation_rank = citation_health_rank_for_counts(citation_counts)
    owner_rank_value = ownership_rank(str(metadata.get("owner", "")))
    object_lifecycle_state = str(object_row["object_lifecycle_state"] or object_row["status"])
    revision_review_state = str(revision_row["revision_review_state"] or revision_row["revision_state"])
    draft_progress_state = str(
        revision_row["draft_progress_state"] or revision_row["draft_state"] or DraftProgressState.READY_FOR_REVIEW.value
    )
    source_sync_state = str(object_row["source_sync_state"] or SourceSyncState.NOT_REQUIRED.value)
    fresh_rank = freshness_rank(
        object_lifecycle_state,
        parse_iso_date(metadata["last_reviewed"]),
        cadence_to_days(str(metadata["review_cadence"]), taxonomies),
        as_of or dt.date.today(),
    )
    base_trust_state = trust_state(
        status=object_lifecycle_state,
        freshness_rank_value=fresh_rank,
        citation_health_rank_value=citation_rank,
        ownership_rank_value=owner_rank_value,
    )
    effective_trust_state = runtime_trust_state(
        base_trust_state=base_trust_state,
        revision_state=revision_review_state,
        existing_trust_state=str(object_row["trust_state"]),
        preserve_existing_warning=True,
    )
    update_knowledge_object_runtime_state(
        connection,
        object_id=object_id,
        trust_state=effective_trust_state,
        object_lifecycle_state=object_lifecycle_state,
        source_sync_state=source_sync_state,
    )
    upsert_search_document(
        connection,
        object_id=object_id,
        revision_id=str(revision_row["revision_id"]),
        title=str(object_row["title"]),
        summary=str(object_row["summary"]),
        object_type=str(object_row["object_type"]),
        legacy_type=str(object_row["legacy_type"]) if object_row["legacy_type"] is not None else None,
        status=object_lifecycle_state,
        object_lifecycle_state=object_lifecycle_state,
        owner=str(object_row["owner"]),
        team=str(object_row["team"]),
        trust_state=effective_trust_state,
        approval_state=approval_state_for_revision_state(revision_review_state),
        revision_review_state=revision_review_state,
        draft_progress_state=draft_progress_state,
        source_sync_state=source_sync_state,
        freshness_rank=fresh_rank,
        citation_health_rank=citation_rank,
        ownership_rank=owner_rank_value,
        path=str(object_row["canonical_path"]),
        search_text=summarize_for_search(document),
    )
    replace_fts_document(
        connection,
        object_id=object_id,
        title=str(object_row["title"]),
        summary=str(object_row["summary"]),
        body=str(revision_row["body_markdown"]),
        tags=list(metadata.get("tags", [])),
        systems=list(metadata.get("systems", [])),
        services=list(
            parsed.related_services
            if parsed.object_type != "service_record"
            else list(dict.fromkeys([str(parsed.metadata["service_name"]), *parsed.related_services]))
        ),
    )


def parsed_source_path(relative_path: str):
    from papyrus.infrastructure.paths import ROOT

    return ROOT / relative_path
