from __future__ import annotations

from typing import Any
from urllib.parse import urlencode

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path, render_definition_rows


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
        if object_id == selected_object_id and (not selected_revision_id or revision_id == selected_revision_id):
            return item
    return items[0]


def _impacted_objects_table(
    components: ComponentPresenter,
    *,
    items: list[dict[str, Any]],
    base_path: str,
    selected_item: dict[str, Any] | None,
    surface: str,
) -> str:
    rows: list[list[str]] = []
    row_attrs: list[dict[str, object]] = []
    for item in items:
        object_id = str(item["object_id"])
        revision_id = str(item.get("revision_id") or "")
        is_selected = selected_item is not None and str(selected_item.get("object_id") or "") == object_id
        rows.append(
            [
                components.decision_cell(
                    title_html=link(str(item["title"]), _impact_selection_href(base_path, object_id=object_id, revision_id=revision_id), css_class="selected-row-link"),
                    supporting_html=escape(item["reason"]),
                    meta=[escape(item["trust_state"])],
                ),
                components.decision_cell(
                    title_html=escape(item["what_changed"]),
                    supporting_html=escape(" -> ".join(item["propagation_path"])),
                ),
                components.decision_cell(
                    title_html=escape(" | ".join(item["revalidate"])),
                ),
                link("Open", f"/objects/{quoted_path(object_id)}", css_class="button button-secondary"),
            ]
        )
        row_attrs.append({"aria-selected": "true", "class": "is-selected"} if is_selected else {})
    return components.queue_table(
        headers=["Guidance", "Changed through", "Revalidate", "Open"],
        rows=rows,
        row_attrs=row_attrs,
        table_id=f"{surface}-impacted-objects",
        surface=surface,
        variant="dense-table",
    )


def _selected_item_panel(components: ComponentPresenter, item: dict[str, Any], *, surface: str) -> str:
    return components.context_panel(
        title=str(item["title"]),
        eyebrow="Selected item",
        body_html=join_html(
            [
                f"<p><strong>{escape(item['reason'])}</strong></p>",
                f"<p><strong>Trust:</strong> {escape(item['trust_state'])}</p>",
                f"<p><strong>Changed:</strong> {escape(item['what_changed'])}</p>",
                f"<p><strong>Propagation path:</strong> {escape(' -> '.join(item['propagation_path']))}</p>",
                f"<p><strong>Revalidate:</strong> {escape(' | '.join(item['revalidate']))}</p>",
            ]
        ),
        footer_html=link("Open guidance", f"/objects/{quoted_path(str(item['object_id']))}", css_class="button button-secondary"),
        variant="selected-item",
        surface=surface,
    )


def present_object_impact(
    renderer: TemplateRenderer,
    *,
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
    summary_html = components.summary_strip(
        title="Change consequences",
        badges=[
            components.badge(label="Impacted", value=len(impact["impacted_objects"]), tone="warning"),
            components.badge(label="Recent events", value=len(impact["recent_events"]), tone="brand"),
            components.badge(label="Related services", value=len(impact["related_services"]), tone="context"),
        ],
        summary="Use the selected row to inspect the most important downstream consequence.",
        surface="impact-object",
        variant="overview",
    )
    impacts_html = (
        _impacted_objects_table(
            components,
            items=impact["impacted_objects"],
            base_path=f"/impact/object/{quoted_path(entity['object_id'])}",
            selected_item=selected_item,
            surface="impact-object",
        )
        if impact["impacted_objects"]
        else components.empty_state(
            title="No impacted objects",
            description="No downstream knowledge objects were linked to this change.",
        )
    )
    aside_html = join_html(
        [
            components.context_panel(
                title="Impact profile",
                eyebrow="Impact",
                body_html=render_definition_rows(
                    [
                        ("Object", escape(entity["title"])),
                        ("What changed", escape(current_impact["what_changed"])),
                        ("Why impacted", escape(current_impact["why_impacted"])),
                        ("Revalidate", escape(" | ".join(current_impact["revalidate"]))),
                    ]
                ),
                footer_html=link("Return to guidance", f"/objects/{quoted_path(entity['object_id'])}", css_class="button button-primary"),
                variant="impact-profile",
                surface="impact-object",
            ),
            _selected_item_panel(components, selected_item, surface="impact-object") if selected_item is not None else "",
            components.context_panel(
                title="Recent change events",
                eyebrow="Audit",
                body_html=components.list_body(
                    items=[
                        (
                            f"{escape(event['occurred_at'])}: {escape(event['event_type'])}"
                            f"<span class=\"list-meta\">{escape(event['actor'])} · {escape(event['source'])}</span>"
                            f"<span class=\"list-meta\">{escape(str(event['payload'].get('summary') or event['payload'].get('reason') or 'No event summary.'))}</span>"
                        )
                        for event in impact["recent_events"]
                    ],
                    empty_label="No direct change events recorded for this object.",
                ),
                variant="recent-events",
                surface="impact-object",
            ),
            components.context_panel(
                title="Inbound relationships",
                eyebrow="Relationships",
                body_html=components.list_body(
                    items=[
                        f"{escape(item['relationship_type'])}: {link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}"
                        for item in impact["inbound_relationships"]
                    ],
                    empty_label="No inbound relationships were found.",
                ),
                variant="inbound-relationships",
                surface="impact-object",
            ),
            components.context_panel(
                title="Citation dependents",
                eyebrow="Evidence",
                body_html=components.list_body(
                    items=[
                        f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}<span class=\"list-meta\">{escape(item['citation_status'])}</span>"
                        for item in impact["citation_dependents"]
                    ],
                    empty_label="No citation dependents were found.",
                ),
                variant="citation-dependents",
                surface="impact-object",
            ),
            components.context_panel(
                title="Related services",
                eyebrow="Relationships",
                body_html=components.list_body(
                    items=[
                        link(item["service_name"], f"/services/{quoted_path(item['service_id'])}")
                        for item in impact["related_services"]
                    ],
                    empty_label="No related services were linked.",
                ),
                variant="related-services",
                surface="impact-object",
            ),
        ]
    )
    return {
        "page_template": "pages/impact_object.html",
        "page_title": f"Impact {entity['title']}",
        "page_header": {
            "headline": f"Change consequences: {entity['title']}",
            "show_actor_links": True,
        },
        "active_nav": "health",
        "aside_html": aside_html,
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-object",
    }


def present_service_impact(
    renderer: TemplateRenderer,
    *,
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
    summary_html = components.summary_strip(
        title="Service impact",
        badges=[
            components.badge(label="Impacted", value=len(impact["impacted_objects"]), tone="warning"),
            components.badge(label="Recent events", value=len(impact["recent_events"]), tone="brand"),
        ],
        summary="Track downstream knowledge before approving related change work.",
        surface="impact-service",
        variant="overview",
    )
    impacts_html = (
        _impacted_objects_table(
            components,
            items=impact["impacted_objects"],
            base_path=f"/impact/service/{quoted_path(entity['service_id'])}",
            selected_item=selected_item,
            surface="impact-service",
        )
        if impact["impacted_objects"]
        else components.empty_state(
            title="No impacted objects",
            description="No downstream knowledge objects were linked to this service change.",
        )
    )
    aside_html = join_html(
        [
            components.context_panel(
                title="Service impact profile",
                eyebrow="Impact",
                body_html=render_definition_rows(
                    [
                        ("Service", escape(entity["service_name"])),
                        ("What changed", escape(current_impact["what_changed"])),
                        ("Why impacted", escape(current_impact["why_impacted"])),
                        ("Revalidate", escape(" | ".join(current_impact["revalidate"]))),
                    ]
                ),
                footer_html=link("Return to service", f"/services/{quoted_path(entity['service_id'])}", css_class="button button-primary"),
                variant="impact-profile",
                surface="impact-service",
            ),
            _selected_item_panel(components, selected_item, surface="impact-service") if selected_item is not None else "",
            components.context_panel(
                title="Recent change events",
                eyebrow="Audit",
                body_html=components.list_body(
                    items=[
                        (
                            f"{escape(event['occurred_at'])}: {escape(event['event_type'])}"
                            f"<span class=\"list-meta\">{escape(event['actor'])} · {escape(event['source'])}</span>"
                            f"<span class=\"list-meta\">{escape(str(event['payload'].get('summary') or event['payload'].get('reason') or 'No event summary.'))}</span>"
                        )
                        for event in impact["recent_events"]
                    ],
                    empty_label="No direct change events recorded for this service.",
                ),
                variant="recent-events",
                surface="impact-service",
            ),
        ]
    )
    return {
        "page_template": "pages/impact_service.html",
        "page_title": f"Impact {entity['service_name']}",
        "page_header": {
            "headline": f"Change consequences: {entity['service_name']}",
            "show_actor_links": True,
        },
        "active_nav": "health",
        "aside_html": aside_html,
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-service",
    }
