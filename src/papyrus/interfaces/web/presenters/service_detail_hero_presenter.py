from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.view_helpers import escape, link, quoted_path


def render_service_detail_hero(*, detail: dict[str, Any]) -> str:
    service = detail["service"]
    return (
        '<section class="service-detail-hero" data-component="service-detail-hero" data-surface="services">'
        f'<p class="service-detail-hero__kicker">{escape(service["service_criticality"])} · {escape(service["status"])}</p>'
        f"<h1>{escape(service['service_name'])}</h1>"
        f'<p class="service-detail-hero__summary">{escape(service["owner"] or "Unassigned")} · {escape(service["team"] or "No team")}</p>'
        '<dl class="service-detail-hero__facts">'
        f'<div><dt>Support entrypoints</dt><dd>{escape(", ".join(service["support_entrypoints"]) or "None recorded")}</dd></div>'
        f'<div><dt>Dependencies</dt><dd>{escape(", ".join(service["dependencies"]) or "None recorded")}</dd></div>'
        f'<div><dt>Failure modes</dt><dd>{escape(", ".join(service["common_failure_modes"]) or "None recorded")}</dd></div>'
        "</dl>"
        '<div class="service-detail-hero__actions">'
        f'{link("Review service impact", f"/impact/service/{quoted_path(service["service_id"])}", css_class="button button-primary")}'
        + (
            link("Open canonical record", f"/objects/{quoted_path(detail['canonical_object']['object_id'])}", css_class="button button-ghost")
            if detail["canonical_object"] is not None
            else ""
        )
        + "</div></section>"
    )
