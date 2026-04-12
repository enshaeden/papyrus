from __future__ import annotations

from papyrus.application.queries import home_dashboard
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.home_presenter import present_home_page
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request


def register(router, runtime) -> None:
    def home_page(request: Request):
        actor_id = actor_for_request(request)
        dashboard = home_dashboard(actor_id=actor_id, database_path=runtime.database_path)
        page = present_home_page(runtime.template_renderer, dashboard=dashboard)
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                actor_id=actor_id,
                current_path=request.path,
                **page,
            )
        )

    router.add(["GET"], "/", home_page)
