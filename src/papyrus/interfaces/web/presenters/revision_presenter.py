from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_projection_overview_panel
from papyrus.interfaces.web.presenters.revision_audit_sequence_presenter import render_revision_audit_sequence
from papyrus.interfaces.web.presenters.revision_comparison_cues_presenter import render_revision_comparison_cues
from papyrus.interfaces.web.presenters.revision_history_table_presenter import render_revision_history_table
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import join_html


def present_revision_history(
    renderer: TemplateRenderer,
    *,
    role: str,
    history: dict[str, Any],
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    object_info = history["object"]
    history_table_html = render_revision_history_table(components=components, history=history, role=role)
    timeline_html = render_revision_audit_sequence(components=components, history=history)
    aside_sections = []
    if detail is not None:
        aside_sections.append(
            render_projection_overview_panel(
                components,
                role=role,
                title="Current posture and next actions",
                ui_projection=detail.get("ui_projection"),
                object_id=str(object_info["object_id"]),
                revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "") or None,
                current_revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "") or None,
            )
        )
    aside_sections.append(render_revision_comparison_cues(components=components))
    aside_html = join_html(aside_sections)
    return {
        "page_template": "pages/revision_history.html",
        "page_title": f"{object_info['title']} revision history",
        "page_header": {
            "headline": "Revision history",
            "show_actor_links": True,
        },
        "active_nav": "inspect" if role == ADMIN_ROLE else "read",
        "aside_html": aside_html,
        "page_context": {
            "history_table_html": history_table_html,
            "timeline_html": timeline_html,
        },
        "page_surface": "revision-history",
    }
