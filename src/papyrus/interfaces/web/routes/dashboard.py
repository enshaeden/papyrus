from __future__ import annotations

from papyrus.application.queries import trust_dashboard
from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, html_response
from papyrus.interfaces.web.presenters.dashboard_presenter import present_trust_dashboard
from papyrus.interfaces.web.route_utils import flash_html_for_request


def register(router, runtime) -> None:
    def trust_dashboard_page(request: Request):
        experience = require_experience(request, "operator", "admin")
        dashboard = trust_dashboard(database_path=runtime.database_path)
        page = present_trust_dashboard(
            runtime.template_renderer,
            role=experience.role,
            dashboard=dashboard,
            selected_object_id=request.query_value("selected_object_id").strip(),
            selected_revision_id=request.query_value("selected_revision_id").strip(),
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

    router.add(["GET"], "/operator/review/governance", trust_dashboard_page)
    router.add(["GET"], "/admin/governance", trust_dashboard_page)
