from __future__ import annotations

from papyrus.application.queries import service_catalog, service_detail
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.service_presenter import present_service_catalog, present_service_detail
from papyrus.interfaces.web.route_utils import flash_html_for_request


def register(router, runtime) -> None:
    def service_catalog_page(request: Request):
        services = service_catalog(database_path=runtime.database_path)
        page = present_service_catalog(runtime.template_renderer, services=services)
        return html_response(runtime.page_renderer.render_page(search_value=request.query_value("query"), flash_html=flash_html_for_request(runtime, request), **page))

    def service_detail_page(request: Request):
        service_id = request.route_value("service_id")
        detail = service_detail(service_id, database_path=runtime.database_path)
        page = present_service_detail(runtime.template_renderer, detail=detail)
        return html_response(runtime.page_renderer.render_page(search_value=request.query_value("query"), flash_html=flash_html_for_request(runtime, request), **page))

    router.add(["GET"], "/services", service_catalog_page)
    router.add(["GET"], "/services/{service_id}", service_detail_page)
