from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def present_object_impact(renderer: TemplateRenderer, *, impact: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    summary_html = components.section_card(
        title="Impact profile",
        eyebrow="Impact",
        body_html=(
            f"<p><strong>{escape(entity['title'])}</strong> affects inbound relationships, citation dependents, and related services.</p>"
        ),
        footer_html=link("Back to object", f"/objects/{quoted_path(entity['object_id'])}", css_class="button button-secondary"),
    )
    impacts_html = join_html(
        [
            components.relationships_panel(
                title="Impacted objects",
                items=[
                    f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}<span class=\"list-meta\">{escape(item['trust_state'])}</span>"
                    for item in impact["impacted_objects"]
                ],
                empty_label="No impacted objects were found.",
            ),
            components.relationships_panel(
                title="Inbound relationships",
                items=[
                    f"{escape(item['relationship_type'])}: {link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}"
                    for item in impact["inbound_relationships"]
                ],
                empty_label="No inbound relationships were found.",
            ),
            components.relationships_panel(
                title="Citation dependents",
                items=[
                    f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}<span class=\"list-meta\">{escape(item['citation_status'])}</span>"
                    for item in impact["citation_dependents"]
                ],
                empty_label="No citation dependents were found.",
            ),
            components.relationships_panel(
                title="Related services",
                items=[
                    link(item["service_name"], f"/services/{quoted_path(item['service_id'])}")
                    for item in impact["related_services"]
                ],
                empty_label="No related services were linked.",
            ),
        ]
    )
    return {
        "page_template": "pages/impact_object.html",
        "page_title": f"Impact {entity['title']}",
        "headline": f"Impact: {entity['title']}",
        "kicker": "Impact",
        "intro": "Affected objects, citation dependents, and services are separated so operators can trace blast radius quickly.",
        "active_nav": "manage",
        "aside_html": "",
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
    }


def present_service_impact(renderer: TemplateRenderer, *, impact: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    summary_html = components.section_card(
        title="Service impact profile",
        eyebrow="Impact",
        body_html=f"<p><strong>{escape(entity['service_name'])}</strong> impacts linked knowledge objects.</p>",
        footer_html=link("Back to service", f"/services/{quoted_path(entity['service_id'])}", css_class="button button-secondary"),
    )
    impacts_html = components.relationships_panel(
        title="Impacted objects",
        items=[
            f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}<span class=\"list-meta\">{escape(item['trust_state'])}</span>"
            for item in impact["impacted_objects"]
        ],
        empty_label="No impacted objects were linked.",
    )
    return {
        "page_template": "pages/impact_service.html",
        "page_title": f"Impact {entity['service_name']}",
        "headline": f"Impact: {entity['service_name']}",
        "kicker": "Impact",
        "intro": "Service impact keeps the affected knowledge set legible before any governed change is approved.",
        "active_nav": "manage",
        "aside_html": "",
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
    }
