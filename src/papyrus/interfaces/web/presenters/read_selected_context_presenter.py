from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.governed_presenter import projection_use_guidance
from papyrus.interfaces.web.view_helpers import escape, link

from .read_results_presenter import linked_services_text, queue_item_href, read_status_line


def render_read_selected_context(*, role: str, item: dict[str, Any] | None) -> str:
    if item is None:
        return ""
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return (
        '<section class="read-selected-context" data-component="read-selected-context" data-surface="read-queue">'
        '<p class="read-selected-context__kicker">Selected context</p>'
        f"<h2>{escape(item['title'])}</h2>"
        f"<p>{escape(str(use_guidance.get('summary') or item.get('summary') or 'No summary recorded.'))}</p>"
        f'<dl class="read-selected-context__facts"><div><dt>Status</dt><dd>{escape(read_status_line(item))}</dd></div><div><dt>Owner</dt><dd>{escape(item.get("owner") or "Unowned")}</dd></div><div><dt>Path</dt><dd>{escape(item.get("path") or "")}</dd></div><div><dt>Services</dt><dd>{escape(linked_services_text(item))}</dd></div></dl>'
        f'<p class="read-selected-context__next"><strong>Next:</strong> {escape(str(use_guidance.get("next_action") or "Inspect the article."))}</p>'
        f"{link('Open article', queue_item_href(item, role=role), css_class='button button-primary', attrs={'data-action-id': 'open-primary-surface'})}"
        "</section>"
    )
