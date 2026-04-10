from __future__ import annotations

import datetime as dt
from typing import Any

from papyrus.domain.lifecycle import ObjectLifecycleState, RevisionReviewState
from papyrus.domain.value_objects import KnowledgeObjectType, RevisionReviewStatus, TrustState


SUPPORTED_KNOWLEDGE_OBJECT_TYPES = (
    KnowledgeObjectType.RUNBOOK.value,
    KnowledgeObjectType.KNOWN_ERROR.value,
    KnowledgeObjectType.SERVICE_RECORD.value,
)

LEGACY_ARTICLE_TYPE_TO_OBJECT_TYPE = {
    "runbook": KnowledgeObjectType.RUNBOOK.value,
    "SOP": KnowledgeObjectType.RUNBOOK.value,
    "access": KnowledgeObjectType.RUNBOOK.value,
    "onboarding": KnowledgeObjectType.RUNBOOK.value,
    "offboarding": KnowledgeObjectType.RUNBOOK.value,
    "asset": KnowledgeObjectType.RUNBOOK.value,
    "incident": KnowledgeObjectType.RUNBOOK.value,
    "troubleshooting": KnowledgeObjectType.KNOWN_ERROR.value,
    "postmortem": KnowledgeObjectType.KNOWN_ERROR.value,
    "reference": KnowledgeObjectType.SERVICE_RECORD.value,
    "policy": KnowledgeObjectType.SERVICE_RECORD.value,
    "FAQ": KnowledgeObjectType.SERVICE_RECORD.value,
}

PLACEHOLDER_OWNER_VALUES = {"", "TBD", "service_owner"}
TRUST_STATE_RANKS = {
    TrustState.TRUSTED.value: 0,
    TrustState.WEAK_EVIDENCE.value: 1,
    TrustState.STALE.value: 2,
    TrustState.SUSPECT.value: 3,
}


def searchable_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["searchable_statuses_default"])


def navigation_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["active_navigation_statuses"])


def status_rank_map(policy: dict[str, Any]) -> dict[str, int]:
    order = policy["lifecycle"]["searchable_status_order"]
    return {status: index for index, status in enumerate(order)}


def primary_object_type(metadata: dict[str, Any]) -> str | None:
    explicit = metadata.get("knowledge_object_type")
    if isinstance(explicit, str) and explicit.strip():
        return explicit
    legacy_type = metadata.get("legacy_article_type")
    if isinstance(legacy_type, str):
        return LEGACY_ARTICLE_TYPE_TO_OBJECT_TYPE.get(legacy_type)
    return None


def bootstrap_revision_review_state(object_lifecycle_state: str) -> str:
    return (
        RevisionReviewState.APPROVED.value
        if object_lifecycle_state
        in {
            ObjectLifecycleState.ACTIVE.value,
            ObjectLifecycleState.DEPRECATED.value,
            ObjectLifecycleState.ARCHIVED.value,
        }
        else RevisionReviewState.DRAFT.value
    )


def ownership_rank(owner: str) -> int:
    return 1 if owner.strip() in PLACEHOLDER_OWNER_VALUES else 0


def citation_health_rank(citation_count: int, broken_count: int) -> int:
    return citation_health_rank_from_status_counts(
        citation_count=citation_count,
        broken_count=broken_count,
        stale_count=0,
        unverified_count=0,
    )


def citation_health_rank_from_status_counts(
    *,
    citation_count: int,
    broken_count: int = 0,
    stale_count: int = 0,
    unverified_count: int = 0,
) -> int:
    if broken_count:
        return 3
    if stale_count:
        return 2
    if unverified_count or citation_count == 0:
        return 1
    return 0


def citation_health_label(rank: int) -> str:
    if rank >= 3:
        return "broken"
    if rank == 2:
        return "stale"
    if rank == 1:
        return "unverified"
    return "verified"


def citation_validity_rank(status: str) -> int:
    ranking = {
        "verified": 0,
        "unverified": 1,
        "stale": 2,
        "broken": 3,
    }
    return ranking.get(str(status), 1)


def worse_citation_validity(left: str, right: str) -> str:
    return left if citation_validity_rank(left) >= citation_validity_rank(right) else right


def normalize_citation_validity_status(status: str | None) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"verified", "unverified", "stale", "broken"}:
        return normalized
    return "unverified"


def citation_status_counts(citation_statuses: list[str]) -> dict[str, int]:
    counts = {"verified": 0, "unverified": 0, "stale": 0, "broken": 0}
    for status in citation_statuses:
        counts[normalize_citation_validity_status(status)] += 1
    return counts


def citation_health_rank_for_statuses(citation_statuses: list[str]) -> int:
    counts = citation_status_counts(citation_statuses)
    return citation_health_rank_from_status_counts(
        citation_count=sum(counts.values()),
        broken_count=counts["broken"],
        stale_count=counts["stale"],
        unverified_count=counts["unverified"],
    )


def citation_health_rank_for_counts(counts: dict[str, int]) -> int:
    return citation_health_rank_from_status_counts(
        citation_count=sum(counts.values()),
        broken_count=int(counts.get("broken", 0) or 0),
        stale_count=int(counts.get("stale", 0) or 0),
        unverified_count=int(counts.get("unverified", 0) or 0),
    )


def freshness_rank(
    object_lifecycle_state: str,
    last_reviewed: dt.date,
    review_cadence_days: int | None,
    as_of: dt.date,
) -> int:
    if object_lifecycle_state == ObjectLifecycleState.DRAFT.value:
        return 2
    if review_cadence_days is None:
        return 0
    due_date = last_reviewed + dt.timedelta(days=review_cadence_days)
    return 1 if due_date < as_of else 0


def trust_state(
    *,
    object_lifecycle_state: str,
    freshness_rank_value: int,
    citation_health_rank_value: int,
    ownership_rank_value: int,
) -> str:
    del ownership_rank_value
    if freshness_rank_value > 0:
        return TrustState.STALE.value
    if citation_health_rank_value > 0:
        return TrustState.WEAK_EVIDENCE.value
    return (
        TrustState.TRUSTED.value
        if object_lifecycle_state != ObjectLifecycleState.DRAFT.value
        else TrustState.SUSPECT.value
    )


def runtime_trust_state(
    *,
    base_trust_state: str,
    revision_state: str,
    existing_trust_state: str | None = None,
    preserve_existing_warning: bool = True,
) -> str:
    if revision_state != RevisionReviewState.APPROVED.value:
        return TrustState.SUSPECT.value
    if preserve_existing_warning and existing_trust_state == TrustState.SUSPECT.value:
        return TrustState.SUSPECT.value
    if base_trust_state != TrustState.TRUSTED.value:
        return base_trust_state
    if preserve_existing_warning and existing_trust_state in {
        TrustState.STALE.value,
        TrustState.WEAK_EVIDENCE.value,
    }:
        return str(existing_trust_state)
    return TrustState.TRUSTED.value


def worse_trust_state(current: str, proposed: str) -> str:
    current_rank = TRUST_STATE_RANKS.get(str(current), 0)
    proposed_rank = TRUST_STATE_RANKS.get(str(proposed), 0)
    return proposed if proposed_rank >= current_rank else current


def relationship_strength_for(relationship_type: str, target_entity_type: str) -> float:
    if relationship_type == "superseded_by":
        return 0.95
    if target_entity_type == "service":
        return 0.9
    if relationship_type in {"related_runbook", "related_known_error"}:
        return 0.8
    if relationship_type == "related_object":
        return 0.7
    return 0.6


def relationship_direction_for(relationship_type: str, target_entity_type: str) -> str:
    if relationship_type == "superseded_by":
        return "reverse"
    if target_entity_type == "service":
        return "reverse"
    if relationship_type in {"related_object", "related_runbook", "related_known_error"}:
        return "reverse"
    return "bidirectional"
