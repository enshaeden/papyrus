from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import (
    impact_object_url,
    impact_service_url,
    object_url,
    service_url,
)
from papyrus.interfaces.web.view_helpers import (
    escape,
    join_html,
    link,
    render_definition_rows,
)


def render_impact_summary(
    *,
    components: ComponentPresenter,
    title: str,
    impacted_count: int,
    recent_events_count: int,
    surface: str,
    related_services_count: int | None = None,
) -> str:
    badges = [
        components.badge(label="Impacted", value=impacted_count, tone="warning"),
        components.badge(label="Recent events", value=recent_events_count, tone="brand"),
    ]
    if related_services_count is not None:
        badges.append(
            components.badge(label="Related services", value=related_services_count, tone="context")
        )
    return (
        f'<section class="impact-summary" data-component="impact-summary" data-surface="{escape(surface)}">'
        '<div class="impact-summary__header">'
        '<p class="impact-summary__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        "</div>"
        f'<div class="impact-summary__badges">{join_html(badges, " ")}</div>'
        "</section>"
    )


def render_impact_profile(
    *,
    title: str,
    rows: list[tuple[str, str]],
    footer_html: str,
    surface: str,
) -> str:
    return (
        f'<section class="impact-profile" data-component="impact-profile" data-surface="{escape(surface)}">'
        '<p class="impact-profile__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        f"{render_definition_rows([(label, escape(value)) for label, value in rows])}"
        f'<div class="impact-profile__footer">{footer_html}</div>'
        "</section>"
    )


def render_impact_event_log(
    *, title: str, events: list[dict[str, object]], empty_label: str, surface: str
) -> str:
    body_html = (
        join_html(
            [
                (
                    '<article class="impact-event-log__item">'
                    f"<p><strong>{escape(event['occurred_at'])}</strong> · {escape(event['event_type'])}</p>"
                    f"<p>{escape(event['actor'])} · {escape(event['source'])}</p>"
                    f"<p>{escape(str(event['payload'].get('summary') or event['payload'].get('reason') or 'No event summary.'))}</p>"
                    "</article>"
                )
                for event in events
            ]
        )
        if events
        else f'<p class="impact-event-log__empty">{escape(empty_label)}</p>'
    )
    return (
        f'<section class="impact-event-log" data-component="impact-event-log" data-surface="{escape(surface)}">'
        '<p class="impact-event-log__kicker">Audit</p>'
        f"<h2>{escape(title)}</h2>"
        f"{body_html}</section>"
    )


def render_impact_relationship_list(
    *,
    title: str,
    eyebrow: str,
    items_html: list[str],
    empty_label: str,
    surface: str,
) -> str:
    body_html = (
        '<div class="impact-relationship-list__items">'
        + join_html(
            [f'<div class="impact-relationship-list__item">{item}</div>' for item in items_html]
        )
        + "</div>"
        if items_html
        else f'<p class="impact-relationship-list__empty">{escape(empty_label)}</p>'
    )
    return (
        f'<section class="impact-relationship-list" data-component="impact-relationship-list" data-surface="{escape(surface)}">'
        f'<p class="impact-relationship-list__kicker">{escape(eyebrow)}</p>'
        f"<h2>{escape(title)}</h2>"
        f"{body_html}</section>"
    )


def render_impact_selected_item(*, item: dict[str, Any], role: str, surface: str) -> str:
    return (
        f'<section class="impact-selected-item" data-component="impact-selected-item" data-surface="{escape(surface)}">'
        '<p class="impact-selected-item__kicker">Selected item</p>'
        f"<h2>{escape(str(item['title']))}</h2>"
        + join_html(
            [
                f"<p><strong>{escape(item['reason'])}</strong></p>",
                f"<p><strong>Trust:</strong> {escape(item['trust_state'])}</p>",
                f"<p><strong>Changed:</strong> {escape(item['what_changed'])}</p>",
                f"<p><strong>Propagation path:</strong> {escape(' -> '.join(item['propagation_path']))}</p>",
                f"<p><strong>Revalidate:</strong> {escape(' | '.join(item['revalidate']))}</p>",
            ]
        )
        + f'<div class="impact-selected-item__footer">{link("Open guidance", object_url(str(item["object_id"])), css_class="button button-secondary")}</div>'
        + "</section>"
    )


def _impact_selection_href(base_path: str, *, object_id: str, revision_id: str = "") -> str:
    return (
        base_path
        + "?"
        + urlencode(
            {
                key: value
                for key, value in {
                    "selected_object_id": object_id,
                    "selected_revision_id": revision_id,
                }.items()
                if value
            }
        )
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
        is_selected = (
            selected_item is not None and str(selected_item.get("object_id") or "") == object_id
        )
        rows.append(
            f"<tr{' class="is-selected"' if is_selected else ''}>"
            f"<td>{components.decision_cell(title_html=link(str(item['title']), _impact_selection_href(base_path, object_id=object_id, revision_id=revision_id), css_class='selected-row-link'), supporting_html=escape(item['reason']), meta=[escape(item['trust_state'])])}</td>"
            f"<td>{components.decision_cell(title_html=escape(item['what_changed']), supporting_html=escape(' -> '.join(item['propagation_path'])))}</td>"
            f"<td>{components.decision_cell(title_html=escape(' | '.join(item['revalidate'])))}</td>"
            f"<td>{link('Open', object_url(object_id), css_class='button button-secondary')}</td>"
            "</tr>"
        )
    return (
        f'<section class="impact-trace" data-component="impact-trace" data-surface="{escape(surface)}">'
        '<p class="impact-trace__kicker">Impact</p>'
        f"<h2>{escape(title)}</h2>"
        '<table class="workbench-table" id="impact-trace-table">'
        "<thead><tr><th>Guidance</th><th>Changed through</th><th>Revalidate</th><th>Open</th></tr></thead>"
        "<tbody>" + join_html(rows) + "</tbody></table></section>"
    )


def _selected_item(
    items: list[dict[str, Any]],
    *,
    selected_object_id: str,
    selected_revision_id: str,
) -> dict[str, Any] | None:
    if not items:
        return None
    for item in items:
        object_id = str(item.get("object_id") or "")
        revision_id = str(item.get("revision_id") or "")
        if object_id == selected_object_id and (
            not selected_revision_id or revision_id == selected_revision_id
        ):
            return item
    return items[0]


def present_object_impact(
    renderer: TemplateRenderer,
    *,
    role: str,
    impact: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    current_impact = impact["current_impact"]
    selected_item = _selected_item(
        impact["impacted_objects"],
        selected_object_id=selected_object_id,
        selected_revision_id=selected_revision_id,
    )
    summary_html = render_impact_summary(
        components=components,
        title="Change impact",
        impacted_count=len(impact["impacted_objects"]),
        recent_events_count=len(impact["recent_events"]),
        related_services_count=len(impact["related_services"]),
        surface="impact-object",
    )
    impacts_html = render_impact_trace(
        components=components,
        role=role,
        title="Impacted guidance",
        items=impact["impacted_objects"],
        base_path=impact_object_url(str(entity["object_id"])),
        selected_item=selected_item,
        surface="impact-object",
        empty_label="No downstream knowledge objects were linked to this change.",
    )
    aside_html = join_html(
        [
            render_impact_profile(
                title="Impact profile",
                rows=[
                    ("Object", str(entity["title"])),
                    ("What changed", str(current_impact["what_changed"])),
                    ("Why impacted", str(current_impact["why_impacted"])),
                    ("Revalidate", " | ".join(current_impact["revalidate"])),
                ],
                footer_html=link(
                    "Return to guidance",
                    object_url(str(entity["object_id"])),
                    css_class="button button-primary",
                ),
                surface="impact-object",
            ),
            render_impact_selected_item(item=selected_item, role=role, surface="impact-object")
            if selected_item is not None
            else "",
            render_impact_event_log(
                title="Recent change events",
                events=impact["recent_events"],
                empty_label="No direct change events recorded for this object.",
                surface="impact-object",
            ),
            render_impact_relationship_list(
                title="Inbound relationships",
                eyebrow="Relationships",
                items_html=[
                    f"{escape(item['relationship_type'])}: {link(item['title'], object_url(str(item['object_id'])))}"
                    for item in impact["inbound_relationships"]
                ],
                empty_label="No inbound relationships were found.",
                surface="impact-object",
            ),
            render_impact_relationship_list(
                title="Citation dependents",
                eyebrow="Evidence",
                items_html=[
                    f'{link(item["title"], object_url(str(item["object_id"])))}<span class="list-meta">{escape(item["citation_status"])}</span>'
                    for item in impact["citation_dependents"]
                ],
                empty_label="No citation dependents were found.",
                surface="impact-object",
            ),
            render_impact_relationship_list(
                title="Related services",
                eyebrow="Relationships",
                items_html=[
                    link(item["service_name"], service_url(str(item["service_id"])))
                    for item in impact["related_services"]
                ],
                empty_label="No related services were linked.",
                surface="impact-object",
            ),
        ]
    )
    return {
        "page_template": "pages/impact_object.html",
        "page_title": f"Impact {entity['title']}",
        "page_header": {
            "headline": f"Change impact: {entity['title']}",
            "show_actor_links": True,
        },
        "active_nav": "oversight",
        "aside_html": aside_html,
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-object",
    }


def present_service_impact(
    renderer: TemplateRenderer,
    *,
    role: str,
    impact: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    current_impact = impact["current_impact"]
    selected_item = _selected_item(
        impact["impacted_objects"],
        selected_object_id=selected_object_id,
        selected_revision_id=selected_revision_id,
    )
    summary_html = render_impact_summary(
        components=components,
        title="Service impact",
        impacted_count=len(impact["impacted_objects"]),
        recent_events_count=len(impact["recent_events"]),
        surface="impact-service",
    )
    impacts_html = render_impact_trace(
        components=components,
        role=role,
        title="Impacted guidance",
        items=impact["impacted_objects"],
        base_path=impact_service_url(str(entity["service_id"])),
        selected_item=selected_item,
        surface="impact-service",
        empty_label="No downstream knowledge objects were linked to this service change.",
    )
    aside_html = join_html(
        [
            render_impact_profile(
                title="Service impact profile",
                rows=[
                    ("Service", str(entity["service_name"])),
                    ("What changed", str(current_impact["what_changed"])),
                    ("Why impacted", str(current_impact["why_impacted"])),
                    ("Revalidate", " | ".join(current_impact["revalidate"])),
                ],
                footer_html=link(
                    "Return to service",
                    service_url(str(entity["service_id"])),
                    css_class="button button-primary",
                ),
                surface="impact-service",
            ),
            render_impact_selected_item(item=selected_item, role=role, surface="impact-service")
            if selected_item is not None
            else "",
            render_impact_event_log(
                title="Recent change events",
                events=impact["recent_events"],
                empty_label="No direct change events recorded for this service.",
                surface="impact-service",
            ),
        ]
    )
    return {
        "page_template": "pages/impact_service.html",
        "page_title": f"Impact {entity['service_name']}",
        "page_header": {
            "headline": f"Change impact: {entity['service_name']}",
            "show_actor_links": True,
        },
        "active_nav": "oversight",
        "aside_html": aside_html,
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-service",
    }
