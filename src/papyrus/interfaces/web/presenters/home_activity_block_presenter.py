from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import OPERATOR_ROLE
from papyrus.interfaces.web.urls import activity_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def render_home_activity_block(*, dashboard: dict[str, Any]) -> str:
    role = str(dashboard.get("role") or "")
    if role != OPERATOR_ROLE:
        return ""

    events = [
        event
        for event in list(dashboard.get("events") or [])
        if str(event.get("next_action") or "").strip()
    ][:4]
    if events:
        lead_event = events[0]
        signal_html = (
            '<div class="home-activity-block__signal">'
            '<p class="home-activity-block__signal-label">Changed what to do</p>'
            f'<p class="home-activity-block__signal-title">{escape(lead_event["what_happened"])}</p>'
            f'<p class="home-activity-block__signal-detail">{escape(lead_event["next_action"])}</p>'
            "</div>"
        )
        list_html = (
            '<ul class="home-activity-block__list">'
            + join_html(
                [
                    (
                        '<li class="home-activity-block__item">'
                        '<div class="home-activity-block__copy">'
                        f'<p class="home-activity-block__title">{escape(event["what_happened"])}</p>'
                        f'<p class="home-activity-block__detail">{escape(event["next_action"])}</p>'
                        "</div>"
                        "</li>"
                    )
                    for event in events
                ]
            )
            + "</ul>"
        )
    else:
        signal_html = (
            '<div class="home-activity-block__signal">'
            '<p class="home-activity-block__signal-label">Changed what to do</p>'
            '<p class="home-activity-block__signal-title">No consequential changes are active right now.</p>'
            '<p class="home-activity-block__signal-detail">Keep working from the current guidance and use the activity feed only if you need a broader audit trail.</p>'
            "</div>"
        )
        list_html = (
            '<ul class="home-activity-block__list">'
            '<li class="home-activity-block__item">'
            '<div class="home-activity-block__copy">'
            '<p class="home-activity-block__title">Activity feed</p>'
            '<p class="home-activity-block__detail">Open the full activity surface for recent decisions, validations, and source-sync events.</p>'
            "</div>"
            "</li></ul>"
        )

    return (
        '<section class="home-activity-block" data-component="home-activity-block" data-surface="home">'
        '<div class="home-activity-block__head">'
        '<div class="home-activity-block__head-copy">'
        "<h2>Activity summary</h2>"
        "<p>Only changes that materially alter today’s next move stay on Home.</p>"
        "</div>"
        + link(
            "Open activity",
            activity_url(role),
            css_class="button button-ghost home-activity-block__action",
            attrs={"data-action-id": "open-activity"},
        )
        + "</div>"
        + signal_html
        + list_html
        + "</section>"
    )
