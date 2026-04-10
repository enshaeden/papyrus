from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_governed_action_panel, render_projection_status_panel
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path, tone_for_revision


def present_revision_history(
    renderer: TemplateRenderer,
    *,
    history: dict[str, Any],
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    object_info = history["object"]
    rows = [
        [
            f"#{escape(revision['revision_number'])}",
            components.badge(
                label="State",
                value=revision["revision_review_state"],
                tone=tone_for_revision(revision["revision_review_state"]),
            ),
            escape(revision["change_summary"] or "No summary recorded."),
            escape(", ".join(f"{status}={count}" for status, count in revision["citations"].items() if count) or "No citations"),
            escape("; ".join(f"{assignment['reviewer']} ({assignment['state']})" for assignment in revision["review_assignments"]) or "No assignments"),
            escape(format_timestamp(revision["imported_at"])),
            "Current" if revision["is_current"] else "",
        ]
        for revision in history["revisions"]
    ]
    history_table_html = components.section_card(
        title="Revision history",
        eyebrow="Read",
        body_html=components.queue_table(
            headers=["Revision", "State", "Change summary", "Citations", "Assignments", "Imported", "Current"],
            rows=rows,
            table_id="revision-history",
        ),
        footer_html=f'<p class="section-footer">{link(object_info["title"], f"/objects/{quoted_path(object_info['object_id'])}")} · {escape(object_info["canonical_path"])}</p>',
    )
    timeline_html = components.section_card(
        title="Audit sequence",
        eyebrow="Governance",
        body_html=join_html(
            [
                f'<div class="timeline-item"><strong>{escape(format_timestamp(event["occurred_at"]))}</strong><p>{escape(event["event_type"])} · {escape(event["actor"])}</p></div>'
                for event in history["audit_events"]
            ]
        ) or '<p class="empty-state-copy">No audit events recorded.</p>',
    )
    aside_sections = []
    if detail is not None:
        aside_sections.extend(
            [
                render_projection_status_panel(
                    components,
                    title="Current governed posture",
                    ui_projection=detail.get("ui_projection"),
                ),
                render_governed_action_panel(
                    components,
                    title="Current governed actions",
                    ui_projection=detail.get("ui_projection"),
                    object_id=str(object_info["object_id"]),
                    revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "") or None,
                ),
            ]
        )
    aside_sections.append(
        components.validation_summary(
            title="Comparison cues",
            findings=[
                "Look for the current marker before using the revision body.",
                "Citation counts show evidence drift even without a diff view.",
                "Assignment state exposes whether a review actually closed.",
            ],
        )
    )
    aside_html = join_html(aside_sections)
    return {
        "page_template": "pages/revision_history.html",
        "page_title": f"{object_info['title']} revision history",
        "headline": "Revision History",
        "kicker": "Read",
        "intro": "Revision state, review assignments, and audit sequence are kept side-by-side for comparison-friendly reading.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "history_table_html": history_table_html,
            "timeline_html": timeline_html,
        },
    }
