from __future__ import annotations

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def _control_card(*, key: str, title: str, href: str, summary: str) -> str:
    return (
        f'<article class="admin-control-card" data-component="admin-control-card" data-control-id="{escape(key)}" data-surface="admin-control">'
        f"<h2>{link(title, href)}</h2>"
        f"<p>{escape(summary)}</p>"
        "</article>"
    )


def present_admin_overview(renderer: TemplateRenderer) -> dict[str, object]:
    del renderer
    controls_html = join_html(
        [
            _control_card(
                key="users",
                title="Users",
                href="/admin/users",
                summary="Manage the local user and role boundary when administration is intentionally in scope.",
            ),
            _control_card(
                key="access",
                title="Access",
                href="/admin/access",
                summary="Inspect and adjust access policy decisions without blending them into shared work routes.",
            ),
            _control_card(
                key="spaces",
                title="Spaces",
                href="/admin/spaces",
                summary="Review governed space boundaries and structural ownership for the active deployment.",
            ),
            _control_card(
                key="templates",
                title="Templates",
                href="/admin/templates",
                summary="Inspect template administration separately from the shared writing workflow.",
            ),
            _control_card(
                key="schemas",
                title="Schemas",
                href="/admin/schemas",
                summary="Inspect schema administration without exposing it on reader or operator routes.",
            ),
            _control_card(
                key="settings",
                title="Settings",
                href="/admin/settings",
                summary="Hold system-level configuration and deployment governance in one admin-only surface.",
            ),
        ]
    )
    shared_work_html = join_html(
        [
            link("Read", "/read", css_class="button button-secondary"),
            link("Review", "/review", css_class="button button-secondary"),
            link("Governance", "/governance", css_class="button button-secondary"),
            link("Services", "/governance/services", css_class="button button-secondary"),
            link("Audit", "/admin/audit", css_class="button button-secondary"),
        ],
        " ",
    )
    return {
        "page_template": "pages/admin_control.html",
        "page_title": "Admin overview",
        "page_header": {"headline": "Admin overview"},
        "active_nav": "overview",
        "aside_html": "",
        "page_context": {
            "content_html": (
                '<section class="admin-overview" data-component="admin-overview" data-surface="admin-control">'
                "<h2>Control plane</h2>"
                "<p>Admin control stays separate from shared read, write, review, and governance work.</p>"
                f'<div class="admin-overview__controls">{controls_html}</div>'
                '<section class="admin-overview__shared-work" data-component="admin-overview-links" data-surface="admin-control">'
                "<h2>Shared work surfaces</h2>"
                f"{shared_work_html}</section>"
                "</section>"
            )
        },
        "page_surface": "overview",
    }


def present_admin_control_page(
    renderer: TemplateRenderer,
    *,
    key: str,
    title: str,
    summary: str,
    next_action: str,
) -> dict[str, object]:
    del renderer
    return {
        "page_template": "pages/admin_control.html",
        "page_title": title,
        "page_header": {"headline": title},
        "active_nav": key,
        "aside_html": "",
        "page_context": {
            "content_html": (
                f'<section class="admin-control-panel" data-component="admin-control-panel" data-control-id="{escape(key)}" data-surface="admin-control">'
                f"<h2>{escape(title)}</h2>"
                f"<p>{escape(summary)}</p>"
                '<div class="admin-control-panel__state" data-component="admin-control-state" data-surface="admin-control">'
                "<h3>Current state</h3>"
                "<p>No dedicated backend model is implemented for this control surface yet.</p>"
                f"<p>{escape(next_action)}</p>"
                "</div></section>"
            )
        },
        "page_surface": key,
    }
