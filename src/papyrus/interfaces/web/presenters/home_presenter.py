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
            "detail": "Go straight to the best current answer.",
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
                eyebrow="Lifecycle",
                title="Read",
                metric_label="Guidance items",
                metric_value=counts["read_ready"],
                description="Read the best current guidance and its trust signals.",
                href="/read",
                action_label="Read guidance",
                tone="brand",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Write",
                metric_label="Drafts or rework items",
                metric_value=counts["drafts"],
                description="Create or finish a draft.",
                href="/write/objects/new",
                action_label="Start a draft",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Review / Approvals",
                metric_label="Review items",
                metric_value=counts["review_required"],
                description="Review changes and make the next decision.",
                href="/review",
                action_label="Review queued changes",
            ),
            _area_card(
                components,
                eyebrow="Lifecycle",
                title="Knowledge Health",
                metric_label="Needs attention",
                metric_value=counts["needs_attention"],
                description="Prioritize stale, weak, or suspect guidance.",
                href="/health",
                action_label="Review risky guidance",
                tone="warning" if counts["needs_attention"] else "approved",
            ),
            _area_card(
                components,
                eyebrow="Context",
                title="Services",
                metric_label="Services in scope",
                metric_value=counts["services"],
                description="Start from a service and move into the linked guidance.",
                href="/services",
                action_label="Browse services",
            ),
            _area_card(
                components,
                eyebrow="Context",
                title="Activity / History",
                metric_label="Recent events",
                metric_value=counts["recent_activity"],
                description="Trace recent changes and their follow-up.",
                href="/activity",
                action_label="Inspect activity",
            ),
        ]
    )
    summary_html = components.trust_summary(
        title="Needs attention now",
        badges=[
            components.badge(label="Review needed", value=counts["review_required"], tone="pending"),
            components.badge(label="Needs revalidation", value=counts["needs_revalidation"], tone="warning"),
            components.badge(label="Weak evidence", value=counts["weak_evidence"], tone="warning"),
            components.badge(label="Stale", value=counts["stale"], tone="danger"),
            components.badge(label="Activity", value=counts["recent_activity"], tone="brand"),
        ],
        summary="Use this as the short list for what needs attention now.",
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
        "headline": "Guided Operational Knowledge",
        "kicker": "Lifecycle",
        "intro": "Read, draft, review, and revalidate guidance from one place.",
        "active_nav": "read",
        "aside_html": "",
        "page_context": {
            "summary_html": summary_html,
            "next_actions_html": next_actions_html,
            "work_areas_html": work_areas_html,
            "activity_html": activity_html,
        },
    }
