from __future__ import annotations

from enum import StrEnum


class KnowledgeObjectType(StrEnum):
    RUNBOOK = "runbook"
    KNOWN_ERROR = "known_error"
    SERVICE_RECORD = "service_record"
    POLICY = "policy"
    SYSTEM_DESIGN = "system_design"


class KnowledgeLifecycleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class RevisionReviewStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class ReviewAssignmentState(StrEnum):
    ASSIGNED = "assigned"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class TrustState(StrEnum):
    TRUSTED = "trusted"
    SUSPECT = "suspect"
    STALE = "stale"
    WEAK_EVIDENCE = "weak_evidence"


class CitationValidityStatus(StrEnum):
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    BROKEN = "broken"
    STALE = "stale"
