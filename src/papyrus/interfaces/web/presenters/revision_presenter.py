from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_projection_overview_panel
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import object_url
from papyrus.interfaces.web.view_helpers import (
    escape,
    format_timestamp,
    join_html,
    link,
    tone_for_revision,
)


def revision_assignments_text(revision: dict[str, Any]) -> str:
    return (
        "; ".join(
            f"{assignment['reviewer']} ({assignment['state']})"
            for assignment in revision["review_assignments"]
        )
        or "No assignments"
    )


def render_revision_history_table(
    *, components: ComponentPresenter, history: dict[str, Any], role: str
) -> str:
    object_info = history["object"]
    rows = []
    for revision in history["revisions"]:
        revision_title = f"#{escape(revision['revision_number'])}"
        rows.append(
            "<tr>"
            f"<td>{components.decision_cell(title_html=revision_title, meta=[escape(format_timestamp(revision['imported_at']))])}</td>"
            "<td>"
            + components.decision_cell(
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
            )
            + "</td>"
            "<td>"
            + components.decision_cell(
                title_html=escape(revision["change_summary"] or "No summary recorded."),
                extra_html=components.inline_disclosure(
                    label="Evidence and assignments",
                    body_html=(
                        f"<p><strong>Citations:</strong> {escape(', '.join(f'{status}={count}' for status, count in revision['citations'].items() if count) or 'No citations')}</p>"
                        f"<p><strong>Assignments:</strong> {escape(revision_assignments_text(revision))}</p>"
                    ),
                ),
            )
            + "</td></tr>"
        )
    body_html = (
        '<table class="workbench-table" id="revision-history" data-component="table" data-surface="revision-history">'
        "<thead><tr><th>Revision</th><th>Status</th><th>What changed</th></tr></thead>"
        "<tbody>" + join_html(rows) + "</tbody></table>"
    )
    return (
        '<section class="revision-history-table" data-component="revision-history-table" data-surface="revision-history">'
        '<p class="revision-history-table__kicker">Content</p>'
        "<h2>Revision history</h2>"
        f"{body_html}"
        f'<p class="section-footer">{link(object_info["title"], object_url(role, str(object_info["object_id"])))} · {escape(object_info["canonical_path"])}</p>'
        "</section>"
    )


def render_revision_audit_sequence(
    *, components: ComponentPresenter, history: dict[str, Any]
) -> str:
    del components
    body_html = (
        join_html(
            [
                f'<div class="revision-audit-sequence__item"><strong>{escape(format_timestamp(event["occurred_at"]))}</strong><p>{escape(event["event_type"])} · {escape(event["actor"])}</p></div>'
                for event in history["audit_events"]
            ]
        )
        or '<p class="empty-state-copy">No audit events recorded.</p>'
    )
    return (
        '<section class="revision-audit-sequence" data-component="revision-audit-sequence" data-surface="revision-history">'
        '<p class="revision-audit-sequence__kicker">Governance</p>'
        "<h2>Audit sequence</h2>"
        f"{body_html}</section>"
    )


def render_revision_comparison_cues(*, components: ComponentPresenter) -> str:
    body_html = components.list_body(
        items=[
            escape("Look for the current marker before using the revision body."),
            escape("Citation counts show evidence drift even without a diff view."),
            escape("Assignment state exposes whether a review actually closed."),
        ],
        empty_label="No comparison cues recorded.",
        css_class="validation-findings",
    )
    return (
        '<section class="revision-comparison-cues" data-component="revision-comparison-cues" data-surface="revision-history">'
        '<p class="revision-comparison-cues__kicker">Content</p>'
        "<h2>Comparison cues</h2>"
        f"{body_html}</section>"
    )


def present_revision_history(
    renderer: TemplateRenderer,
    *,
    role: str,
    history: dict[str, Any],
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    object_info = history["object"]
    history_table_html = render_revision_history_table(
        components=components, history=history, role=role
    )
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
                revision_id=str((detail.get("current_revision") or {}).get("revision_id") or "")
                or None,
                current_revision_id=str(
                    (detail.get("current_revision") or {}).get("revision_id") or ""
                )
                or None,
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
