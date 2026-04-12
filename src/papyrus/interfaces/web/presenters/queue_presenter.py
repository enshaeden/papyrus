from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.domain.actor import resolve_actor
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def _queue_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _filters_html(query: str, selected_type: str, selected_trust: str, selected_review_state: str) -> str:
    return (
        '<form class="read-filters" method="get" action="/read" data-component="filter-bar" data-surface="read-queue">'
        '<div class="read-filters-search">'
        f'<input type="search" name="query" placeholder="Search by title, path, service, or summary" value="{escape(query)}" />'
        '<button class="button button-primary" type="submit">Search</button>'
        "</div>"
        '<div class="read-filters-row">'
        '<label><span>Type</span><select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbook</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known error</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service record</option>'
        f'<option value="policy"{" selected" if selected_type == "policy" else ""}>Policy</option>'
        f'<option value="system_design"{" selected" if selected_type == "system_design" else ""}>System design</option>'
        "</select></label>"
        '<label><span>Trust</span><select name="trust">'
        f'<option value=""{" selected" if not selected_trust else ""}>Any</option>'
        f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        "</select></label>"
        '<label><span>Review</span><select name="review_state">'
        f'<option value=""{" selected" if not selected_review_state else ""}>Any</option>'
        f'<option value="approved"{" selected" if selected_review_state == "approved" else ""}>Approved</option>'
        f'<option value="in_review"{" selected" if selected_review_state == "in_review" else ""}>In review</option>'
        f'<option value="draft"{" selected" if selected_review_state == "draft" else ""}>Draft</option>'
        f'<option value="rejected"{" selected" if selected_review_state == "rejected" else ""}>Rejected</option>'
        "</select></label>"
        "</div></form>"
    )


def _selection_href(
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


def _selected_item(items: list[dict[str, Any]], *, selected_object_id: str, selected_revision_id: str) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id):
            return item
    return items[0]


def _status_line(item: dict[str, Any]) -> str:
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


def _linked_services_text(item: dict[str, Any]) -> str:
    linked_services = item.get("linked_services") or []
    if not linked_services:
        return "No linked service context."
    return ", ".join(str(service["service_name"]) for service in linked_services)


def _operator_results_html(items: list[dict[str, Any]]) -> str:
    if not items:
        return '<section class="read-results-empty"><h2>No matching guidance</h2><p>Adjust the search or widen the filters.</p></section>'
    return join_html(
        [
            (
                '<article class="read-result-card" data-component="article-result" data-surface="read-queue">'
                '<div class="read-result-copy">'
                f'<p class="read-result-meta">{escape(_status_line(item))}</p>'
                f'<h2>{link(item["title"], _queue_item_href(item))}</h2>'
                f'<p class="read-result-summary">{escape(item.get("summary") or "No summary recorded.")}</p>'
                f'<p class="read-result-guidance">{escape(str(projection_use_guidance(item.get("ui_projection")).get("summary") or "Open the article for the full procedure."))}</p>'
                f'<p class="read-result-support">{escape(_linked_services_text(item))}</p>'
                "</div>"
                '<div class="read-result-actions">'
                f'{link("Open article", _queue_item_href(item), css_class="button button-primary", attrs={"data-action-id": "open-primary-surface"})}'
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


def _dense_results_html(
    items: list[dict[str, Any]],
    *,
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
                f'<td><a class="selected-row-link" href="{escape(_selection_href(query=query, selected_type=selected_type, selected_trust=selected_trust, selected_review_state=selected_review_state, object_id=object_id, revision_id=revision_id))}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("summary") or "")}</span></td>'
                f'<td>{escape(_status_line(item))}</td>'
                f'<td>{escape(str(projection_use_guidance(item.get("ui_projection")).get("next_action") or "Inspect article"))}</td>'
                f'<td>{escape(_linked_services_text(item))}</td>'
                f'<td>{link("Open", _queue_item_href(item), css_class="button button-ghost", attrs={"data-action-id": "open-primary-surface"})}</td>'
                "</tr>"
            )
        )
    return (
        '<section class="read-workbench" data-component="table" data-surface="read-queue">'
        '<table class="workbench-table" id="read-queue-results">'
        "<thead><tr><th>Guidance</th><th>Status</th><th>Next action</th><th>Service</th><th>Open</th></tr></thead>"
        "<tbody>"
        + join_html(rows)
        + "</tbody></table></section>"
    )


def _selected_context_html(item: dict[str, Any] | None) -> str:
    if item is None:
        return ""
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return (
        '<section class="selected-context" data-component="selected-context" data-surface="read-queue">'
        "<p class=\"selected-context-kicker\">Selected context</p>"
        f'<h2>{escape(item["title"])}</h2>'
        f'<p>{escape(str(use_guidance.get("summary") or item.get("summary") or "No summary recorded."))}</p>'
        f'<dl class="selected-context-facts"><div><dt>Status</dt><dd>{escape(_status_line(item))}</dd></div><div><dt>Owner</dt><dd>{escape(item.get("owner") or "Unowned")}</dd></div><div><dt>Path</dt><dd>{escape(item.get("path") or "")}</dd></div><div><dt>Services</dt><dd>{escape(_linked_services_text(item))}</dd></div></dl>'
        f'<p class="selected-context-next"><strong>Next:</strong> {escape(str(use_guidance.get("next_action") or "Inspect the article."))}</p>'
        f'{link("Open article", _queue_item_href(item), css_class="button button-primary", attrs={"data-action-id": "open-primary-surface"})}'
        "</section>"
    )


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
    actor_id: str = "",
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer
    actor = resolve_actor(actor_id or "local.operator")
    behavior = actor.page_behavior("read-queue")
    selected = _selected_item(items, selected_object_id=selected_object_id, selected_revision_id=selected_revision_id)
    dense_mode = bool(behavior and behavior.show_context_rail)
    headline = (
        "Search for the article you should read next."
        if actor.actor_id == "local.operator"
        else "Triage guidance with decision context visible."
    )
    intro = (
        "Operators see readable article candidates first; governance detail moves behind the article until it is needed."
        if actor.actor_id == "local.operator"
        else "Reviewer and manager search stays dense so trust, service impact, and next action stay in scan range."
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Read Guidance",
        "page_header": {
            "headline": "Read",
            "kicker": actor.display_name,
            "intro": intro,
        },
        "active_nav": "read",
        "aside_html": _selected_context_html(selected) if dense_mode else "",
        "page_context": {
            "workspace_html": (
                '<section class="read-hero" data-component="workspace-hero" data-surface="read-queue">'
                f"<h1>{escape(headline)}</h1>"
                f"<p>{escape(intro)}</p>"
                "</section>"
                + _filters_html(query, selected_type, selected_trust, selected_review_state)
                + (
                    _dense_results_html(
                        items,
                        query=query,
                        selected_type=selected_type,
                        selected_trust=selected_trust,
                        selected_review_state=selected_review_state,
                        selected_item=selected,
                    )
                    if dense_mode
                    else _operator_results_html(items)
                )
            )
        },
        "page_surface": "read-queue",
    }
