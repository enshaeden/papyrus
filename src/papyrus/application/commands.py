from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from papyrus.application import sync_flow, validation_flow
from papyrus.domain.entities import ValidationIssue
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

