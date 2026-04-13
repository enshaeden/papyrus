from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.service_detail_hero_presenter import render_service_detail_hero
from papyrus.interfaces.web.presenters.service_map_presenter import render_service_map
from papyrus.interfaces.web.presenters.service_path_presenter import render_service_path
from papyrus.interfaces.web.presenters.service_pressure_presenter import render_service_pressure
from papyrus.interfaces.web.rendering import TemplateRenderer


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
    return {
        "page_template": "pages/service_detail.html",
        "page_title": service["service_name"],
        "page_header": {
            "headline": "Services",
            "intro": "Service context",
        },
        "active_nav": "services",
        "aside_html": "",
        "page_context": {
            "header_html": render_service_detail_hero(detail=detail, role=role),
            "overview_html": render_service_pressure(posture=detail["service_posture"]),
            "linked_objects_html": render_service_path(role=role, linked_objects=detail["linked_objects"]),
        },
        "page_surface": "services",
    }
