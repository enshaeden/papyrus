from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.impact_event_log_presenter import render_impact_event_log
from papyrus.interfaces.web.presenters.impact_profile_presenter import render_impact_profile
from papyrus.interfaces.web.presenters.impact_relationship_list_presenter import render_impact_relationship_list
from papyrus.interfaces.web.presenters.impact_selected_item_presenter import render_impact_selected_item
from papyrus.interfaces.web.presenters.impact_summary_presenter import render_impact_summary
from papyrus.interfaces.web.presenters.impact_trace_presenter import render_impact_trace
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import activity_url, impact_object_url, impact_service_url, object_url, service_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link


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
        title="Change consequences",
        summary="Use the selected row to inspect the most important downstream consequence.",
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
        base_path=impact_object_url(role, str(entity["object_id"])),
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
                footer_html=link("Return to guidance", object_url(role, str(entity["object_id"])), css_class="button button-primary"),
                surface="impact-object",
            ),
            render_impact_selected_item(item=selected_item, role=role, surface="impact-object") if selected_item is not None else "",
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
                    f"{escape(item['relationship_type'])}: {link(item['title'], object_url(role, str(item['object_id'])))}"
                    for item in impact["inbound_relationships"]
                ],
                empty_label="No inbound relationships were found.",
                surface="impact-object",
            ),
            render_impact_relationship_list(
                title="Citation dependents",
                eyebrow="Evidence",
                items_html=[
                    f"{link(item['title'], object_url(role, str(item['object_id'])))}<span class=\"list-meta\">{escape(item['citation_status'])}</span>"
                    for item in impact["citation_dependents"]
                ],
                empty_label="No citation dependents were found.",
                surface="impact-object",
            ),
            render_impact_relationship_list(
                title="Related services",
                eyebrow="Relationships",
                items_html=[
                    link(item["service_name"], service_url(role, str(item["service_id"])))
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
        summary="Track downstream knowledge before approving related change work.",
        impacted_count=len(impact["impacted_objects"]),
        recent_events_count=len(impact["recent_events"]),
        surface="impact-service",
    )
    impacts_html = render_impact_trace(
        components=components,
        role=role,
        title="Impacted guidance",
        items=impact["impacted_objects"],
        base_path=impact_service_url(role, str(entity["service_id"])),
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
                footer_html=link("Return to service", service_url(role, str(entity["service_id"])), css_class="button button-primary"),
                surface="impact-service",
            ),
            render_impact_selected_item(item=selected_item, role=role, surface="impact-service") if selected_item is not None else "",
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
            "headline": f"Change consequences: {entity['service_name']}",
            "show_actor_links": True,
        },
        "active_nav": "health",
        "aside_html": aside_html,
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-service",
    }
