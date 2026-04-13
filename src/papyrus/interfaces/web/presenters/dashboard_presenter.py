from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.health_board_presenter import render_health_board
from papyrus.interfaces.web.presenters.health_cleanup_board_presenter import (
    render_health_cleanup_board,
)
from papyrus.interfaces.web.presenters.health_validation_board_presenter import (
    render_health_validation_board,
)
from papyrus.interfaces.web.rendering import TemplateRenderer


def present_trust_dashboard(
    renderer: TemplateRenderer,
    *,
    role: str,
    dashboard: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer, selected_object_id, selected_revision_id
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Knowledge Health",
        "page_header": {
            "headline": "Knowledge Health",
            "intro": "Stewardship and risk board",
        },
        "active_nav": "health",
        "aside_html": "",
        "page_context": {
            "summary_cards_html": (
                render_health_board(role=role, queue=dashboard["queue"])
                + render_health_cleanup_board(cleanup_counts=dashboard.get("cleanup_counts") or {})
                + render_health_validation_board(validation_posture=dashboard["validation_posture"])
            ),
            "primary_html": "",
        },
        "page_surface": "knowledge-health",
    }
