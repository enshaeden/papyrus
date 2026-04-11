from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def present_object_impact(renderer: TemplateRenderer, *, impact: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    current_impact = impact["current_impact"]
    summary_html = components.surface_panel(
        title="Impact profile",
        eyebrow="Impact",
        body_html=(
            f"<p><strong>{escape(entity['title'])}</strong></p>"
            f"<p><strong>What changed:</strong> {escape(current_impact['what_changed'])}</p>"
            f"<p><strong>Why this is impacted:</strong> {escape(current_impact['why_impacted'])}</p>"
            f"<p><strong>What to revalidate:</strong> {escape(' | '.join(current_impact['revalidate']))}</p>"
        ),
        footer_html=link("Return to guidance", f"/objects/{quoted_path(entity['object_id'])}", css_class="button button-primary"),
        variant="impact-profile",
        surface="impact-object",
    )
    impacts_html = join_html(
        [
            components.surface_panel(
                title="Impacted objects",
                eyebrow="Relationships",
                body_html=components.list_body(
                    items=[
                        (
                            f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}"
                            f"<span class=\"list-meta\">{escape(item['trust_state'])} · {escape(item['reason'])}</span>"
                            f"<span class=\"list-meta\">changed: {escape(item['what_changed'])}</span>"
                            f"<span class=\"list-meta\">path: {escape(' -> '.join(item['propagation_path']))}</span>"
                            f"<span class=\"list-meta\">revalidate: {escape(' | '.join(item['revalidate']))}</span>"
                        )
                        for item in impact["impacted_objects"]
                    ],
                    empty_label="No impacted objects were found.",
                ),
                variant="impacted-objects",
                surface="impact-object",
            ),
            components.surface_panel(
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
                tone="context",
                variant="recent-events",
                surface="impact-object",
            ),
            components.surface_panel(
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
            components.surface_panel(
                title="Citation dependents",
                eyebrow="Evidence",
                body_html=components.list_body(
                    items=[
                        f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}<span class=\"list-meta\">{escape(item['citation_status'])}</span>"
                        for item in impact["citation_dependents"]
                    ],
                    empty_label="No citation dependents were found.",
                ),
                tone="context",
                variant="citation-dependents",
                surface="impact-object",
            ),
            components.surface_panel(
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
        "aside_html": "",
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-object",
    }


def present_service_impact(renderer: TemplateRenderer, *, impact: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    entity = impact["entity"]
    current_impact = impact["current_impact"]
    summary_html = components.surface_panel(
        title="Service impact profile",
        eyebrow="Impact",
        body_html=(
            f"<p><strong>{escape(entity['service_name'])}</strong></p>"
            f"<p><strong>What changed:</strong> {escape(current_impact['what_changed'])}</p>"
            f"<p><strong>Why this is impacted:</strong> {escape(current_impact['why_impacted'])}</p>"
            f"<p><strong>What to revalidate:</strong> {escape(' | '.join(current_impact['revalidate']))}</p>"
        ),
        footer_html=link("Return to service", f"/services/{quoted_path(entity['service_id'])}", css_class="button button-primary"),
        variant="impact-profile",
        surface="impact-service",
    )
    impacts_html = join_html(
        [
            components.surface_panel(
                title="Impacted objects",
                eyebrow="Relationships",
                body_html=components.list_body(
                    items=[
                        (
                            f"{link(item['title'], f'/objects/{quoted_path(item['object_id'])}')}"
                            f"<span class=\"list-meta\">{escape(item['trust_state'])} · {escape(item['reason'])}</span>"
                            f"<span class=\"list-meta\">changed: {escape(item['what_changed'])}</span>"
                            f"<span class=\"list-meta\">path: {escape(' -> '.join(item['propagation_path']))}</span>"
                            f"<span class=\"list-meta\">revalidate: {escape(' | '.join(item['revalidate']))}</span>"
                        )
                        for item in impact["impacted_objects"]
                    ],
                    empty_label="No impacted objects were linked.",
                ),
                variant="impacted-objects",
                surface="impact-service",
            ),
            components.surface_panel(
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
                tone="context",
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
        "aside_html": "",
        "page_context": {"summary_html": summary_html, "impacts_html": impacts_html},
        "page_surface": "impact-service",
    }
