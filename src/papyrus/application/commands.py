from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.application import evidence_flow, event_flow, impact_flow, review_flow, sync_flow, validation_flow, writeback_flow
from papyrus.domain.actor import require_actor_id
from papyrus.domain.entities import AuditEvent, KnowledgeObject, KnowledgeRevision, ReviewAssignment, ValidationIssue
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.knowledge_repo import load_knowledge_documents


@dataclass(frozen=True)
class ValidationCommandResult:
    issues: list[ValidationIssue]
    document_count: int


@dataclass(frozen=True)
class ProjectionBuildResult:
    database_path: Path
    document_count: int
    mode: str


@dataclass(frozen=True)
class WorkflowAuditResult:
    event: AuditEvent


@dataclass(frozen=True)
class SourceWritebackCommandResult:
    object_id: str
    revision_id: str
    file_path: Path


@dataclass(frozen=True)
class EventIngestCommandResult:
    event_id: str
    event_type: str
    entity_type: str
    entity_id: str
    impacted_count: int


@dataclass(frozen=True)
class EvidenceCommandResult:
    object_id: str
    citation_ids: list[str]
    snapshot_path: str | None = None


def governance_workflow(
    database_path: Path = DB_PATH,
    *,
    source_root: Path = ROOT,
) -> review_flow.GovernanceWorkflow:
    return review_flow.GovernanceWorkflow(database_path, source_root=source_root)


def validate_repository_command(include_rendered_site: bool = False) -> ValidationCommandResult:
    issues = validation_flow.validate_repository(include_rendered_site=include_rendered_site)
    return ValidationCommandResult(
        issues=issues,
        document_count=len(load_knowledge_documents()),
    )


def build_projection_command(database_path: Path = DB_PATH) -> ProjectionBuildResult:
    document_count, mode = sync_flow.build_search_projection(database_path)
    return ProjectionBuildResult(
        database_path=database_path,
        document_count=document_count,
        mode=mode,
    )


def _require_actor_in_kwargs(kwargs: dict[str, Any]) -> None:
    kwargs["actor"] = require_actor_id(str(kwargs.get("actor") or ""))


def create_object_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeObject:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).create_object(**kwargs)


def create_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).create_revision(**kwargs)


def submit_for_review_command(database_path: Path = DB_PATH, **kwargs: Any) -> WorkflowAuditResult:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return WorkflowAuditResult(governance_workflow(database_path, source_root=source_root).submit_for_review(**kwargs))


def assign_reviewer_command(database_path: Path = DB_PATH, **kwargs: Any) -> ReviewAssignment:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).assign_reviewer(**kwargs)


def approve_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).approve_revision(**kwargs)


def reject_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).reject_revision(**kwargs)


def supersede_object_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeObject:
    source_root = Path(kwargs.pop("source_root", ROOT))
    _require_actor_in_kwargs(kwargs)
    return governance_workflow(database_path, source_root=source_root).supersede_object(**kwargs)


def writeback_object_command(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    source_root: Path | None = None,
) -> SourceWritebackCommandResult:
    actor = require_actor_id(actor)
    result = writeback_flow.write_object_to_source(
        database_path=database_path,
        object_id=object_id,
        actor=actor,
        root_path=source_root or ROOT,
    )
    return SourceWritebackCommandResult(
        object_id=result.object_id,
        revision_id=result.revision_id,
        file_path=result.file_path,
    )


def writeback_all_command(
    *,
    database_path: Path = DB_PATH,
    actor: str,
    source_root: Path | None = None,
) -> list[SourceWritebackCommandResult]:
    actor = require_actor_id(actor)
    results = writeback_flow.write_all_approved_revisions(
        database_path=database_path,
        actor=actor,
        root_path=source_root or ROOT,
    )
    return [
        SourceWritebackCommandResult(
            object_id=result.object_id,
            revision_id=result.revision_id,
            file_path=result.file_path,
        )
        for result in results
    ]


def ingest_event_command(
    *,
    database_path: Path = DB_PATH,
    event_type: str,
    source: str,
    entity_type: str,
    entity_id: str,
    payload: dict[str, Any] | None,
    actor: str,
    occurred_at: str | dt.datetime | None = None,
    event_id: str | None = None,
) -> EventIngestCommandResult:
    actor = require_actor_id(actor)
    result = event_flow.ingest_event(
        database_path=database_path,
        event_type=event_type,
        source=source,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        actor=actor,
        occurred_at=occurred_at,
        event_id=event_id,
    )
    return EventIngestCommandResult(
        event_id=result.event.event_id,
        event_type=result.event.event_type,
        entity_type=result.event.entity_type,
        entity_id=result.event.entity_id,
        impacted_count=len(result.impacted_objects),
    )


def mark_evidence_stale_command(
    *,
    database_path: Path = DB_PATH,
    actor: str,
    reason: str,
    citation_id: str | None = None,
    object_id: str | None = None,
) -> EvidenceCommandResult:
    actor = require_actor_id(actor)
    result = evidence_flow.mark_evidence_stale(
        database_path=database_path,
        actor=actor,
        reason=reason,
        citation_id=citation_id,
        object_id=object_id,
    )
    return EvidenceCommandResult(object_id=result.object_id, citation_ids=result.citation_ids)


def request_evidence_revalidation_command(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    notes: str | None = None,
) -> EvidenceCommandResult:
    actor = require_actor_id(actor)
    result = evidence_flow.request_evidence_revalidation(
        database_path=database_path,
        object_id=object_id,
        actor=actor,
        notes=notes,
    )
    return EvidenceCommandResult(object_id=result.object_id, citation_ids=result.citation_ids)


def attach_evidence_snapshot_command(
    *,
    database_path: Path = DB_PATH,
    citation_id: str,
    snapshot_source_path: str | Path,
    actor: str,
    expires_at: str | dt.datetime | None = None,
    root_path: Path | None = None,
) -> EvidenceCommandResult:
    actor = require_actor_id(actor)
    result = evidence_flow.attach_evidence_snapshot(
        database_path=database_path,
        citation_id=citation_id,
        snapshot_source_path=snapshot_source_path,
        actor=actor,
        expires_at=expires_at,
        root_path=root_path or ROOT,
    )
    return EvidenceCommandResult(
        object_id=result.object_id,
        citation_ids=result.citation_ids,
        snapshot_path=result.snapshot_path,
    )


def record_validation_run_command(
    *,
    database_path: Path = DB_PATH,
    run_id: str,
    run_type: str,
    status: str,
    finding_count: int,
    details: dict[str, Any],
    actor: str,
    started_at: dt.datetime | None = None,
    completed_at: dt.datetime | None = None,
) -> str:
    actor = require_actor_id(actor)
    return validation_flow.record_validation_run(
        database_path=database_path,
        run_id=run_id,
        run_type=run_type,
        status=status,
        finding_count=finding_count,
        details=details,
        actor=actor,
        started_at=started_at,
        completed_at=completed_at,
    )


def mark_object_suspect_due_to_change_command(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    reason: str,
    changed_entity_type: str,
    changed_entity_id: str | None = None,
) -> WorkflowAuditResult:
    actor = require_actor_id(actor)
    return WorkflowAuditResult(
        impact_flow.mark_object_suspect_due_to_change(
            database_path=database_path,
            object_id=object_id,
            actor=actor,
            reason=reason,
            changed_entity_type=changed_entity_type,
            changed_entity_id=changed_entity_id,
        )
    )
