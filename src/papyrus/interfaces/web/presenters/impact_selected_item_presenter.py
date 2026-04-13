from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.urls import object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def render_impact_selected_item(*, item: dict[str, Any], role: str, surface: str) -> str:
    return (
        f'<section class="impact-selected-item" data-component="impact-selected-item" data-surface="{escape(surface)}">'
        '<p class="impact-selected-item__kicker">Selected item</p>'
        f'<h2>{escape(str(item["title"]))}</h2>'
        + join_html(
            [
                f"<p><strong>{escape(item['reason'])}</strong></p>",
                f"<p><strong>Trust:</strong> {escape(item['trust_state'])}</p>",
                f"<p><strong>Changed:</strong> {escape(item['what_changed'])}</p>",
                f"<p><strong>Propagation path:</strong> {escape(' -> '.join(item['propagation_path']))}</p>",
                f"<p><strong>Revalidate:</strong> {escape(' | '.join(item['revalidate']))}</p>",
            ]
        )
        + f'<div class="impact-selected-item__footer">{link("Open guidance", object_url(role, str(item["object_id"])), css_class="button button-secondary")}</div>'
        + "</section>"
    )
