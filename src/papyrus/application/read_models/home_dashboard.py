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


def _task_item(*, title: str, detail: str, href: str, metric: str = "", tone: str = "default") -> dict[str, str]:
    return {
        "title": title,
        "detail": detail,
        "href": href,
        "metric": metric,
        "tone": tone,
    }


def _launch_block(block_id: str, title: str, summary: str, items: list[dict[str, str]], *, tone: str = "default") -> dict[str, Any]:
    return {
        "block_id": block_id,
        "title": title,
        "summary": summary,
        "items": items,
        "tone": tone,
    }


def _operator_home(
    *,
    counts: dict[str, int],
    read_queue: list[dict[str, Any]],
    manage: dict[str, Any],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    safe_items = [item for item in read_queue if bool(dict((item.get("ui_projection") or {}).get("use_guidance") or {}).get("safe_to_use"))][:3]
    draft_items = manage["draft_items"][:3]
    watch_items = manage["needs_revalidation"][:3]
    return {
        "headline": "Start from the article, not the audit trail.",
        "intro": "Home is a launch surface for today’s work: open the safest guidance, continue drafts, and watch the few items that could block operators.",
        "primary_blocks": [
            _launch_block(
                "do_now",
                "Do now",
                "Open the best current guidance first.",
                [
                    _task_item(
                        title=item["title"],
                        detail=item["summary"],
                        href=f"/objects/{item['object_id']}",
                        metric=f"{item['object_type']} · {item['object_id']}",
                        tone="approved",
                    )
                    for item in safe_items
                ]
                or [_task_item(title="Read guidance", detail="Start from the read workspace.", href="/read", metric=str(counts["read_ready"]))],
                tone="approved",
            ),
            _launch_block(
                "continue",
                "Continue",
                "Move work already in flight before starting a new branch of work.",
                [
                    _task_item(
                        title=item["title"],
                        detail=item.get("change_summary") or item["summary"],
                        href=f"/objects/{item['object_id']}",
                        metric=f"{item['revision_review_state']} · {item['owner'] or 'unowned'}",
                        tone="brand",
                    )
                    for item in draft_items
                ]
                or [_task_item(title="Start a draft", detail="No drafts are waiting.", href="/write/objects/new", metric=str(counts["drafts"]))],
                tone="brand",
            ),
            _launch_block(
                "watch",
                "Watch",
                "These items should change today’s decisions only if they affect the article you are using.",
                [
                    _task_item(
                        title=item["title"],
                        detail=", ".join(item["reasons"][:2]) or "Needs follow-up.",
                        href=f"/objects/{item['object_id']}",
                        metric=item["trust_state"],
                        tone="warning",
                    )
                    for item in watch_items
                ]
                or [_task_item(title="Health board", detail="No urgent follow-up items are queued.", href="/health", metric=str(counts["needs_revalidation"]))],
                tone="warning",
            ),
        ],
        "secondary_blocks": [],
        "activity": [
            {
                "title": str(event.get("what_happened") or ""),
                "detail": str(event.get("next_action") or ""),
                "href": "/activity",
            }
            for event in events[:4]
            if str(event.get("next_action") or "").strip()
        ],
    }


def _reviewer_home(*, counts: dict[str, int], manage: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "headline": "Work the queue with decision context visible.",
        "intro": "Reviewer home is a workbench: pending decisions, blocked reviews, and trust exceptions are surfaced directly instead of being routed through generic launch cards.",
        "primary_blocks": [
            _launch_block(
                "queue_status",
                "Queue status",
                "See the shape of review pressure before opening an individual item.",
                [
                    _task_item(title="Needs decision", detail="Assigned items awaiting a decision.", href="/review", metric=str(counts["needs_decision"]), tone="warning"),
                    _task_item(title="Ready for review", detail="Submitted revisions without reviewer ownership.", href="/review", metric=str(counts["ready_for_review"]), tone="brand"),
                    _task_item(title="Needs revalidation", detail="Weak or stale guidance that can block approvals.", href="/health", metric=str(counts["needs_revalidation"]), tone="danger"),
                ],
                tone="brand",
            ),
            _launch_block(
                "pending_decisions",
                "Pending decisions",
                "Open the revisions that need a compact yes or no.",
                [
                    _task_item(
                        title=item["title"],
                        detail=item.get("change_summary") or item["summary"],
                        href=f"/manage/reviews/{item['object_id']}/{item['revision_id']}",
                        metric=item["assignment"]["reviewer"] if item.get("assignment") else "unassigned",
                        tone="warning",
                    )
                    for item in manage["needs_decision"][:4]
                ]
                or [_task_item(title="Open review queue", detail="No assigned decisions are waiting.", href="/review", metric="0")],
                tone="warning",
            ),
            _launch_block(
                "blocked_reviews",
                "Blocked reviews",
                "Clear the items that cannot move cleanly into approval.",
                [
                    _task_item(
                        title=item["title"],
                        detail=", ".join(item["reasons"][:2]) or "Needs reviewer intervention.",
                        href=f"/objects/{item['object_id']}",
                        metric=item["trust_state"],
                        tone="danger",
                    )
                    for item in manage["needs_revalidation"][:4]
                ]
                or [_task_item(title="Inspect health board", detail="No trust exceptions are blocking review right now.", href="/health", metric="0")],
                tone="danger",
            ),
        ],
        "secondary_blocks": [
            _launch_block(
                "governance_consequences",
                "Recent governance consequences",
                "Only recent events with reviewer follow-up stay on the home surface.",
                [
                    _task_item(title=str(event["what_happened"]), detail=str(event["next_action"]), href="/activity", metric=str(event["entity_type"]))
                    for event in events[:4]
                ],
            )
        ],
        "activity": [],
    }


def _manager_home(*, counts: dict[str, int], manage: dict[str, Any], services: list[dict[str, Any]]) -> dict[str, Any]:
    critical_services = [service for service in services if service["service_criticality"] in {"critical", "high"}][:4]
    return {
        "headline": "Portfolio pressure before item detail.",
        "intro": "Manager home is a pressure board: risk, review, service, and cleanup views are surfaced as portfolio signals rather than operator tasks.",
        "primary_blocks": [
            _launch_block(
                "risk_pressure",
                "Risk pressure",
                "Guidance that is weak, stale, or suspect enough to affect portfolio trust.",
                [
                    _task_item(title="Needs attention", detail="Items across review and trust queues.", href="/health", metric=str(counts["needs_attention"]), tone="danger"),
                    _task_item(title="Weak evidence", detail="Guidance with weak or missing source support.", href="/health", metric=str(counts["weak_evidence"]), tone="warning"),
                    _task_item(title="Stale guidance", detail="Articles due for revalidation.", href="/health", metric=str(counts["stale"]), tone="warning"),
                ],
                tone="danger",
            ),
            _launch_block(
                "review_pressure",
                "Review pressure",
                "Decision backlog and unowned review work.",
                [
                    _task_item(title="Queued reviews", detail="Total items in review.", href="/review", metric=str(counts["review_required"]), tone="warning"),
                    _task_item(title="Needs decision", detail="Assigned items waiting on reviewer action.", href="/review", metric=str(counts["needs_decision"]), tone="brand"),
                    _task_item(title="Ready for review", detail="Submitted work without an owner.", href="/review", metric=str(counts["ready_for_review"]), tone="brand"),
                ],
                tone="warning",
            ),
            _launch_block(
                "service_pressure",
                "Service pressure",
                "Start from service criticality when deciding where to intervene next.",
                [
                    _task_item(
                        title=service["service_name"],
                        detail=f"{service['status']} · {service['owner'] or 'unassigned'}",
                        href=f"/services/{service['service_id']}",
                        metric=service["service_criticality"],
                        tone="brand",
                    )
                    for service in critical_services
                ]
                or [_task_item(title="Service map", detail="Inspect service context.", href="/services", metric=str(counts["services"]))],
                tone="brand",
            ),
            _launch_block(
                "cleanup_pressure",
                "Cleanup pressure",
                "Debt that should be reduced before it turns into trust drag.",
                [
                    _task_item(title="Drafts and rejected work", detail="Unfinished or reworked guidance.", href="/review", metric=str(counts["drafts"]), tone="default"),
                    _task_item(title="Needs revalidation", detail="Items due for evidence or freshness review.", href="/health", metric=str(counts["needs_revalidation"]), tone="warning"),
                ],
            ),
        ],
        "secondary_blocks": [
            _launch_block(
                "portfolio_trends",
                "Where the pressure is concentrated",
                "Use these counts to choose the next board, not the next individual article.",
                [
                    _task_item(title="Review required", detail="Revisions still in motion.", href="/review", metric=str(counts["review_required"])),
                    _task_item(title="Services in scope", detail="Service records currently represented.", href="/services", metric=str(counts["services"])),
                    _task_item(title="Recent activity", detail="Recent changes and consequences.", href="/activity", metric=str(counts["recent_activity"])),
                ],
            )
        ],
        "activity": [],
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

    if actor.actor_id == "local.reviewer":
        shape = _reviewer_home(counts=counts, manage=manage, events=events)
    elif actor.actor_id == "local.manager":
        shape = _manager_home(counts=counts, manage=manage, services=services)
    else:
        shape = _operator_home(counts=counts, read_queue=read_queue, manage=manage, events=events)

    return {
        "actor_id": actor.actor_id,
        "layout_mode": (actor.page_behavior("home").mode if actor.page_behavior("home") is not None else "launchpad"),
        "counts": counts,
        "headline": shape["headline"],
        "intro": shape["intro"],
        "primary_blocks": shape["primary_blocks"],
        "secondary_blocks": shape["secondary_blocks"],
        "activity": shape["activity"],
        "events": events,
    }
