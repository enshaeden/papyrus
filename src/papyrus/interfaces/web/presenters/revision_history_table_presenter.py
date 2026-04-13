from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
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
