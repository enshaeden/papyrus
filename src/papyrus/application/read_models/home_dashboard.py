from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.domain.actor import resolve_actor
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
    actor_id: str,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    actor = resolve_actor(actor_id)
    ranking = "triage" if actor.actor_id in {"local.reviewer", "local.manager"} else "operator"
    read_queue = knowledge_queue(limit=16, database_path=database_path, ranking=ranking)
    manage = manage_queue(database_path=database_path)
    services = service_catalog(database_path=database_path)
    events = event_history(limit=8, database_path=database_path)
    counts = _counts(read_queue=read_queue, manage=manage, services=services, events=events)

    return {
        "actor_id": actor.actor_id,
        "layout_mode": (actor.page_behavior("home").mode if actor.page_behavior("home") is not None else "launchpad"),
        "counts": counts,
        "read_queue": read_queue,
        "manage": manage,
        "services": services,
        "events": events,
    }
