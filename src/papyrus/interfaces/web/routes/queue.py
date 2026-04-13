from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import queue_ranking_for_role
from papyrus.application.queries import knowledge_queue, search_knowledge_objects
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.queue_presenter import present_queue_page
from papyrus.interfaces.web.route_utils import flash_html_for_request


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
        experience = require_experience(request, "reader", "operator", "admin")
        query = request.query_value("query").strip()
        selected_type = request.query_value("object_type").strip()
        selected_trust = request.query_value("trust").strip()
        selected_review_state = request.query_value("review_state").strip()
        selected_object_id = request.query_value("selected_object_id").strip()
        selected_revision_id = request.query_value("selected_revision_id").strip()
        limit = int(request.query_value("limit", "100"))
        items = (
            search_knowledge_objects(query, limit=limit, database_path=runtime.database_path, role=experience.role)
            if query
            else knowledge_queue(
                limit=limit,
                database_path=runtime.database_path,
                ranking=queue_ranking_for_role(experience.role),
                role=experience.role,
            )
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
            role=experience.role,
            selected_object_id=selected_object_id,
            selected_revision_id=selected_revision_id,
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=query,
                flash_html=flash_html_for_request(runtime, request),
                role_id=experience.role,
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/reader/browse", queue_page)
    router.add(["GET"], "/operator/read", queue_page)
    router.add(["GET"], "/admin/inspect", queue_page)
