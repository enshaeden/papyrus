from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.application.role_visibility import normalize_role, queue_ranking_for_role, role_from_actor_id
from papyrus.infrastructure.paths import DB_PATH

from .impact_activity import event_history
from .queue_search import knowledge_queue
from .review_manage import manage_queue
from .services_dashboard import service_catalog


def _counts(*, read_queue: list[dict[str, Any]], manage: dict[str, Any], services: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "read_ready": sum(
            1
            for item in read_queue
            if bool(dict((item.get("ui_projection") or {}).get("use_guidance") or {}).get("safe_to_use"))
        ),
        "drafts": len(manage["draft_items"]),
        "review_required": len(manage["review_required"]),
        "ready_for_review": len(manage["ready_for_review"]),
        "needs_decision": len(manage["needs_decision"]),
        "needs_revalidation": len(manage["needs_revalidation"]),
        "needs_attention": len(manage["needs_attention"]),
        "weak_evidence": len(manage["weak_evidence_items"]),
        "stale": len(manage["stale_items"]),
        "services": len(services),
        "recent_activity": len(events),
    }

def home_dashboard(
    *,
    role: str | None = None,
    actor_id: str | None = None,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    resolved_role = normalize_role(role or role_from_actor_id(actor_id))
    read_queue = knowledge_queue(limit=16, database_path=database_path, ranking=queue_ranking_for_role(resolved_role), role=resolved_role)
    manage = manage_queue(database_path=database_path)
    services = service_catalog(database_path=database_path)
    events = event_history(limit=8, database_path=database_path)
    counts = _counts(read_queue=read_queue, manage=manage, services=services, events=events)

    layout_modes = {
        "reader": "library",
        "operator": "workshop",
        "admin": "control-room",
    }
    return {
        "role": resolved_role,
        "layout_mode": layout_modes.get(resolved_role, "workshop"),
        "counts": counts,
        "read_queue": read_queue,
        "manage": manage,
        "services": services,
        "events": events,
    }
