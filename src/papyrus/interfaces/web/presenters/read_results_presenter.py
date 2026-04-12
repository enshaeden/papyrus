from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def queue_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def selection_href(
    *,
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
    object_id: str,
    revision_id: str = "",
) -> str:
    params = {
        "query": query,
        "object_type": selected_type,
        "trust": selected_trust,
        "review_state": selected_review_state,
        "selected_object_id": object_id,
    }
    if revision_id:
        params["selected_revision_id"] = revision_id
    return "/read?" + urlencode({key: value for key, value in params.items() if value})


def read_status_line(item: dict[str, Any]) -> str:
    state = projection_state(item.get("ui_projection"))
    return " · ".join(
        entry
        for entry in [
            str(item.get("object_type") or "").replace("_", " "),
            str(state.get("revision_review_state") or item.get("revision_review_state") or "unknown"),
            str(state.get("trust_state") or item.get("trust_state") or "unknown"),
        ]
        if entry
    )


def linked_services_text(item: dict[str, Any]) -> str:
    linked_services = item.get("linked_services") or []
    if not linked_services:
        return "No linked service context."
    return ", ".join(str(service["service_name"]) for service in linked_services)


def render_read_result_cards(*, items: list[dict[str, Any]]) -> str:
    if not items:
        return '<section class="read-results-empty"><h2>No matching guidance</h2><p>Adjust the search or widen the filters.</p></section>'
    return join_html(
        [
            (
                '<article class="read-result-card" data-component="read-result-card" data-surface="read-queue">'
                '<div class="read-result-card__copy">'
                f'<p class="read-result-card__meta">{escape(read_status_line(item))}</p>'
                f'<h2>{link(item["title"], queue_item_href(item))}</h2>'
                f'<p class="read-result-card__summary">{escape(item.get("summary") or "No summary recorded.")}</p>'
                f'<p class="read-result-card__guidance">{escape(str(projection_use_guidance(item.get("ui_projection")).get("summary") or "Open the article for the full procedure."))}</p>'
                f'<p class="read-result-card__support">{escape(linked_services_text(item))}</p>'
                "</div>"
                '<div class="read-result-card__actions">'
                f'{link("Open article", queue_item_href(item), css_class="button button-primary", attrs={"data-action-id": "open-primary-surface"})}'
                + (
                    f'{link("Open service", f"/services/{quoted_path(item["linked_services"][0]["service_id"])}", css_class="button button-ghost")}'
                    if item.get("linked_services")
                    else ""
                )
                + "</div></article>"
            )
            for item in items
        ]
    )


def render_read_results_table(
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
    selected_item: dict[str, Any] | None,
) -> str:
    if not items:
        return '<section class="read-results-empty"><h2>No matching guidance</h2><p>Adjust the search or widen the filters.</p></section>'
    rows = []
    for item in items:
        object_id = str(item["object_id"])
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        is_selected = (
            selected_item is not None
            and str(selected_item.get("object_id") or "") == object_id
            and str(selected_item.get("revision_id") or selected_item.get("current_revision_id") or "") == revision_id
        )
        rows.append(
            (
                f'<tr{" class=\"is-selected\"" if is_selected else ""}>'
                f'<td><a class="selected-row-link" href="{escape(selection_href(query=query, selected_type=selected_type, selected_trust=selected_trust, selected_review_state=selected_review_state, object_id=object_id, revision_id=revision_id))}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("summary") or "")}</span></td>'
                f'<td>{escape(read_status_line(item))}</td>'
                f'<td>{escape(str(projection_use_guidance(item.get("ui_projection")).get("next_action") or "Inspect article"))}</td>'
                f'<td>{escape(linked_services_text(item))}</td>'
                f'<td>{link("Open", queue_item_href(item), css_class="button button-ghost", attrs={"data-action-id": "open-primary-surface"})}</td>'
                "</tr>"
            )
        )
    return (
        '<section class="read-results-table" data-component="read-results-table" data-surface="read-queue">'
        '<table class="workbench-table" id="read-queue-results">'
        "<thead><tr><th>Guidance</th><th>Status</th><th>Next action</th><th>Service</th><th>Open</th></tr></thead>"
        "<tbody>"
        + join_html(rows)
        + "</tbody></table></section>"
    )
