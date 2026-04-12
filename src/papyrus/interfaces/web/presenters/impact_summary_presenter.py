from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.view_helpers import escape, join_html


def render_impact_summary(
    *,
    components: ComponentPresenter,
    title: str,
    summary: str,
    impacted_count: int,
    recent_events_count: int,
    surface: str,
    related_services_count: int | None = None,
) -> str:
    badges = [
        components.badge(label="Impacted", value=impacted_count, tone="warning"),
        components.badge(label="Recent events", value=recent_events_count, tone="brand"),
    ]
    if related_services_count is not None:
        badges.append(components.badge(label="Related services", value=related_services_count, tone="context"))
    return (
        f'<section class="impact-summary" data-component="impact-summary" data-surface="{escape(surface)}">'
        '<div class="impact-summary__header">'
        '<p class="impact-summary__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        f"<p>{escape(summary)}</p>"
        "</div>"
        f'<div class="impact-summary__badges">{join_html(badges, " ")}</div>'
        "</section>"
    )
