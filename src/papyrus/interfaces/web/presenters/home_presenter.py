from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link


def _area_card(
    components: ComponentPresenter,
    *,
    eyebrow: str,
    title: str,
    metric_label: str,
    metric_value: object,
    description: str,
    href: str,
    action_label: str,
    tone: str = "default",
    action_variant: str = "secondary",
) -> str:
    return components.section_card(
        title=title,
        eyebrow=eyebrow,
        tone=tone,
        body_html=(
            f'<p class="metric-value">{escape(metric_value)}</p>'
            f'<p><strong>{escape(metric_label)}</strong></p>'
            f"<p>{escape(description)}</p>"
        ),
        footer_html=link(action_label, href, css_class=f"button button-{escape(action_variant)}"),
    )


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


def _area_definitions(actor_id: str, *, counts: dict[str, int]) -> list[dict[str, str | int]]:
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


def _activity_rows(events: list[dict[str, Any]]) -> list[list[str]]:
    rows: list[list[str]] = []
    for event in events:
        summary = (
            str(event.get("what_happened") or "")
            or str(event.get("payload", {}).get("summary") or event.get("payload", {}).get("reason") or "No summary recorded.")
        )
        next_action = str(event.get("next_action") or "Inspect the affected object or service for the next step.")
        rows.append(
            [
                escape(format_timestamp(event["occurred_at"])),
                escape(summary),
                escape(f"{event['entity_type']}:{event['entity_id']}"),
                escape(next_action),
            ]
        )
    return rows


def present_home_page(
    renderer: TemplateRenderer,
    *,
    actor_id: str,
    counts: dict[str, int],
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    next_actions_html = join_html(
        [
            _area_card(
                components,
                eyebrow="Next",
                title=str(item["title"]),
                metric_label="Outstanding work",
                metric_value=item["count"],
                description=str(item["detail"]),
                href=str(item["href"]),
                action_label=str(item["label"]),
                tone="brand" if index == 0 else "default",
                action_variant="primary" if index == 0 else "secondary",
            )
            for index, item in enumerate(_next_action_definitions(actor_id, counts=counts))
        ]
    )
    work_areas_html = join_html(
        [
            _area_card(
                components,
                eyebrow="Route",
                title=str(item["title"]),
                metric_label=str(item["metric_label"]),
                metric_value=item["metric_value"],
                description=str(item["description"]),
                href=str(item["href"]),
                action_label=str(item["action_label"]),
                tone=str(item["tone"]),
            )
            for item in _area_definitions(actor_id, counts=counts)
        ]
    )
    summary_html = components.trust_summary(
        title="Current pressure",
        badges=(
            [
                components.badge(label="Review needed", value=counts["review_required"], tone="pending"),
                components.badge(label="Needs revalidation", value=counts["needs_revalidation"], tone="warning"),
                components.badge(label="Activity", value=counts["recent_activity"], tone="brand"),
            ]
            if actor_id == "local.reviewer"
            else [
                components.badge(label="Needs attention", value=counts["needs_attention"], tone="warning"),
                components.badge(label="Review needed", value=counts["review_required"], tone="pending"),
                components.badge(label="Services", value=counts["services"], tone="brand"),
            ]
            if actor_id == "local.manager"
            else [
                components.badge(label="Read ready", value=counts["read_ready"], tone="approved"),
                components.badge(label="Drafts", value=counts["drafts"], tone="pending"),
                components.badge(label="Needs revalidation", value=counts["needs_revalidation"], tone="warning"),
            ]
        ),
        summary="Use the top row to choose the next governed action.",
    )
    activity_html = components.section_card(
        title="Recent activity",
        eyebrow="Activity",
        body_html=(
            components.queue_table(
                headers=["When", "What happened", "Affected", "Next action"],
                rows=_activity_rows(events),
                table_id="home-activity",
            )
            if events
            else '<p class="empty-state-copy">No recent activity is recorded yet.</p>'
        ),
    )
    return {
        "page_template": "pages/home.html",
        "page_title": "Home",
        "page_surface": "home",
        "page_header": {
            "headline": "Home",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        "active_nav": "",
        "aside_html": "",
        "page_context": {
            "summary_html": summary_html,
            "next_actions_html": next_actions_html,
            "work_areas_html": work_areas_html,
            "activity_html": activity_html,
        },
    }
