from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.infrastructure.paths import DB_PATH

from .impact_activity import event_history
from .queue_search import knowledge_queue
from .review_manage import manage_queue
from .services_dashboard import service_catalog


def _next_action_definitions(actor_id: str, *, counts: dict[str, int]) -> list[dict[str, str | int]]:
    shared = {
        "review": counts["review_required"],
        "revalidate": counts["needs_revalidation"],
        "activity": counts["recent_activity"],
        "drafts": counts["drafts"],
        "health": counts["needs_attention"],
    }
    if actor_id == "local.reviewer":
        return [
            {
                "title": "Make review decisions",
                "detail": "Work the revisions waiting on a decision.",
                "href": "/review",
                "label": "Review queued changes",
                "count": shared["review"],
            },
            {
                "title": "Revalidate weak guidance",
                "detail": "Clear stale or weak-evidence items.",
                "href": "/health",
                "label": "Review risky guidance",
                "count": shared["revalidate"],
            },
            {
                "title": "Inspect recent consequences",
                "detail": "Trace recent changes when the next step is unclear.",
                "href": "/activity",
                "label": "Inspect activity",
                "count": shared["activity"],
            },
        ]
    if actor_id == "local.manager":
        return [
            {
                "title": "Shepherd knowledge health",
                "detail": "Focus on the guidance that needs attention first.",
                "href": "/health",
                "label": "Review risky guidance",
                "count": shared["health"],
            },
            {
                "title": "Reduce review pressure",
                "detail": "Keep pending decisions from stalling.",
                "href": "/review",
                "label": "Review queued changes",
                "count": shared["review"],
            },
            {
                "title": "Inspect recent activity",
                "detail": "Use recent events to decide where to step in next.",
                "href": "/activity",
                "label": "Inspect activity",
                "count": shared["activity"],
            },
        ]
    return [
        {
            "title": "Use current guidance",
            "detail": "Start from the best current answer.",
            "href": "/read",
            "label": "Read guidance",
            "count": counts["read_ready"],
        },
        {
            "title": "Continue authoring",
            "detail": "Finish a draft or move a gap forward.",
            "href": "/write/objects/new",
            "label": "Start a draft",
            "count": shared["drafts"],
        },
        {
            "title": "Escalate unsafe guidance",
            "detail": "Hand off stale or weak guidance instead of guessing.",
            "href": "/health",
            "label": "Review risky guidance",
            "count": shared["revalidate"],
        },
    ]


def _work_area_definitions(actor_id: str, *, counts: dict[str, int]) -> list[dict[str, str | int]]:
    if actor_id == "local.reviewer":
        return [
            {
                "title": "Review / Approvals",
                "metric_label": "Queued decisions",
                "metric_value": counts["review_required"],
                "description": "Move the review queue first.",
                "href": "/review",
                "action_label": "Review queue",
                "tone": "brand",
            },
            {
                "title": "Knowledge Health",
                "metric_label": "Needs follow-up",
                "metric_value": counts["needs_attention"],
                "description": "Check weak, stale, or suspect guidance.",
                "href": "/health",
                "action_label": "Review risky guidance",
                "tone": "warning" if counts["needs_attention"] else "approved",
            },
            {
                "title": "Activity / History",
                "metric_label": "Recent events",
                "metric_value": counts["recent_activity"],
                "description": "Inspect recent consequences when a queue item is unclear.",
                "href": "/activity",
                "action_label": "Inspect activity",
                "tone": "default",
            },
        ]
    if actor_id == "local.manager":
        return [
            {
                "title": "Knowledge Health",
                "metric_label": "Needs follow-up",
                "metric_value": counts["needs_attention"],
                "description": "Triage the highest-risk guidance first.",
                "href": "/health",
                "action_label": "Review risky guidance",
                "tone": "brand" if counts["needs_attention"] else "approved",
            },
            {
                "title": "Review / Approvals",
                "metric_label": "Queued decisions",
                "metric_value": counts["review_required"],
                "description": "Reduce review pressure before it stalls changes.",
                "href": "/review",
                "action_label": "Review queue",
                "tone": "warning" if counts["review_required"] else "default",
            },
            {
                "title": "Services",
                "metric_label": "Services in scope",
                "metric_value": counts["services"],
                "description": "Start from service impact when intervention is unclear.",
                "href": "/services",
                "action_label": "Browse services",
                "tone": "default",
            },
        ]
    return [
        {
            "title": "Read",
            "metric_label": "Guidance items",
            "metric_value": counts["read_ready"],
            "description": "Find the current answer fast.",
            "href": "/read",
            "action_label": "Read guidance",
            "tone": "brand",
        },
        {
            "title": "Write",
            "metric_label": "Drafts or rework items",
            "metric_value": counts["drafts"],
            "description": "Create a draft or finish one in progress.",
            "href": "/write/objects/new",
            "action_label": "Start a draft",
            "tone": "default",
        },
        {
            "title": "Services",
            "metric_label": "Services in scope",
            "metric_value": counts["services"],
            "description": "Start from the affected service when you need context first.",
            "href": "/services",
            "action_label": "Browse services",
            "tone": "default",
        },
    ]


def home_dashboard(
    *,
    actor_id: str,
    database_path: str | Path = DB_PATH,
) -> dict[str, Any]:
    read_queue = knowledge_queue(limit=12, database_path=database_path)
    manage = manage_queue(database_path=database_path)
    services = service_catalog(database_path=database_path)
    events = event_history(limit=8, database_path=database_path)
    counts = {
        "read_ready": sum(
            1
            for item in read_queue
            if bool(dict((item.get("ui_projection") or {}).get("use_guidance") or {}).get("safe_to_use"))
        ),
        "drafts": len(manage["draft_items"]),
        "review_required": len(manage["review_required"]),
        "needs_revalidation": len(manage["needs_revalidation"]),
        "needs_attention": len(manage["needs_attention"]),
        "weak_evidence": len(manage["weak_evidence_items"]),
        "stale": len(manage["stale_items"]),
        "services": len(services),
        "recent_activity": len(events),
    }
    return {
        "counts": counts,
        "events": events,
        "next_actions": _next_action_definitions(actor_id, counts=counts),
        "work_areas": _work_area_definitions(actor_id, counts=counts),
        "summary_variant": actor_id,
    }
