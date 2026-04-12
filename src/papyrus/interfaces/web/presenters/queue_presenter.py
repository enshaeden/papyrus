from __future__ import annotations

from typing import Any

from papyrus.domain.actor import resolve_actor
from papyrus.interfaces.web.presenters.read_filter_bar_presenter import render_read_filter_bar
from papyrus.interfaces.web.presenters.read_queue_hero_presenter import render_read_queue_hero
from papyrus.interfaces.web.presenters.read_results_presenter import render_read_result_cards, render_read_results_table
from papyrus.interfaces.web.presenters.read_selected_context_presenter import render_read_selected_context
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import join_html


def _selected_item(items: list[dict[str, Any]], *, selected_object_id: str, selected_revision_id: str) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id):
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
    actor_id: str = "",
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer
    actor = resolve_actor(actor_id or "local.operator")
    behavior = actor.page_behavior("read-queue")
    selected = _selected_item(items, selected_object_id=selected_object_id, selected_revision_id=selected_revision_id)
    dense_mode = bool(behavior and behavior.show_context_rail)
    headline = (
        "Search for the article you should read next."
        if actor.actor_id == "local.operator"
        else "Triage guidance with decision context visible."
    )
    intro = (
        "Operators see readable article candidates first; governance detail moves behind the article until it is needed."
        if actor.actor_id == "local.operator"
        else "Reviewer and manager search stays dense so trust, service impact, and next action stay in scan range."
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Read Guidance",
        "page_header": {
            "headline": "Read",
            "kicker": actor.display_name,
            "intro": intro,
        },
        "active_nav": "read",
        "aside_html": render_read_selected_context(item=selected) if dense_mode else "",
        "page_context": {
            "workspace_html": join_html(
                [
                    render_read_queue_hero(headline=headline, intro=intro),
                    render_read_filter_bar(
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
                        )
                        if dense_mode
                        else render_read_result_cards(items=items)
                    ),
                ]
            )
        },
        "page_surface": "read-queue",
    }
