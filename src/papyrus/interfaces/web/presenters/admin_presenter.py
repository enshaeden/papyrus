from __future__ import annotations

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def _control_card(*, key: str, title: str, href: str, summary: str) -> str:
    return (
        f'<article class="admin-control-card" data-component="admin-control-card" data-control-id="{escape(key)}" data-surface="admin-control">'
        f'<p class="panel-kicker">Admin control</p><h2>{link(title, href)}</h2>'
        f"<p>{escape(summary)}</p>"
        f"{link('Open', href, css_class='button button-secondary')}"
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
                summary="Role boundary, principal inventory, and account governance.",
            ),
            _control_card(
                key="access",
                title="Access",
                href="/admin/access",
                summary="Access policy, fail-closed checks, and visibility authority.",
            ),
            _control_card(
                key="spaces",
                title="Spaces",
                href="/admin/spaces",
                summary="Governed space boundaries and ownership structure.",
            ),
            _control_card(
                key="templates",
                title="Templates",
                href="/admin/templates",
                summary="Template inventory and governed authoring definitions.",
            ),
            _control_card(
                key="schemas",
                title="Schemas",
                href="/admin/schemas",
                summary="Schema inventory and structural policy surfaces.",
            ),
            _control_card(
                key="settings",
                title="Settings",
                href="/admin/settings",
                summary="Deployment posture and system configuration authority.",
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
                '<p class="page-kicker">Admin surfaces stay separate from shared work.</p>'
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
