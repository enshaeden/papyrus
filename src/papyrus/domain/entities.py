from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class KnowledgeDocument:
    source_path: Path
    relative_path: str
    metadata: dict[str, Any]
    body: str

    @property
    def knowledge_object_id(self) -> str:
        return str(self.metadata.get("id", ""))

    @property
    def article_id(self) -> str:
        return self.knowledge_object_id

    @property
    def object_type(self) -> str:
        value = self.metadata.get("knowledge_object_type") or self.metadata.get("type")
        return str(value or "")


@dataclass(frozen=True)
class KnowledgeObject:
    object_id: str
    object_type: str
    title: str
    status: str
    owner: str
    team: str
    canonical_path: str


@dataclass(frozen=True)
class KnowledgeRevision:
    revision_id: str
    object_id: str
    revision_number: int
    state: str
    approved_at: dt.datetime | None = None
    approved_by: str | None = None


@dataclass(frozen=True)
class Citation:
    citation_id: str
    revision_id: str
    source_type: str
    source_ref: str
    source_title: str
    note: str | None = None
    captured_at: dt.datetime | None = None
    validity_status: str = "unverified"
    integrity_hash: str | None = None


@dataclass(frozen=True)
class Service:
    service_id: str
    name: str
    owner: str
    status: str


@dataclass(frozen=True)
class Relationship:
    relationship_id: str
    source_object_id: str
    target_object_id: str
    relationship_type: str


@dataclass(frozen=True)
class ReviewAssignment:
    assignment_id: str
    object_id: str
    revision_id: str
    reviewer: str
    state: str


@dataclass(frozen=True)
class ValidationRun:
    run_id: str
    started_at: dt.datetime
    completed_at: dt.datetime | None = None
    status: str = "pending"
    findings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    event_type: str
    occurred_at: dt.datetime
    actor: str
    object_id: str | None = None
    revision_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationIssue:
    path: str
    message: str
    field: str | None = None

    def render(self) -> str:
        if self.field:
            return f"{self.path}: {self.field}: {self.message}"
        return f"{self.path}: {self.message}"


@dataclass(frozen=True)
class BrokenLink:
    source_path: str
    target: str
    reason: str


@dataclass(frozen=True)
class DuplicateCandidate:
    left_path: str
    right_path: str
    left_title: str
    right_title: str
    similarity: float


@dataclass(frozen=True)
class DocsPlacementWarning:
    path: str
    score: int
    signals: list[str]


@dataclass(frozen=True)
class SearchHit:
    object_id: str
    title: str
    summary: str
    content_type: str
    status: str
    path: str


@dataclass(frozen=True)
class ParsedKnowledgeObjectSource:
    document: KnowledgeDocument
    object_type: str
    legacy_type: str | None
    metadata: dict[str, Any]
    citations: list[dict[str, Any]]
    related_services: list[str]
    related_object_ids: list[str]
    trust_state: str
    approval_state: str
    freshness_rank: int
    citation_health_rank: int
    ownership_rank: int
