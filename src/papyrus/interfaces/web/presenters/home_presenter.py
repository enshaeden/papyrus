from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.home_activity_block_presenter import (
    render_home_activity_block,
)
from papyrus.interfaces.web.presenters.home_launch_block_presenter import render_home_launch_blocks
from papyrus.interfaces.web.rendering import TemplateRenderer


def present_home_page(renderer: TemplateRenderer, *, dashboard: dict[str, Any]) -> dict[str, Any]:
    del renderer
    role = str(dashboard.get("role") or "")
    return {
        "page_template": "pages/home.html",
        "page_title": "Overview" if role == "admin" else "Home",
        "page_surface": "home",
        "page_header": {
            "headline": "Overview" if role == "admin" else "Home",
        },
        "active_nav": "home",
        "aside_html": "",
        "page_context": {
            "home_launch_html": render_home_launch_blocks(dashboard=dashboard),
            "home_activity_html": render_home_activity_block(dashboard=dashboard),
        },
    }
