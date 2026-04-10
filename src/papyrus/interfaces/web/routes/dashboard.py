from __future__ import annotations

from papyrus.application.queries import trust_dashboard
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.dashboard_presenter import present_trust_dashboard
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request


def register(router, runtime) -> None:
    def trust_dashboard_page(request: Request):
        dashboard = trust_dashboard(database_path=runtime.database_path)
        page = present_trust_dashboard(runtime.template_renderer, dashboard=dashboard)
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_for_request(request),
                current_path=request.path,
                header_mode="compact",
                **page,
            )
        )

    router.add(["GET"], "/dashboard/trust", trust_dashboard_page)
    router.add(["GET"], "/health", trust_dashboard_page)
