from __future__ import annotations

from papyrus.application.queries import home_dashboard
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.presenters.home_presenter import present_home_page
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.http import redirect_response


def register(router, runtime) -> None:
    def root_landing(_: Request):
        return redirect_response("/operator")

    def home_page(request: Request):
        experience = require_experience(request, "operator", "admin")
        dashboard = home_dashboard(role=experience.role, database_path=runtime.database_path)
        page = present_home_page(runtime.template_renderer, dashboard=dashboard)
        return html_response(
            runtime.page_renderer.render_page(
                search_value=request.query_value("query"),
                flash_html=flash_html_for_request(runtime, request),
                role_id=experience.role,
                current_path=request.path,
                **page,
            )
        )

    def admin_landing(_: Request):
        return redirect_response("/admin/overview")

    def reader_landing(_: Request):
        return redirect_response("/reader/browse")

    router.add(["GET"], "/", root_landing)
    router.add(["GET"], "/operator", home_page)
    router.add(["GET"], "/admin/overview", home_page)
    router.add(["GET"], "/admin", admin_landing)
    router.add(["GET"], "/reader", reader_landing)
