from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.service_map_presenter import render_service_map
from papyrus.interfaces.web.presenters.service_path_presenter import render_service_path
from papyrus.interfaces.web.presenters.service_pressure_presenter import render_service_pressure
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import impact_service_url, object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link, render_definition_rows


def present_service_catalog(renderer: TemplateRenderer, *, services: list[dict[str, Any]], role: str) -> dict[str, Any]:
    del renderer
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "page_header": {
            "headline": "Services",
            "intro": "Service entry map",
        },
        "active_nav": "services",
        "aside_html": "",
        "page_context": {"services_html": render_service_map(role=role, services=services)},
        "page_surface": "services",
    }


def present_service_detail(renderer: TemplateRenderer, *, detail: dict[str, Any], role: str) -> dict[str, Any]:
    del renderer
    service = detail["service"]
    actions = [
        link("Review service impact", impact_service_url(role, str(service["service_id"])), css_class="button button-primary"),
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
            "kicker": f'{service["service_criticality"]} · {service["status"]}',
            "intro": f'{service["owner"] or "Unassigned"} · {service["team"] or "No team"}',
            "detail_html": (
                '<dl class="metadata-list">'
                + render_definition_rows(
                    [
                        ("Support entrypoints", escape(", ".join(service["support_entrypoints"]) or "None recorded")),
                        ("Dependencies", escape(", ".join(service["dependencies"]) or "None recorded")),
                        ("Failure modes", escape(", ".join(service["common_failure_modes"]) or "None recorded")),
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
            "linked_objects_html": render_service_path(role=role, linked_objects=detail["linked_objects"]),
        },
        "page_surface": "services",
    }
