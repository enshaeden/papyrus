from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.application.blueprint_registry import (
    blueprint_label,
    is_primary_authoring_blueprint,
    list_primary_authoring_blueprints,
)
from papyrus.application.role_visibility import ADMIN_ROLE, READER_ROLE
from papyrus.interfaces.web.experience import experience_for_role
from papyrus.interfaces.web.presenters.governed_presenter import (
    primary_surface_href,
    projection_state,
    projection_use_guidance,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import search_url, service_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def queue_item_href(item: dict[str, Any], *, role: str) -> str:
    return primary_surface_href(
        role=role,
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip()
        or None,
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
    role: str,
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
    return (
        search_url(role) + "?" + urlencode({key: value for key, value in params.items() if value})
    )


def read_status_line(item: dict[str, Any], *, role: str) -> str:
    state = projection_state(item.get("ui_projection"))
    tokens = [str(item.get("object_type") or "").replace("_", " ")]
    if role == READER_ROLE:
        return " · ".join(entry for entry in tokens if entry)
    review_state = str(
        state.get("revision_review_state") or item.get("revision_review_state") or "unknown"
    )
    trust_state = str(state.get("trust_state") or item.get("trust_state") or "unknown")
    if review_state != "approved":
        tokens.append(review_state)
    if trust_state not in {"trusted", "approved"}:
        tokens.append(trust_state)
    return " · ".join(entry for entry in tokens if entry)


def linked_services_text(item: dict[str, Any]) -> str:
    linked_services = item.get("linked_services") or []
    if not linked_services:
        return "No linked service context."
    return ", ".join(str(service["service_name"]) for service in linked_services)


def render_read_filter_bar(
    *, role: str, query: str, selected_type: str, selected_trust: str, selected_review_state: str
) -> str:
    type_options = [
        f'<option value="{escape(blueprint.blueprint_id)}"{" selected" if selected_type == blueprint.blueprint_id else ""}>'
        f"{escape(blueprint.display_name)}</option>"
        for blueprint in list_primary_authoring_blueprints()
    ]
    if selected_type:
        try:
            if not is_primary_authoring_blueprint(selected_type):
                type_options.append(
                    f'<option value="{escape(selected_type)}" selected>'
                    f"{escape(blueprint_label(selected_type, include_scope_note=True))}</option>"
                )
        except ValueError:
            pass
    return (
        f'<form class="read-filter-bar" method="get" action="{escape(search_url(role))}" data-component="read-filter-bar" data-surface="read-queue">'
        + '<div class="read-filter-bar__search">'
        + f'<input type="search" name="query" placeholder="Search by title, path, service, or summary" value="{escape(query)}" />'
        + '<button class="button button-primary" type="submit">Search</button>'
        + "</div>"
        + '<div class="read-filter-bar__row">'
        + '<label><span>Type</span><select name="object_type">'
        + f'<option value=""{" selected" if not selected_type else ""}>All</option>'
        + "".join(type_options)
        + "</select></label>"
        + '<label><span>Trust</span><select name="trust">'
        + f'<option value=""{" selected" if not selected_trust else ""}>Any</option>'
        + f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        + f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        + f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        + f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        + "</select></label>"
        + '<label><span>Review</span><select name="review_state">'
        + f'<option value=""{" selected" if not selected_review_state else ""}>Any</option>'
        + f'<option value="approved"{" selected" if selected_review_state == "approved" else ""}>Approved</option>'
        + f'<option value="in_review"{" selected" if selected_review_state == "in_review" else ""}>In review</option>'
        + f'<option value="draft"{" selected" if selected_review_state == "draft" else ""}>Draft</option>'
        + f'<option value="rejected"{" selected" if selected_review_state == "rejected" else ""}>Rejected</option>'
        + "</select></label>"
        + "</div></form>"
    )


def render_read_result_cards(*, role: str, items: list[dict[str, Any]]) -> str:
    if not items:
        return '<section class="read-results-empty"><h2>No matching guidance</h2><p>Adjust the search or widen the filters.</p></section>'
    return join_html(
        [
            (
                '<article class="read-result-card" data-component="read-result-card" data-surface="read-queue">'
                '<div class="read-result-card__copy">'
                f'<p class="read-result-card__meta">{escape(read_status_line(item, role=role))}</p>'
                f"<h2>{link(item['title'], queue_item_href(item, role=role))}</h2>"
                f'<p class="read-result-card__summary">{escape(item.get("summary") or "No summary recorded.")}</p>'
                f'<p class="read-result-card__guidance">{escape(str(projection_use_guidance(item.get("ui_projection")).get("summary") or "Open the article for the full procedure."))}</p>'
                f'<p class="read-result-card__support">{escape(linked_services_text(item))}</p>'
                "</div>"
                '<div class="read-result-card__actions">'
                f"{link('Open article', queue_item_href(item, role=role), css_class='button button-primary', attrs={'data-action-id': 'open-primary-surface'})}"
                + (
                    f"{link('Open service', service_url(role, str(item['linked_services'][0]['service_id'])), css_class='button button-ghost')}"
                    if item.get("linked_services") and role != READER_ROLE
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
    role: str,
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
            and str(
                selected_item.get("revision_id") or selected_item.get("current_revision_id") or ""
            )
            == revision_id
        )
        rows.append(
            f"<tr{' class="is-selected"' if is_selected else ''}>"
            f'<td><a class="selected-row-link" href="{escape(selection_href(query=query, selected_type=selected_type, selected_trust=selected_trust, selected_review_state=selected_review_state, object_id=object_id, revision_id=revision_id, role=role))}">{escape(item["title"])}</a><span class="table-support">{escape(item.get("summary") or "")}</span></td>'
            f"<td>{escape(read_status_line(item, role=role))}</td>"
            f"<td>{escape(str(projection_use_guidance(item.get('ui_projection')).get('next_action') or 'Inspect article'))}</td>"
            f"<td>{escape(linked_services_text(item))}</td>"
            f"<td>{link('Open', queue_item_href(item, role=role), css_class='button button-ghost', attrs={'data-action-id': 'open-primary-surface'})}</td>"
            "</tr>"
        )
    return (
        '<section class="read-results-table" data-component="read-results-table" data-surface="read-queue">'
        '<table class="workbench-table" id="read-queue-results">'
        "<thead><tr><th>Guidance</th><th>Status</th><th>Next action</th><th>Service</th><th>Open</th></tr></thead>"
        "<tbody>" + join_html(rows) + "</tbody></table></section>"
    )


def render_read_selected_context(*, role: str, item: dict[str, Any] | None) -> str:
    if item is None:
        return ""
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return (
        '<section class="read-selected-context" data-component="read-selected-context" data-surface="read-queue">'
        '<p class="read-selected-context__kicker">Selected context</p>'
        f"<h2>{escape(item['title'])}</h2>"
        f"<p>{escape(str(use_guidance.get('summary') or item.get('summary') or 'No summary recorded.'))}</p>"
        f'<dl class="read-selected-context__facts"><div><dt>Status</dt><dd>{escape(read_status_line(item, role=role))}</dd></div><div><dt>Owner</dt><dd>{escape(item.get("owner") or "Unowned")}</dd></div><div><dt>Path</dt><dd>{escape(item.get("path") or "")}</dd></div><div><dt>Services</dt><dd>{escape(linked_services_text(item))}</dd></div></dl>'
        f'<p class="read-selected-context__next"><strong>Next:</strong> {escape(str(use_guidance.get("next_action") or "Inspect the article."))}</p>'
        f"{link('Open article', queue_item_href(item, role=role), css_class='button button-primary', attrs={'data-action-id': 'open-primary-surface'})}"
        "</section>"
    )


def _selected_item(
    items: list[dict[str, Any]], *, selected_object_id: str, selected_revision_id: str
) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or item.get("current_revision_id") or "")
        if object_id == selected_object_id and (
            not selected_revision_id or revision_id == selected_revision_id
        ):
            return item
    return items[0]


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_review_state: str,
    role: str,
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer
    experience = experience_for_role(role)
    behavior = experience.page_behavior("read-queue")
    selected = _selected_item(
        items, selected_object_id=selected_object_id, selected_revision_id=selected_revision_id
    )
    dense_mode = bool(behavior and behavior.show_context_rail)
    if role == READER_ROLE:
        intro = "Reader surfaces stay content-first so you can open dependable guidance without governance-heavy framing."
        page_title = "Read"
        header_headline = "Read"
        active_nav = "read"
    elif role == ADMIN_ROLE:
        intro = "Admin content stays dense so oversight, service impact, and next action remain in scan range."
        page_title = "Content"
        header_headline = "Inspect"
        active_nav = "inspect"
    else:
        intro = "Operators start from the article, then pull governance context forward only when the current task needs a decision."
        page_title = "Read"
        header_headline = "Read"
        active_nav = "read"
    return {
        "page_template": "pages/queue.html",
        "page_title": page_title,
        "page_header": {
            "headline": header_headline,
            "kicker": experience.label,
            "intro": intro,
        },
        "active_nav": active_nav,
        "aside_html": render_read_selected_context(role=role, item=selected) if dense_mode else "",
        "page_context": {
            "workspace_html": join_html(
                [
                    render_read_filter_bar(
                        role=role,
                        query=query,
                        selected_type=selected_type,
                        selected_trust=selected_trust,
                        selected_review_state=selected_review_state,
                    ),
                    (
                        render_read_results_table(
                            items=items,
                            query=query,
                            selected_type=selected_type,
                            selected_trust=selected_trust,
                            selected_review_state=selected_review_state,
                            selected_item=selected,
                            role=role,
                        )
                        if dense_mode
                        else render_read_result_cards(role=role, items=items)
                    ),
                ]
            )
        },
        "page_surface": "read-queue",
    }
