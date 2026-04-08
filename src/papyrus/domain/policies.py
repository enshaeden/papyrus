from __future__ import annotations

import datetime as dt
from typing import Any

from papyrus.domain.value_objects import KnowledgeObjectType


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
    legacy_type = metadata.get("legacy_article_type") or metadata.get("type")
    if isinstance(legacy_type, str):
        return LEGACY_ARTICLE_TYPE_TO_OBJECT_TYPE.get(legacy_type)
    return None


def approval_state_for_status(status: str) -> str:
    return "approved" if status in {"active", "deprecated", "archived"} else "draft"


def ownership_rank(owner: str) -> int:
    return 1 if owner.strip() in PLACEHOLDER_OWNER_VALUES else 0


def citation_health_rank(citation_count: int, broken_count: int) -> int:
    if broken_count:
        return 2
    if citation_count == 0:
        return 1
    return 0


def freshness_rank(
    status: str,
    last_reviewed: dt.date,
    review_cadence_days: int | None,
    as_of: dt.date,
) -> int:
    if status == "draft":
        return 2
    if review_cadence_days is None:
        return 1
    due_date = last_reviewed + dt.timedelta(days=review_cadence_days)
    return 1 if due_date < as_of else 0


def trust_state(
    *,
    status: str,
    freshness_rank_value: int,
    citation_health_rank_value: int,
    ownership_rank_value: int,
) -> str:
    if freshness_rank_value > 0:
        return "stale"
    if citation_health_rank_value > 0:
        return "weak_evidence"
    if ownership_rank_value > 0:
        return "suspect"
    return "trusted" if status != "draft" else "suspect"
