from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, READER_ROLE
from papyrus.interfaces.web.experience import experience_for_role
from papyrus.interfaces.web.presenters.read_filter_bar_presenter import render_read_filter_bar
from papyrus.interfaces.web.presenters.read_results_presenter import (
    render_read_result_cards,
    render_read_results_table,
)
from papyrus.interfaces.web.presenters.read_selected_context_presenter import (
    render_read_selected_context,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import join_html


def _selected_item(
    items: list[dict[str, Any]], *, selected_object_id: str, selected_revision_id: str
) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (
            not selected_revision_id or revision_id == selected_revision_id
        ):
            return item
    return items[0]


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
    role: str,
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer
    experience = experience_for_role(role)
    behavior = experience.page_behavior("read-queue")
    selected = _selected_item(
        items, selected_object_id=selected_object_id, selected_revision_id=selected_revision_id
    )
    dense_mode = bool(behavior and behavior.show_context_rail)
    if role == READER_ROLE:
        intro = "Reader browse stays content-first and only surfaces reader-visible objects."
        page_title = "Browse Guidance"
        header_headline = "Browse"
        active_nav = "read"
    elif role == ADMIN_ROLE:
        intro = "Admin inspection stays dense so governance, service impact, and next action remain in scan range."
        page_title = "Inspect Guidance"
        header_headline = "Inspect"
        active_nav = "inspect"
    else:
        intro = "Operators see readable article candidates first; governance detail moves behind the article until it is needed."
        page_title = "Read Guidance"
        header_headline = "Read"
        active_nav = "read"
    return {
        "page_template": "pages/queue.html",
        "page_title": page_title,
        "page_header": {
            "headline": header_headline,
            "kicker": experience.label,
            "intro": intro,
        },
        "active_nav": active_nav,
        "aside_html": render_read_selected_context(role=role, item=selected) if dense_mode else "",
        "page_context": {
            "workspace_html": join_html(
                [
                    render_read_filter_bar(
                        role=role,
                        query=query,
                        selected_type=selected_type,
                        selected_trust=selected_trust,
                        selected_review_state=selected_review_state,
                    ),
                    (
                        render_read_results_table(
                            items=items,
                            query=query,
                            selected_type=selected_type,
                            selected_trust=selected_trust,
                            selected_review_state=selected_review_state,
                            selected_item=selected,
                            role=role,
                        )
                        if dense_mode
                        else render_read_result_cards(role=role, items=items)
                    ),
                ]
            )
        },
        "page_surface": "read-queue",
    }
