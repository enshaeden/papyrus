from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.application import impact_flow, review_flow, sync_flow, validation_flow
from papyrus.domain.entities import AuditEvent, KnowledgeObject, KnowledgeRevision, ReviewAssignment, ValidationIssue
from papyrus.infrastructure.paths import DB_PATH
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


def governance_workflow(database_path: Path = DB_PATH) -> review_flow.GovernanceWorkflow:
    return review_flow.GovernanceWorkflow(database_path)


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


def create_object_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeObject:
    return governance_workflow(database_path).create_object(**kwargs)


def create_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    return governance_workflow(database_path).create_revision(**kwargs)


def submit_for_review_command(database_path: Path = DB_PATH, **kwargs: Any) -> WorkflowAuditResult:
    return WorkflowAuditResult(governance_workflow(database_path).submit_for_review(**kwargs))


def assign_reviewer_command(database_path: Path = DB_PATH, **kwargs: Any) -> ReviewAssignment:
    return governance_workflow(database_path).assign_reviewer(**kwargs)


def approve_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    return governance_workflow(database_path).approve_revision(**kwargs)


def reject_revision_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeRevision:
    return governance_workflow(database_path).reject_revision(**kwargs)


def supersede_object_command(database_path: Path = DB_PATH, **kwargs: Any) -> KnowledgeObject:
    return governance_workflow(database_path).supersede_object(**kwargs)


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
