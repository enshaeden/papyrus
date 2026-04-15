from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import impact_service_url, object_url, service_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link, render_definition_rows


def service_status(service: dict[str, Any]) -> str:
    if service["status"] != "active":
        return "Degraded"
    if int(service.get("linked_object_count") or 0) == 0:
        return "Missing guidance path"
    if service["service_criticality"] in {"critical", "high"}:
        return "Critical service"
    return "Stable entry"


def render_service_map(*, role: str, services: list[dict[str, Any]]) -> str:
    return (
        '<section class="service-map" data-component="service-map" data-surface="services">'
        '<div class="service-map__grid">'
        + join_html(
            [
                (
                    '<article class="service-map__card" data-component="service-map-card" data-surface="services">'
                    f'<p class="service-map__kicker">{escape(service["service_criticality"])} · {escape(service["status"])}</p>'
                    f"<h2>{link(service['service_name'], service_url(role, str(service['service_id'])))}</h2>"
                    f'<p class="service-map__summary">{escape(service_status(service))}</p>'
                    '<dl class="service-map__facts">'
                    f"<div><dt>Owner</dt><dd>{escape(service['owner'] or 'Unassigned')}</dd></div>"
                    f"<div><dt>Team</dt><dd>{escape(service['team'] or 'No team')}</dd></div>"
                    f"<div><dt>Linked guidance</dt><dd>{escape(service['linked_object_count'])}</dd></div>"
                    "</dl>"
                    '<div class="service-map__actions">'
                    f"{link('Open service path', service_url(role, str(service['service_id'])), css_class='button button-primary', attrs={'data-action-id': 'open-service-path'})}"
                    "</div></article>"
                )
                for service in services
            ]
        )
        + "</div></section>"
    )


def render_service_pressure(*, posture: dict[str, object]) -> str:
    return (
        '<section class="service-pressure" data-component="service-pressure" data-surface="services">'
        '<p class="service-pressure__kicker">Service posture</p>'
        "<h2>Service pressure</h2>"
        '<div class="service-pressure__grid">'
        f'<article><p class="service-pressure__metric">{escape(posture["linked_object_count"])}</p><p>Linked guidance items</p></article>'
        f'<article><p class="service-pressure__metric">{escape(posture["review_required_count"])}</p><p>Need review</p></article>'
        f'<article><p class="service-pressure__metric">{escape(posture["degraded_count"])}</p><p>Degraded items</p></article>'
        "</div></section>"
    )


def render_service_path(*, role: str, linked_objects: list[dict[str, Any]]) -> str:
    if not linked_objects:
        return '<section class="service-path-empty" data-component="service-path-empty" data-surface="services"><h2>Linked guidance path</h2><p>No guidance is linked to this service yet.</p></section>'
    return (
        '<section class="service-path" data-component="service-path" data-surface="services">'
        '<p class="service-path__kicker">Guidance path</p>'
        "<h2>Linked guidance path</h2>"
        '<div class="service-path__list">'
        + join_html(
            [
                (
                    '<article class="service-path__item" data-component="service-path-item" data-surface="services">'
                    f'<p class="service-path__meta">{escape(item["relationship_type"])} · {escape(item["trust_state"])} · {escape(item["revision_review_state"] or "unknown")}</p>'
                    f"<h3>{link(item['title'], object_url(role, str(item['object_id'])))}</h3>"
                    f"<p>{escape(item['path'])}</p>"
                    f"{link('Open content', object_url(role, str(item['object_id'])), css_class='button button-ghost', attrs={'data-action-id': 'open-primary-surface'})}"
                    "</article>"
                )
                for item in linked_objects
            ]
        )
        + "</div></section>"
    )


def present_service_catalog(
    renderer: TemplateRenderer, *, services: list[dict[str, Any]], role: str
) -> dict[str, Any]:
    del renderer
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "page_header": {"headline": "Services"},
        "active_nav": "services",
        "aside_html": "",
        "page_context": {"services_html": render_service_map(role=role, services=services)},
        "page_surface": "services",
    }


def present_service_detail(
    renderer: TemplateRenderer, *, detail: dict[str, Any], role: str
) -> dict[str, Any]:
    del renderer
    service = detail["service"]
    actions = [
        link(
            "Review service impact",
            impact_service_url(role, str(service["service_id"])),
            css_class="button button-primary",
        ),
    ]
    if detail["canonical_object"] is not None:
        actions.append(
            link(
                "Open canonical record",
                object_url(role, str(detail["canonical_object"]["object_id"])),
                css_class="button button-ghost",
            )
        )
    return {
        "page_template": "pages/service_detail.html",
        "page_title": service["service_name"],
        "page_header": {
            "headline": service["service_name"],
            "kicker": f"{service['service_criticality']} · {service['status']}",
            "detail_html": (
                '<dl class="metadata-list">'
                + render_definition_rows(
                    [
                        (
                            "Support entrypoints",
                            escape(", ".join(service["support_entrypoints"]) or "None recorded"),
                        ),
                        (
                            "Dependencies",
                            escape(", ".join(service["dependencies"]) or "None recorded"),
                        ),
                        (
                            "Failure modes",
                            escape(", ".join(service["common_failure_modes"]) or "None recorded"),
                        ),
                    ]
                )
                + "</dl>"
            ),
            "actions_html": join_html(actions),
        },
        "active_nav": "services",
        "aside_html": "",
        "page_context": {
            "overview_html": render_service_pressure(posture=detail["service_posture"]),
            "linked_objects_html": render_service_path(
                role=role, linked_objects=detail["linked_objects"]
            ),
        },
        "page_surface": "services",
    }
