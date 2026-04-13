from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, join_html


def render_impact_relationship_list(
    *,
    title: str,
    eyebrow: str,
    items_html: list[str],
    empty_label: str,
    surface: str,
) -> str:
    body_html = (
        '<div class="impact-relationship-list__items">'
        + join_html(
            [f'<div class="impact-relationship-list__item">{item}</div>' for item in items_html]
        )
        + "</div>"
        if items_html
        else f'<p class="impact-relationship-list__empty">{escape(empty_label)}</p>'
    )
    return (
        f'<section class="impact-relationship-list" data-component="impact-relationship-list" data-surface="{escape(surface)}">'
        f'<p class="impact-relationship-list__kicker">{escape(eyebrow)}</p>'
        f"<h2>{escape(title)}</h2>"
        f"{body_html}</section>"
    )
