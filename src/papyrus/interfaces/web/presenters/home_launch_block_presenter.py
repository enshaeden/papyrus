from __future__ import annotations

from collections.abc import Callable
from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, OPERATOR_ROLE, READER_ROLE
from papyrus.interfaces.web.urls import (
    activity_url,
    governance_url,
    object_url,
    review_decision_url,
    review_queue_url,
    service_catalog_url,
    service_url,
    write_new_url,
)
from papyrus.interfaces.web.view_helpers import escape, join_html, link

_HOME_LAUNCH_ACTION_LABELS = {
    "do_now": "Open",
    "continue": "Continue",
    "watch": "Inspect",
    "queue_status": "Open board",
    "pending_decisions": "Review",
    "blocked_reviews": "Inspect",
    "governance_consequences": "Open activity",
    "risk_pressure": "Open board",
    "review_pressure": "Open board",
    "service_pressure": "Open service",
    "cleanup_pressure": "Inspect",
    "portfolio_trends": "Open board",
}


def _humanize_token(token: str) -> str:
    return token.replace("_", " ").strip()


def _projection_summary(item: dict[str, Any]) -> str:
    use_guidance = dict((item.get("ui_projection") or {}).get("use_guidance") or {})
    return str(use_guidance.get("summary") or item.get("summary") or "No summary recorded.")


def _safe_to_use(item: dict[str, Any]) -> bool:
    use_guidance = dict((item.get("ui_projection") or {}).get("use_guidance") or {})
    return bool(use_guidance.get("safe_to_use"))


def _render_block_item(
    *,
    title: str,
    detail: str,
    href: str,
    metric: str = "",
    tone: str = "default",
    action_label: str,
    action_id: str = "open-home-launch-item",
) -> str:
    return (
        '<li class="home-launch-block__item">'
        '<div class="home-launch-block__copy">'
        f'<p class="home-launch-block__item-title">{escape(title)}</p>'
        f'<p class="home-launch-block__item-detail">{escape(detail)}</p>'
        "</div>"
        '<div class="home-launch-block__meta">'
        + (f'<p class="home-launch-block__metric">{escape(metric)}</p>' if metric else "")
        + link(
            action_label,
            href,
            css_class=f"button button-ghost home-launch-block__link tone-{escape(tone)}",
            attrs={"data-action-id": action_id},
        )
        + "</div></li>"
    )


def _render_block_shell(
    *, block_id: str, title: str, summary: str, tone: str, items_html: list[str]
) -> str:
    return (
        f'<section class="home-launch-block tone-{escape(tone)}" data-component="home-launch-block" data-surface="home" data-home-block="{escape(block_id)}">'
        '<div class="home-launch-block__head">'
        f'<p class="home-launch-block__kicker">{escape(block_id.replace("_", " "))}</p>'
        f"<h2>{escape(title)}</h2>"
        f'<p class="home-launch-block__summary">{escape(summary)}</p>'
        "</div>"
        '<ul class="home-launch-block__list">' + join_html(items_html) + "</ul></section>"
    )


def _render_do_now_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    safe_items = [item for item in dashboard["read_queue"] if _safe_to_use(item)][:3]
    items_html = [
        _render_block_item(
            title=str(item["title"]),
            detail=_projection_summary(item),
            href=object_url(role, str(item["object_id"])),
            metric=_humanize_token(str(item["object_type"])),
            tone="approved",
            action_label=_HOME_LAUNCH_ACTION_LABELS["do_now"],
            action_id="open-primary-surface",
        )
        for item in safe_items
    ] or [
        _render_block_item(
            title="Read guidance",
            detail="Start from the read workspace.",
            href="/reader/browse" if role == READER_ROLE else "/operator/read",
            metric=str(dashboard["counts"]["read_ready"]),
            tone="approved",
            action_label=_HOME_LAUNCH_ACTION_LABELS["do_now"],
        )
    ]
    return _render_block_shell(
        block_id="do_now",
        title="Do now",
        summary="Open the best current guidance first.",
        tone="approved",
        items_html=items_html,
    )


def _render_continue_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    draft_items = list(dashboard["manage"]["draft_items"])[:3]
    items_html = [
        _render_block_item(
            title=str(item["title"]),
            detail=str(item.get("change_summary") or item.get("summary") or "No summary recorded."),
            href=object_url(role, str(item["object_id"])),
            metric=f"{item['revision_review_state']} · {item['owner'] or 'unowned'}",
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["continue"],
        )
        for item in draft_items
    ] or [
        _render_block_item(
            title="Start a draft",
            detail="No drafts are waiting.",
            href=write_new_url(),
            metric=str(dashboard["counts"]["drafts"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["continue"],
        )
    ]
    return _render_block_shell(
        block_id="continue",
        title="Continue",
        summary="Move work already in flight before starting a new branch of work.",
        tone="brand",
        items_html=items_html,
    )


def _render_watch_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    watch_items = list(dashboard["manage"]["needs_revalidation"])[:3]
    items_html = [
        _render_block_item(
            title=str(item["title"]),
            detail=", ".join(item["reasons"][:2]) or "Needs follow-up.",
            href=object_url(role, str(item["object_id"])),
            metric=str(item["trust_state"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["watch"],
        )
        for item in watch_items
    ] or [
        _render_block_item(
            title="Health board",
            detail="No urgent follow-up items are queued.",
            href=governance_url(role),
            metric=str(dashboard["counts"]["needs_revalidation"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["watch"],
        )
    ]
    return _render_block_shell(
        block_id="watch",
        title="Watch",
        summary="These items should change today’s decisions only if they affect the article you are using.",
        tone="warning",
        items_html=items_html,
    )


def _render_queue_status_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title="Needs decision",
            detail="Assigned items awaiting a decision.",
            href=review_queue_url(role),
            metric=str(counts["needs_decision"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["queue_status"],
        ),
        _render_block_item(
            title="Ready for review",
            detail="Submitted revisions without reviewer ownership.",
            href=review_queue_url(role),
            metric=str(counts["ready_for_review"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["queue_status"],
        ),
        _render_block_item(
            title="Needs revalidation",
            detail="Weak or stale guidance that can block approvals.",
            href=governance_url(role),
            metric=str(counts["needs_revalidation"]),
            tone="danger",
            action_label=_HOME_LAUNCH_ACTION_LABELS["queue_status"],
        ),
    ]
    return _render_block_shell(
        block_id="queue_status",
        title="Queue status",
        summary="See the shape of review pressure before opening an individual item.",
        tone="brand",
        items_html=items_html,
    )


def _render_pending_decisions_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title=str(item["title"]),
            detail=str(item.get("change_summary") or item.get("summary") or "No summary recorded."),
            href=review_decision_url(role, str(item["object_id"]), str(item["revision_id"])),
            metric=str((item.get("assignment") or {}).get("reviewer") or "unassigned"),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["pending_decisions"],
        )
        for item in list(dashboard["manage"]["needs_decision"])[:4]
    ] or [
        _render_block_item(
            title="Open review queue",
            detail="No assigned decisions are waiting.",
            href=review_queue_url(role),
            metric="0",
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["pending_decisions"],
        )
    ]
    return _render_block_shell(
        block_id="pending_decisions",
        title="Pending decisions",
        summary="Open the revisions that need a compact yes or no.",
        tone="warning",
        items_html=items_html,
    )


def _render_blocked_reviews_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title=str(item["title"]),
            detail=", ".join(item["reasons"][:2]) or "Needs reviewer intervention.",
            href=object_url(role, str(item["object_id"])),
            metric=str(item["trust_state"]),
            tone="danger",
            action_label=_HOME_LAUNCH_ACTION_LABELS["blocked_reviews"],
        )
        for item in list(dashboard["manage"]["needs_revalidation"])[:4]
    ] or [
        _render_block_item(
            title="Inspect health board",
            detail="No trust exceptions are blocking review right now.",
            href=governance_url(role),
            metric="0",
            tone="danger",
            action_label=_HOME_LAUNCH_ACTION_LABELS["blocked_reviews"],
        )
    ]
    return _render_block_shell(
        block_id="blocked_reviews",
        title="Blocked reviews",
        summary="Clear the items that cannot move cleanly into approval.",
        tone="danger",
        items_html=items_html,
    )


def _render_governance_consequences_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title=str(event.get("what_happened") or "Recent event"),
            detail=str(event.get("next_action") or "Inspect activity."),
            href=activity_url(role),
            metric=str(event.get("entity_type") or "event"),
            tone="default",
            action_label=_HOME_LAUNCH_ACTION_LABELS["governance_consequences"],
            action_id="open-activity",
        )
        for event in list(dashboard["events"])[:4]
    ]
    return _render_block_shell(
        block_id="governance_consequences",
        title="Recent governance consequences",
        summary="Only recent events with reviewer follow-up stay on the home surface.",
        tone="default",
        items_html=items_html,
    )


def _render_risk_pressure_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title="Needs attention",
            detail="Items across review and trust queues.",
            href=governance_url(role),
            metric=str(counts["needs_attention"]),
            tone="danger",
            action_label=_HOME_LAUNCH_ACTION_LABELS["risk_pressure"],
        ),
        _render_block_item(
            title="Weak evidence",
            detail="Guidance with weak or missing source support.",
            href=governance_url(role),
            metric=str(counts["weak_evidence"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["risk_pressure"],
        ),
        _render_block_item(
            title="Stale guidance",
            detail="Articles due for revalidation.",
            href=governance_url(role),
            metric=str(counts["stale"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["risk_pressure"],
        ),
    ]
    return _render_block_shell(
        block_id="risk_pressure",
        title="Risk pressure",
        summary="Guidance that is weak, stale, or suspect enough to affect portfolio trust.",
        tone="danger",
        items_html=items_html,
    )


def _render_review_pressure_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title="Queued reviews",
            detail="Total items in review.",
            href=review_queue_url(role),
            metric=str(counts["review_required"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["review_pressure"],
        ),
        _render_block_item(
            title="Needs decision",
            detail="Assigned items waiting on reviewer action.",
            href=review_queue_url(role),
            metric=str(counts["needs_decision"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["review_pressure"],
        ),
        _render_block_item(
            title="Ready for review",
            detail="Submitted work without an owner.",
            href=review_queue_url(role),
            metric=str(counts["ready_for_review"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["review_pressure"],
        ),
    ]
    return _render_block_shell(
        block_id="review_pressure",
        title="Review pressure",
        summary="Decision backlog and unowned review work.",
        tone="warning",
        items_html=items_html,
    )


def _render_service_pressure_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or ADMIN_ROLE)
    critical_services = [
        service
        for service in list(dashboard["services"])
        if service["service_criticality"] in {"critical", "high"}
    ][:4]
    items_html = [
        _render_block_item(
            title=str(service["service_name"]),
            detail=f"{service['status']} · {service['owner'] or 'unassigned'}",
            href=service_url(role, str(service["service_id"])),
            metric=str(service["service_criticality"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["service_pressure"],
        )
        for service in critical_services
    ] or [
        _render_block_item(
            title="Service map",
            detail="Inspect service context.",
            href=service_catalog_url(role),
            metric=str(dashboard["counts"]["services"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["service_pressure"],
        )
    ]
    return _render_block_shell(
        block_id="service_pressure",
        title="Service pressure",
        summary="Start from service criticality when deciding where to intervene next.",
        tone="brand",
        items_html=items_html,
    )


def _render_cleanup_pressure_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title="Drafts and rejected work",
            detail="Unfinished or reworked guidance.",
            href=review_queue_url(role),
            metric=str(counts["drafts"]),
            tone="default",
            action_label=_HOME_LAUNCH_ACTION_LABELS["cleanup_pressure"],
        ),
        _render_block_item(
            title="Needs revalidation",
            detail="Items due for evidence or freshness review.",
            href=governance_url(role),
            metric=str(counts["needs_revalidation"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["cleanup_pressure"],
        ),
    ]
    return _render_block_shell(
        block_id="cleanup_pressure",
        title="Cleanup pressure",
        summary="Debt that should be reduced before it turns into trust drag.",
        tone="default",
        items_html=items_html,
    )


def _render_portfolio_trends_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    items_html = [
        _render_block_item(
            title="Review required",
            detail="Revisions still in motion.",
            href=review_queue_url(role),
            metric=str(counts["review_required"]),
            tone="default",
            action_label=_HOME_LAUNCH_ACTION_LABELS["portfolio_trends"],
        ),
        _render_block_item(
            title="Services in scope",
            detail="Service records currently represented.",
            href=service_catalog_url(role),
            metric=str(counts["services"]),
            tone="default",
            action_label=_HOME_LAUNCH_ACTION_LABELS["portfolio_trends"],
        ),
        _render_block_item(
            title="Recent activity",
            detail="Recent changes and consequences.",
            href=activity_url(role),
            metric=str(counts["recent_activity"]),
            tone="default",
            action_label=_HOME_LAUNCH_ACTION_LABELS["portfolio_trends"],
            action_id="open-activity",
        ),
    ]
    return _render_block_shell(
        block_id="portfolio_trends",
        title="Where the pressure is concentrated",
        summary="Use these counts to choose the next board, not the next individual article.",
        tone="default",
        items_html=items_html,
    )


_PRIMARY_RENDERERS: dict[str, list[Callable[[dict[str, Any]], str]]] = {
    READER_ROLE: [_render_do_now_block],
    OPERATOR_ROLE: [_render_do_now_block, _render_continue_block, _render_watch_block],
    ADMIN_ROLE: [
        _render_queue_status_block,
        _render_pending_decisions_block,
        _render_blocked_reviews_block,
        _render_risk_pressure_block,
        _render_review_pressure_block,
        _render_service_pressure_block,
    ],
}

_SECONDARY_RENDERERS: dict[str, list[Callable[[dict[str, Any]], str]]] = {
    READER_ROLE: [],
    OPERATOR_ROLE: [],
    ADMIN_ROLE: [
        _render_governance_consequences_block,
        _render_cleanup_pressure_block,
        _render_portfolio_trends_block,
    ],
}


def render_home_launch_blocks(*, dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    primary_renderers = _PRIMARY_RENDERERS.get(role, _PRIMARY_RENDERERS[OPERATOR_ROLE])
    secondary_renderers = _SECONDARY_RENDERERS.get(role, _SECONDARY_RENDERERS[OPERATOR_ROLE])
    primary_html = join_html([renderer(dashboard) for renderer in primary_renderers])
    secondary_html = join_html([renderer(dashboard) for renderer in secondary_renderers])
    return (
        '<div class="home-launch-area">'
        + (f'<div class="home-launch-grid">{primary_html}</div>' if primary_html else "")
        + (f'<div class="home-launch-secondary">{secondary_html}</div>' if secondary_html else "")
        + "</div>"
    )
