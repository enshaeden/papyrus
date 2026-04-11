from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_projection_overview_panel
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path, tone_for_revision


def _revision_assignments_text(revision: dict[str, Any]) -> str:
    return "; ".join(
        f"{assignment['reviewer']} ({assignment['state']})"
        for assignment in revision["review_assignments"]
    ) or "No assignments"


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
            components.decision_cell(
                title_html=f"#{escape(revision['revision_number'])}",
                meta=[escape(format_timestamp(revision["imported_at"]))],
            ),
            components.decision_cell(
                title_html=escape(revision["revision_review_state"]),
                badges=[
                    components.badge(
                        label="State",
                        value=revision["revision_review_state"],
                        tone=tone_for_revision(revision["revision_review_state"]),
                    ),
                    components.badge(
                        label="Current",
                        value="Now" if revision["is_current"] else "Past",
                        tone="brand" if revision["is_current"] else "muted",
                    ),
                ],
            ),
            components.decision_cell(
                title_html=escape(revision["change_summary"] or "No summary recorded."),
                extra_html=components.inline_disclosure(
                    label="Evidence and assignments",
                    body_html=join_html(
                        [
                            f"<p><strong>Citations:</strong> {escape(', '.join(f'{status}={count}' for status, count in revision['citations'].items() if count) or 'No citations')}</p>",
                            f"<p><strong>Assignments:</strong> {escape(_revision_assignments_text(revision))}</p>",
                        ]
                    ),
                ),
            ),
        ]
        for revision in history["revisions"]
    ]
    history_table_html = components.surface_panel(
        title="Revision history",
        eyebrow="Read",
        body_html=components.table(
            headers=["Revision", "Status", "What changed"],
            rows=rows,
            table_id="revision-history",
            surface="revision-history",
        ),
        footer_html=f'<p class="section-footer">{link(object_info["title"], f"/objects/{quoted_path(object_info['object_id'])}")} · {escape(object_info["canonical_path"])}</p>',
        variant="history-table",
        surface="revision-history",
    )
    timeline_html = components.surface_panel(
        title="Audit sequence",
        eyebrow="Governance",
        body_html=join_html(
            [
                f'<div class="timeline-item"><strong>{escape(format_timestamp(event["occurred_at"]))}</strong><p>{escape(event["event_type"])} · {escape(event["actor"])}</p></div>'
                for event in history["audit_events"]
            ]
        ) or '<p class="empty-state-copy">No audit events recorded.</p>',
        variant="audit-sequence",
        surface="revision-history",
    )
    aside_sections = []
    if detail is not None:
        aside_sections.extend(
            [
                render_projection_overview_panel(
                    components,
                    title="Current posture and next actions",
                    ui_projection=detail.get("ui_projection"),
                    object_id=str(object_info["object_id"]),
                    revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "") or None,
                    current_revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "") or None,
                ),
            ]
        )
    aside_sections.append(
        components.surface_panel(
            title="Comparison cues",
            eyebrow="Read",
            body_html=components.list_body(
                items=[
                    escape("Look for the current marker before using the revision body."),
                    escape("Citation counts show evidence drift even without a diff view."),
                    escape("Assignment state exposes whether a review actually closed."),
                ],
                empty_label="No comparison cues recorded.",
                css_class="validation-findings",
            ),
            tone="context",
            variant="comparison-cues",
            surface="revision-history",
        )
    )
    aside_html = join_html(aside_sections)
    return {
        "page_template": "pages/revision_history.html",
        "page_title": f"{object_info['title']} revision history",
        "page_header": {
            "headline": "Revision history",
            "show_actor_links": True,
        },
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "history_table_html": history_table_html,
            "timeline_html": timeline_html,
        },
        "page_surface": "revision-history",
    }
