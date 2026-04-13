from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.urls import object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def _impact_selection_href(base_path: str, *, object_id: str, revision_id: str = "") -> str:
    return base_path + "?" + urlencode(
        {
            key: value
            for key, value in {
                "selected_object_id": object_id,
                "selected_revision_id": revision_id,
            }.items()
            if value
        }
    )


def render_impact_trace(
    *,
    components: ComponentPresenter,
    role: str,
    title: str,
    items: list[dict[str, Any]],
    base_path: str,
    selected_item: dict[str, Any] | None,
    surface: str,
    empty_label: str,
) -> str:
    if not items:
        return (
            f'<section class="impact-trace" data-component="impact-trace" data-surface="{escape(surface)}">'
            '<p class="impact-trace__kicker">Impact</p>'
            f"<h2>{escape(title)}</h2>"
            f'<p class="impact-trace__empty">{escape(empty_label)}</p>'
            "</section>"
        )
    rows: list[str] = []
    for item in items:
        object_id = str(item["object_id"])
        revision_id = str(item.get("revision_id") or "")
        is_selected = selected_item is not None and str(selected_item.get("object_id") or "") == object_id
        rows.append(
            f'<tr{" class=\"is-selected\"" if is_selected else ""}>'
            f'<td>{components.decision_cell(title_html=link(str(item["title"]), _impact_selection_href(base_path, object_id=object_id, revision_id=revision_id), css_class="selected-row-link"), supporting_html=escape(item["reason"]), meta=[escape(item["trust_state"])])}</td>'
            f'<td>{components.decision_cell(title_html=escape(item["what_changed"]), supporting_html=escape(" -> ".join(item["propagation_path"])))}</td>'
            f'<td>{components.decision_cell(title_html=escape(" | ".join(item["revalidate"])))}</td>'
            f'<td>{link("Open", object_url(role, object_id), css_class="button button-secondary")}</td>'
            "</tr>"
        )
    return (
        f'<section class="impact-trace" data-component="impact-trace" data-surface="{escape(surface)}">'
        '<p class="impact-trace__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        '<table class="workbench-table" id="impact-trace-table">'
        "<thead><tr><th>Guidance</th><th>Changed through</th><th>Revalidate</th><th>Open</th></tr></thead>"
        "<tbody>"
        + join_html(rows)
        + "</tbody></table></section>"
    )
