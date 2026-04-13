from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.governed_presenter import projection_reasons, projection_use_guidance
from papyrus.interfaces.web.urls import review_queue_url
from papyrus.interfaces.web.view_helpers import escape, join_html


def render_review_lane(
    *,
    role: str,
    title: str,
    items: list[dict[str, Any]],
    active_object_id: str,
    active_revision_id: str,
    action_html_resolver,
) -> str:
    if not items:
        return (
            '<section class="review-lane" data-component="review-lane" data-surface="review">'
            f"<h2>{escape(title)}</h2><p class=\"review-lane-empty\">No items in this lane.</p></section>"
        )
    rows = []
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        is_selected = object_id == active_object_id and (not active_revision_id or revision_id == active_revision_id)
        use_guidance = projection_use_guidance(item.get("ui_projection"))
        rows.append(
            (
                f'<tr{" class=\"is-selected\"" if is_selected else ""}{" aria-selected=\"true\"" if is_selected else ""}>'
                f'<td><a class="selected-row-link" href="{escape(review_queue_url(role))}?selected_object_id={escape(object_id)}&selected_revision_id={escape(revision_id)}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("change_summary") or item.get("summary") or "")}</span></td>'
                f'<td>{escape(str(use_guidance.get("summary") or "Review item"))}</td>'
                f'<td>{escape(", ".join(projection_reasons(item.get("ui_projection"))) or "No explicit reasons")}</td>'
                f'<td>{escape(str(item.get("owner") or "Unowned"))}</td>'
                f'<td>{action_html_resolver(item)}</td>'
                "</tr>"
            )
        )
    return (
        '<section class="review-lane" data-component="review-lane" data-surface="review">'
        f"<h2>{escape(title)}</h2>"
        '<table class="workbench-table">'
        "<thead><tr><th>Guidance</th><th>Status</th><th>Why now</th><th>Owner</th><th>Action</th></tr></thead>"
        "<tbody>"
        + join_html(rows)
        + "</tbody></table></section>"
    )
