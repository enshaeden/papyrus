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
    counts: dict[str, int],
    next_actions: list[dict[str, str | int]],
    work_areas: list[dict[str, str | int]],
    events: list[dict[str, Any]],
    summary_variant: str,
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
            for index, item in enumerate(next_actions)
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
            for item in work_areas
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
            if summary_variant == "local.reviewer"
            else [
                components.badge(label="Needs attention", value=counts["needs_attention"], tone="warning"),
                components.badge(label="Review needed", value=counts["review_required"], tone="pending"),
                components.badge(label="Services", value=counts["services"], tone="brand"),
            ]
            if summary_variant == "local.manager"
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
