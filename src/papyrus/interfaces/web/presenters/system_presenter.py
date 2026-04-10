from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape


def present_error_page(
    renderer: TemplateRenderer,
    *,
    title: str,
    detail: str,
    status: str,
    action: str,
    active_nav: str = "manage",
) -> dict[str, object]:
    components = ComponentPresenter(renderer)
    error_html = components.surface_panel(
        title=title,
        eyebrow="System",
        body_html=f"<p>{escape(detail)}</p><p><strong>Next action:</strong> {escape(action)}</p><p class=\"section-footer\">HTTP status: {escape(status)}</p>",
        tone="danger" if status.startswith("5") else "default",
        variant="system-error",
        surface="system-error",
    )
    return {
        "page_template": "pages/error.html",
        "page_title": title,
        "page_header": {"headline": title},
        "active_nav": active_nav,
        "aside_html": "",
        "shell_variant": "minimal",
        "page_context": {"error_html": error_html},
        "page_surface": "system-error",
    }
