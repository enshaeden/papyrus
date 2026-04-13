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
    if not events:
        return ""

    return (
        '<section class="home-activity-block" data-component="home-activity-block" data-surface="home">'
        '<div class="home-activity-block__head">'
        "<h2>Recent activity</h2>"
        "<p>Only activity that could change today’s next step stays on this screen.</p>"
        "</div>"
        '<ul class="home-activity-block__list">'
        + join_html(
            [
                (
                    '<li class="home-activity-block__item">'
                    '<div class="home-activity-block__copy">'
                    f'<p class="home-activity-block__title">{escape(event["what_happened"])}</p>'
                    f'<p class="home-activity-block__detail">{escape(event["next_action"])}</p>'
                    "</div>"
                    '<div class="home-activity-block__meta">'
                    f'{link("Open", activity_url(role), css_class="button button-ghost", attrs={"data-action-id": "open-activity"})}'
                    "</div>"
                    "</li>"
                )
                for event in events
            ]
        )
        + "</ul></section>"
    )
