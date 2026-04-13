from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.urls import service_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


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
                    f'<h2>{link(service["service_name"], service_url(role, str(service["service_id"])))}</h2>'
                    f'<p class="service-map__summary">{escape(service_status(service))}</p>'
                    '<dl class="service-map__facts">'
                    f'<div><dt>Owner</dt><dd>{escape(service["owner"] or "Unassigned")}</dd></div>'
                    f'<div><dt>Team</dt><dd>{escape(service["team"] or "No team")}</dd></div>'
                    f'<div><dt>Linked guidance</dt><dd>{escape(service["linked_object_count"])}</dd></div>'
                    "</dl>"
                    '<div class="service-map__actions">'
                    f'{link("Open service path", service_url(role, str(service["service_id"])), css_class="button button-primary", attrs={"data-action-id": "open-service-path"})}'
                    "</div></article>"
                )
                for service in services
            ]
        )
        + "</div></section>"
    )
