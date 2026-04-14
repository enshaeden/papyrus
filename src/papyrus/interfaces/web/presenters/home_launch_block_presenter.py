from __future__ import annotations

from collections.abc import Callable
from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, OPERATOR_ROLE, READER_ROLE
from papyrus.interfaces.web.urls import (
    activity_url,
    import_list_url,
    object_url,
    oversight_url,
    review_decision_url,
    review_queue_url,
    service_catalog_url,
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
    "recent_changes": "Open history",
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


def _review_dashboard(dashboard: dict[str, Any]) -> dict[str, Any]:
    review = dashboard.get("review")
    if isinstance(review, dict):
        return review
    fallback = dashboard.get("manage")
    if isinstance(fallback, dict):
        return fallback
    return {}


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
    *,
    block_id: str,
    title: str,
    summary: str,
    tone: str,
    items_html: list[str],
    emphasis: str = "board",
    lead_action_html: str = "",
) -> str:
    return (
        f'<section class="home-launch-block tone-{escape(tone)} is-{escape(emphasis)}" data-component="home-launch-block" data-surface="home" data-home-block="{escape(block_id)}">'
        + '<div class="home-launch-block__head">'
        + '<div class="home-launch-block__head-copy">'
        + f'<p class="home-launch-block__kicker">{escape(block_id.replace("_", " "))}</p>'
        + f"<h2>{escape(title)}</h2>"
        + f'<p class="home-launch-block__summary">{escape(summary)}</p>'
        + "</div>"
        + (
            f'<div class="home-launch-block__head-action">{lead_action_html}</div>'
            if lead_action_html
            else ""
        )
        + "</div>"
        + '<ul class="home-launch-block__list">'
        + join_html(items_html)
        + "</ul></section>"
    )


def _render_do_now_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    safe_items = [item for item in dashboard["read_queue"] if _safe_to_use(item)][:3]
    primary_target = (
        object_url(role, str(safe_items[0]["object_id"]))
        if safe_items
        else "/reader/browse"
        if role == READER_ROLE
        else "/operator/read"
    )
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
            title="Open content",
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
        summary="Start with the strongest current guidance. Open the best answer first, then branch into work only if the article is missing or suspect.",
        tone="approved",
        items_html=items_html,
        emphasis="primary",
        lead_action_html=link(
            "Start here",
            primary_target,
            css_class="button button-primary home-launch-block__start",
            attrs={"data-action-id": "open-primary-surface"},
        ),
    )


def _render_continue_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    draft_items = list(_review_dashboard(dashboard).get("draft_items") or [])[:3]
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
            title="Start a primary template",
            detail="Create a runbook, known error, or service record.",
            href=write_new_url(),
            metric=str(dashboard["counts"]["drafts"]),
            tone="brand",
            action_label=_HOME_LAUNCH_ACTION_LABELS["continue"],
        )
    ]
    return _render_block_shell(
        block_id="continue",
        title="Continue",
        summary="Continue a governed revision before starting a new template.",
        tone="brand",
        items_html=items_html,
        emphasis="supporting",
    )


def _render_watch_block(dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    watch_items = list(_review_dashboard(dashboard).get("needs_revalidation") or [])[:3]
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
            title="Oversight",
            detail="No urgent follow-up items are queued.",
            href=oversight_url(role),
            metric=str(dashboard["counts"]["needs_revalidation"]),
            tone="warning",
            action_label=_HOME_LAUNCH_ACTION_LABELS["watch"],
        )
    ]
    return _render_block_shell(
        block_id="watch",
        title="Watch",
        summary="These items may change whether the current content is dependable.",
        tone="warning",
        items_html=items_html,
        emphasis="supporting",
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
            href=oversight_url(role),
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
        for item in list(_review_dashboard(dashboard).get("needs_decision") or [])[:4]
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
        for item in list(_review_dashboard(dashboard).get("needs_revalidation") or [])[:4]
    ] or [
        _render_block_item(
            title="Inspect health board",
            detail="No trust exceptions are blocking review right now.",
            href=oversight_url(role),
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


def _render_pressure_summary_block(dashboard: dict[str, Any]) -> str:
    counts = dashboard["counts"]
    role = str(dashboard.get("role") or ADMIN_ROLE)
    critical_services = sum(
        1
        for service in list(dashboard.get("services") or [])
        if str(service.get("service_criticality") or "") in {"critical", "high"}
    )
    items_html = [
        _render_block_item(
            title="Needs attention",
            detail="Weak evidence, stale guidance, or suspect objects that can slow approval.",
            href=oversight_url(role),
            metric=str(counts["needs_attention"]),
            tone="danger",
            action_label="Open health",
        ),
        _render_block_item(
            title="Ready for review",
            detail="Submitted revisions that still need reviewer ownership.",
            href=review_queue_url(role),
            metric=str(counts["ready_for_review"]),
            tone="warning",
            action_label="Open review",
        ),
        _render_block_item(
            title="Critical services in scope",
            detail="High-criticality service records that can shift where follow-up should land.",
            href=service_catalog_url(role),
            metric=str(critical_services),
            tone="brand",
            action_label="Open services",
        ),
    ]
    return _render_block_shell(
        block_id="pressure_summary",
        title="Pressure summary",
        summary="Use one compact pressure readout to decide whether the next move belongs in review, health, or service context.",
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
        _render_pressure_summary_block,
    ],
}

_SECONDARY_RENDERERS: dict[str, list[Callable[[dict[str, Any]], str]]] = {
    READER_ROLE: [],
    OPERATOR_ROLE: [],
    ADMIN_ROLE: [],
}


def _render_board_links_entry(*, dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    counts = dashboard["counts"]
    if role == ADMIN_ROLE:
        links = [
            ("Review queue", review_queue_url(role), f"{counts['review_required']} in review"),
            ("Health board", oversight_url(role), f"{counts['needs_attention']} need attention"),
            ("Services", service_catalog_url(role), f"{counts['services']} services"),
            ("Audit activity", activity_url(role), f"{counts['recent_activity']} recent events"),
        ]
    else:
        links = [
            (
                "Read workspace",
                "/reader/browse" if role == READER_ROLE else "/operator/read",
                f"{counts['read_ready']} ready to use",
            ),
            ("Write workspace", write_new_url(), f"{counts['drafts']} drafts in motion"),
            ("Import workbench", import_list_url(), "Bring external guidance into draft review"),
            (
                "Review queue",
                review_queue_url(role),
                f"{counts['review_required']} revisions in review",
            ),
            (
                "Health board",
                oversight_url(role),
                f"{counts['needs_revalidation']} items need follow-up",
            ),
            ("Services", service_catalog_url(role), f"{counts['services']} services in scope"),
            ("Activity", activity_url(role), f"{counts['recent_activity']} consequential changes"),
        ]
    return (
        '<section class="home-board-links" data-component="home-board-links" data-surface="home">'
        '<details class="home-board-links__details">'
        "<summary>View all boards</summary>"
        '<p class="home-board-links__summary">Keep the landing view focused, then branch into the full work surfaces only when you need broader context.</p>'
        '<ul class="home-board-links__list">'
        + join_html(
            [
                '<li class="home-board-links__item">'
                + link(title, href, css_class="home-board-links__link")
                + f'<span class="home-board-links__meta">{escape(detail)}</span>'
                + "</li>"
                for title, href, detail in links
            ]
        )
        + "</ul></details></section>"
    )


def render_home_launch_blocks(*, dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or OPERATOR_ROLE)
    primary_renderers = _PRIMARY_RENDERERS.get(role, _PRIMARY_RENDERERS[OPERATOR_ROLE])
    primary_html = join_html([renderer(dashboard) for renderer in primary_renderers])
    secondary_renderers = _SECONDARY_RENDERERS.get(role, _SECONDARY_RENDERERS[OPERATOR_ROLE])
    secondary_html = join_html([renderer(dashboard) for renderer in secondary_renderers])
    board_links_html = _render_board_links_entry(dashboard=dashboard)
    if role == OPERATOR_ROLE:
        operator_blocks = [renderer(dashboard) for renderer in primary_renderers]
        primary_block = operator_blocks[0] if operator_blocks else ""
        support_blocks = join_html(operator_blocks[1:])
        return (
            '<div class="home-launch-area role-operator">'
            + (f'<div class="home-launch-primary">{primary_block}</div>' if primary_block else "")
            + (f'<div class="home-launch-support">{support_blocks}</div>' if support_blocks else "")
            + board_links_html
            + (
                f'<div class="home-launch-secondary">{secondary_html}</div>'
                if secondary_html
                else ""
            )
            + "</div>"
        )
    return (
        f'<div class="home-launch-area role-{escape(role)}">'
        + (f'<div class="home-launch-grid">{primary_html}</div>' if primary_html else "")
        + board_links_html
        + (f'<div class="home-launch-secondary">{secondary_html}</div>' if secondary_html else "")
        + "</div>"
    )
