from __future__ import annotations

from typing import Any

from papyrus.domain.value_objects import KnowledgeObjectType


SUPPORTED_KNOWLEDGE_OBJECT_TYPES = (
    KnowledgeObjectType.RUNBOOK.value,
    KnowledgeObjectType.KNOWN_ERROR.value,
    KnowledgeObjectType.SERVICE_RECORD.value,
)


def searchable_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["searchable_statuses_default"])


def navigation_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["active_navigation_statuses"])


def status_rank_map(policy: dict[str, Any]) -> dict[str, int]:
    order = policy["lifecycle"]["searchable_status_order"]
    return {status: index for index, status in enumerate(order)}

