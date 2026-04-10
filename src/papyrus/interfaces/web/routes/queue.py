from __future__ import annotations

from typing import Any

from papyrus.application.queries import knowledge_queue, search_knowledge_objects
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.queue_presenter import present_queue_page
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request


def _apply_filters(
    items: list[dict[str, Any]],
    *,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
) -> list[dict[str, Any]]:
    filtered = items
    if selected_type:
        filtered = [item for item in filtered if item["object_type"] == selected_type]
    if selected_trust:
        filtered = [item for item in filtered if item["trust_state"] == selected_trust]
    if selected_review_state:
        filtered = [item for item in filtered if item["revision_review_state"] == selected_review_state]
    return filtered


def register(router, runtime) -> None:
    def queue_page(request: Request):
        query = request.query_value("query").strip()
        selected_type = request.query_value("object_type").strip()
        selected_trust = request.query_value("trust").strip()
        selected_review_state = request.query_value("review_state").strip()
        limit = int(request.query_value("limit", "100"))
        items = (
            search_knowledge_objects(query, limit=limit, database_path=runtime.database_path)
            if query
            else knowledge_queue(limit=limit, database_path=runtime.database_path)
        )
        items = _apply_filters(
            items,
            selected_type=selected_type,
            selected_trust=selected_trust,
            selected_review_state=selected_review_state,
        )
        page = present_queue_page(
            runtime.template_renderer,
            items=items,
            query=query,
            selected_type=selected_type,
            selected_trust=selected_trust,
            selected_review_state=selected_review_state,
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=query,
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/queue", queue_page)
    router.add(["GET"], "/read", queue_page)
