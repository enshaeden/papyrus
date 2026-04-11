from __future__ import annotations

from papyrus.application.queries import impact_view_for_object, impact_view_for_service
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.impact_presenter import present_object_impact, present_service_impact
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request


def register(router, runtime) -> None:
    def object_impact_page(request: Request):
        object_id = request.route_value("object_id")
        impact = impact_view_for_object(object_id, database_path=runtime.database_path)
        page = present_object_impact(
            runtime.template_renderer,
            impact=impact,
            selected_object_id=request.query_value("selected_object_id").strip(),
            selected_revision_id=request.query_value("selected_revision_id").strip(),
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                **page,
            )
        )

    def service_impact_page(request: Request):
        service_id = request.route_value("service_id")
        impact = impact_view_for_service(service_id, database_path=runtime.database_path)
        page = present_service_impact(
            runtime.template_renderer,
            impact=impact,
            selected_object_id=request.query_value("selected_object_id").strip(),
            selected_revision_id=request.query_value("selected_revision_id").strip(),
        )
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/impact/object/{object_id}", object_impact_page)
    router.add(["GET"], "/impact/service/{service_id}", service_impact_page)
