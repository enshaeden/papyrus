from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def _service_status(service: dict[str, Any]) -> str:
    if service["status"] != "active":
        return "Degraded"
    if int(service.get("linked_object_count") or 0) == 0:
        return "Missing guidance path"
    if service["service_criticality"] in {"critical", "high"}:
        return "Critical service"
    return "Stable entry"


def present_service_catalog(renderer: TemplateRenderer, *, services: list[dict[str, Any]]) -> dict[str, Any]:
    del renderer
    map_html = (
        '<section class="service-map" data-component="service-map" data-surface="services">'
        '<div class="service-map-hero">'
        "<h1>Start from service context.</h1>"
        "<p>Services is an entry map: ownership, criticality, health, and linked guidance paths are visible before you open an article.</p>"
        "</div>"
        '<div class="service-map-grid">'
        + join_html(
            [
                (
                    '<article class="service-map-card">'
                    f'<p class="service-map-card-kicker">{escape(service["service_criticality"])} · {escape(service["status"])}</p>'
                    f'<h2>{link(service["service_name"], f"/services/{quoted_path(service["service_id"])}")}</h2>'
                    f'<p class="service-map-card-summary">{escape(_service_status(service))}</p>'
                    '<dl class="service-map-card-facts">'
                    f'<div><dt>Owner</dt><dd>{escape(service["owner"] or "Unassigned")}</dd></div>'
                    f'<div><dt>Team</dt><dd>{escape(service["team"] or "No team")}</dd></div>'
                    f'<div><dt>Linked guidance</dt><dd>{escape(service["linked_object_count"])}</dd></div>'
                    "</dl>"
                    '<div class="service-map-card-actions">'
                    f'{link("Open service path", f"/services/{quoted_path(service["service_id"])}", css_class="button button-primary", attrs={"data-action-id": "open-service-path"})}'
                    "</div></article>"
                )
                for service in services
            ]
        )
        + "</div></section>"
    )
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "page_header": {
            "headline": "Services",
            "intro": "Service entry map",
        },
        "active_nav": "services",
        "aside_html": "",
        "page_context": {"services_html": map_html},
        "page_surface": "services",
    }


def present_service_detail(renderer: TemplateRenderer, *, detail: dict[str, Any]) -> dict[str, Any]:
    del renderer
    service = detail["service"]
    linked_html = (
        '<section class="service-path" data-component="service-path" data-surface="services">'
        "<h2>Linked guidance path</h2>"
        '<div class="service-path-list">'
        + join_html(
            [
                (
                    '<article class="service-path-item">'
                    f'<p class="service-path-meta">{escape(item["relationship_type"])} · {escape(item["trust_state"])} · {escape(item["revision_review_state"] or "unknown")}</p>'
                    f'<h3>{link(item["title"], f"/objects/{quoted_path(item["object_id"])}")}</h3>'
                    f'<p>{escape(item["path"])}</p>'
                    f'{link("Read guidance", f"/objects/{quoted_path(item["object_id"])}", css_class="button button-ghost", attrs={"data-action-id": "open-primary-surface"})}'
                    "</article>"
                )
                for item in detail["linked_objects"]
            ]
        )
        + "</div></section>"
        if detail["linked_objects"]
        else '<section class="service-path-empty"><h2>Linked guidance path</h2><p>No guidance is linked to this service yet.</p></section>'
    )
    overview_html = (
        '<section class="service-detail-hero" data-component="service-detail-hero" data-surface="services">'
        f'<p class="service-detail-kicker">{escape(service["service_criticality"])} · {escape(service["status"])}</p>'
        f"<h1>{escape(service['service_name'])}</h1>"
        f'<p class="service-detail-summary">{escape(service["owner"] or "Unassigned")} · {escape(service["team"] or "No team")}</p>'
        '<dl class="service-detail-facts">'
        f'<div><dt>Support entrypoints</dt><dd>{escape(", ".join(service["support_entrypoints"]) or "None recorded")}</dd></div>'
        f'<div><dt>Dependencies</dt><dd>{escape(", ".join(service["dependencies"]) or "None recorded")}</dd></div>'
        f'<div><dt>Failure modes</dt><dd>{escape(", ".join(service["common_failure_modes"]) or "None recorded")}</dd></div>'
        "</dl>"
        '<div class="service-detail-actions">'
        f'{link("Review service impact", f"/impact/service/{quoted_path(service["service_id"])}", css_class="button button-primary")}'
        + (
            link("Open canonical record", f"/objects/{quoted_path(detail['canonical_object']['object_id'])}", css_class="button button-ghost")
            if detail["canonical_object"] is not None
            else ""
        )
        + "</div></section>"
    )
    pressure_html = (
        '<section class="service-pressure" data-component="service-pressure" data-surface="services">'
        "<h2>Service pressure</h2>"
        '<div class="service-pressure-grid">'
        f'<article><p class="service-pressure-metric">{escape(detail["service_posture"]["linked_object_count"])}</p><p>Linked guidance items</p></article>'
        f'<article><p class="service-pressure-metric">{escape(detail["service_posture"]["review_required_count"])}</p><p>Need review</p></article>'
        f'<article><p class="service-pressure-metric">{escape(detail["service_posture"]["degraded_count"])}</p><p>Degraded items</p></article>'
        "</div></section>"
    )
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
            "header_html": overview_html,
            "overview_html": pressure_html,
            "linked_objects_html": linked_html,
        },
        "page_surface": "services",
    }
