from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.urls import object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def render_service_path(*, role: str, linked_objects: list[dict[str, Any]]) -> str:
    if not linked_objects:
        return '<section class="service-path-empty" data-component="service-path-empty" data-surface="services"><h2>Linked guidance path</h2><p>No guidance is linked to this service yet.</p></section>'
    return (
        '<section class="service-path" data-component="service-path" data-surface="services">'
        "<h2>Linked guidance path</h2>"
        '<div class="service-path__list">'
        + join_html(
            [
                (
                    '<article class="service-path__item" data-component="service-path-item" data-surface="services">'
                    f'<p class="service-path__meta">{escape(item["relationship_type"])} · {escape(item["trust_state"])} · {escape(item["revision_review_state"] or "unknown")}</p>'
                    f"<h3>{link(item['title'], object_url(role, str(item['object_id'])))}</h3>"
                    f"<p>{escape(item['path'])}</p>"
                    f"{link('Read guidance', object_url(role, str(item['object_id'])), css_class='button button-ghost', attrs={'data-action-id': 'open-primary-surface'})}"
                    "</article>"
                )
                for item in linked_objects
            ]
        )
        + "</div></section>"
    )
