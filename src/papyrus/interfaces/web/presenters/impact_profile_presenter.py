from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, render_definition_rows


def render_impact_profile(
    *,
    title: str,
    rows: list[tuple[str, str]],
    footer_html: str,
    surface: str,
) -> str:
    return (
        f'<section class="impact-profile" data-component="impact-profile" data-surface="{escape(surface)}">'
        '<p class="impact-profile__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        f"{render_definition_rows([(label, escape(value)) for label, value in rows])}"
        f'<div class="impact-profile__footer">{footer_html}</div>'
        "</section>"
    )
