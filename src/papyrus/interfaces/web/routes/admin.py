from __future__ import annotations

from papyrus.interfaces.web.experience import require_experience
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.admin_presenter import (
    present_admin_control_page,
    present_admin_overview,
)
from papyrus.interfaces.web.route_utils import flash_html_for_request


def _render_page(runtime, request: Request, *, page: dict[str, object]):
    experience = require_experience(request, "admin")
    return html_response(
        runtime.page_renderer.render_page(
            search_value=request.query_value("query"),
            flash_html=flash_html_for_request(runtime, request),
            role_id=experience.role,
            current_path=request.path,
            **page,
        )
    )


def register(router, runtime) -> None:
    def admin_landing(_: Request):
        return redirect_response("/admin/overview")

    def overview_page(request: Request):
        require_experience(request, "admin")
        return _render_page(runtime, request, page=present_admin_overview(runtime.template_renderer))

    def users_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="users",
                title="Users",
                summary="User administration remains admin-owned and absent from shared routes.",
                next_action="Add the backing user-management read model before introducing operational edits here.",
            ),
        )

    def access_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="access",
                title="Access",
                summary="Access governance belongs to the admin control plane, not to shared reader or operator shells.",
                next_action="Add explicit access policy data only when the backend source of truth exists.",
            ),
        )

    def spaces_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="spaces",
                title="Spaces",
                summary="Space boundaries and ownership stay governed separately from the shared knowledge work surfaces.",
                next_action="Implement the governed space inventory before turning this into an editing workflow.",
            ),
        )

    def templates_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="templates",
                title="Templates",
                summary="Template administration is reserved for admin control, even though shared writing consumes those definitions.",
                next_action="Back this page with template inventory data once template administration is implemented.",
            ),
        )

    def schemas_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="schemas",
                title="Schemas",
                summary="Schema administration remains an admin-only concern and must not leak into shared workflows.",
                next_action="Add schema inspection data when the admin schema surface is ready to be authoritative.",
            ),
        )

    def settings_page(request: Request):
        return _render_page(
            runtime,
            request,
            page=present_admin_control_page(
                runtime.template_renderer,
                key="settings",
                title="Settings",
                summary="System settings belong to the control plane and stay absent from the shared route model.",
                next_action="Introduce backed settings only when the runtime configuration contract is explicitly governed.",
            ),
        )

    router.add(["GET"], "/admin", admin_landing, minimum_visible_role="admin")
    router.add(["GET"], "/admin/overview", overview_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/users", users_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/access", access_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/spaces", spaces_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/templates", templates_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/schemas", schemas_page, minimum_visible_role="admin")
    router.add(["GET"], "/admin/settings", settings_page, minimum_visible_role="admin")
