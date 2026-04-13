from __future__ import annotations

READER_ROLE = "reader"
OPERATOR_ROLE = "operator"
ADMIN_ROLE = "admin"

ROLE_IDS = {READER_ROLE, OPERATOR_ROLE, ADMIN_ROLE}
READER_VISIBLE_LIFECYCLE_STATES = {"active"}
READER_VISIBLE_REVIEW_STATES = {"approved"}

_ACTOR_ROLE_MAP = {
    "local.operator": OPERATOR_ROLE,
    "local.reviewer": OPERATOR_ROLE,
    "local.manager": ADMIN_ROLE,
}


def normalize_role(role: str | None = None) -> str:
    normalized = str(role or "").strip().lower()
    if normalized in ROLE_IDS:
        return normalized
    return OPERATOR_ROLE


def role_from_actor_id(actor_id: str | None = None) -> str:
    normalized = str(actor_id or "").strip()
    if normalized in _ACTOR_ROLE_MAP:
        return _ACTOR_ROLE_MAP[normalized]
    return normalize_role(normalized)


def queue_ranking_for_role(role: str | None = None) -> str:
    normalized_role = normalize_role(role)
    if normalized_role == ADMIN_ROLE:
        return "triage"
    return "operator"


def object_visible_to_role(
    role: str | None,
    *,
    object_lifecycle_state: str | None,
    revision_review_state: str | None,
) -> bool:
    normalized_role = normalize_role(role)
    if normalized_role != READER_ROLE:
        return True
    return (
        str(object_lifecycle_state or "").strip() in READER_VISIBLE_LIFECYCLE_STATES
        and str(revision_review_state or "").strip() in READER_VISIBLE_REVIEW_STATES
    )


def filter_queue_items_for_role(
    items: list[dict[str, object]], role: str | None
) -> list[dict[str, object]]:
    normalized_role = normalize_role(role)
    if normalized_role != READER_ROLE:
        return items
    return [
        item
        for item in items
        if object_visible_to_role(
            normalized_role,
            object_lifecycle_state=str(item.get("object_lifecycle_state") or ""),
            revision_review_state=str(item.get("revision_review_state") or ""),
        )
    ]
