from __future__ import annotations

from enum import StrEnum

from papyrus.domain.lifecycle import (
    DraftProgressState,
    IngestionLifecycleState,
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
)


class KnowledgeObjectType(StrEnum):
    RUNBOOK = "runbook"
    KNOWN_ERROR = "known_error"
    SERVICE_RECORD = "service_record"
    POLICY = "policy"
    SYSTEM_DESIGN = "system_design"


KnowledgeLifecycleStatus = ObjectLifecycleState
RevisionReviewStatus = RevisionReviewState
DraftState = DraftProgressState
IngestionStatus = IngestionLifecycleState
SourceSyncStatus = SourceSyncState


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
