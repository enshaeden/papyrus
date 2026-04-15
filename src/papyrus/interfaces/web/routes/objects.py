from __future__ import annotations

from papyrus.application.queries import (
    knowledge_object_detail,
    reader_object_nav_tree,
    revision_history,
)
from papyrus.application.role_visibility import READER_ROLE
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.object_presenter import present_object_detail
from papyrus.interfaces.web.presenters.revision_presenter import present_revision_history
from papyrus.interfaces.web.route_utils import flash_html_for_request


def register(router, runtime) -> None:
    def object_detail_page(request: Request):
        object_id = request.route_value("object_id")
        experience = require_experience(request, "reader", "operator", "admin")
        detail = knowledge_object_detail(
            object_id, database_path=runtime.database_path, visibility_role=experience.role
        )
        reader_object_nav = (
            reader_object_nav_tree(
                current_object_id=object_id,
                current_path=str(detail["object"].get("path") or ""),
                current_canonical_path=str(detail["object"].get("canonical_path") or ""),
                database_path=runtime.database_path,
            )
            if experience.role == READER_ROLE
            else None
        )
        page = present_object_detail(
            runtime.template_renderer,
            detail=detail,
            experience=experience,
            reader_object_nav=reader_object_nav,
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                role_id=experience.role,
                current_path=request.path,
                **page,
            )
        )

    def object_revision_history_page(request: Request):
        object_id = request.route_value("object_id")
        experience = require_experience(request, "operator", "admin")
        history = revision_history(object_id, database_path=runtime.database_path)
        detail = knowledge_object_detail(
            object_id, database_path=runtime.database_path, visibility_role=experience.role
        )
        page = present_revision_history(
            runtime.template_renderer, history=history, detail=detail, role=experience.role
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                role_id=experience.role,
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/reader/object/{object_id}", object_detail_page)
    router.add(["GET"], "/operator/read/object/{object_id}", object_detail_page)
    router.add(["GET"], "/admin/inspect/object/{object_id}", object_detail_page)
    router.add(["GET"], "/operator/read/object/{object_id}/revisions", object_revision_history_page)
    router.add(["GET"], "/admin/inspect/object/{object_id}/revisions", object_revision_history_page)
