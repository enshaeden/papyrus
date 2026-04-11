from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link


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


def _next_action_rows(items: list[dict[str, str | int]]) -> str:
    return join_html(
        [
            (
                f'<article class="next-action-row{" is-primary" if index == 0 else ""}">'
                f'<p class="next-action-count">{escape(item["count"])}</p>'
                '<div class="next-action-copy">'
                f'<p class="next-action-title">{escape(item["title"])}</p>'
                f'<p class="next-action-detail">{escape(item["detail"])}</p>'
                "</div>"
                f'{link(str(item["label"]), str(item["href"]), css_class="button button-primary" if index == 0 else "button button-secondary")}'
                "</article>"
            )
            for index, item in enumerate(items)
        ]
    )


def _work_area_rows(items: list[dict[str, str | int]]) -> str:
    return join_html(
        [
            (
                '<article class="work-area-row">'
                '<div class="work-area-copy">'
                f'<p class="work-area-title">{escape(item["title"])}</p>'
                f'<p class="work-area-detail">{escape(item["description"])}</p>'
                "</div>"
                '<div class="work-area-meta">'
                f'<p class="work-area-metric">{escape(item["metric_value"])}</p>'
                f'<p class="work-area-label">{escape(item["metric_label"])}</p>'
                f'{link(str(item["action_label"]), str(item["href"]), css_class="work-area-link")}'
                "</div></article>"
            )
            for item in items
        ]
    )


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
    next_actions_html = components.content_section(
        title="Next actions",
        eyebrow="Next",
        body_html=_next_action_rows(next_actions),
        variant="next-actions",
        surface="home",
    )
    work_areas_html = components.content_section(
        title="Work areas",
        eyebrow="Route",
        body_html=_work_area_rows(work_areas),
        variant="work-areas",
        surface="home",
    )
    activity_html = components.content_section(
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
