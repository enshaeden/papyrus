from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def present_service_detail(renderer: TemplateRenderer, *, detail: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    service = detail["service"]
    header_html = components.object_header(
        object_type="service_record",
        object_id=service["service_id"],
        title=service["service_name"],
        summary=f"Criticality {service['service_criticality']} · owner {service['owner'] or 'unassigned'}",
        badges=[
            components.badge(label="Criticality", value=service["service_criticality"], tone="warning" if service["service_criticality"] in {"high", "critical"} else "approved"),
            components.badge(label="Status", value=service["status"], tone="approved" if service["status"] == "active" else "muted"),
            components.badge(label="Linked objects", value=len(detail["linked_objects"]), tone="pending"),
        ],
        actions_html=link("Impact view", f"/impact/service/{quoted_path(service['service_id'])}", css_class="button button-secondary"),
    )
    overview_html = join_html(
        [
            components.section_card(
                title="Operational profile",
                eyebrow="Service",
                body_html=join_html(
                    [
                        f"<p><strong>Owner:</strong> {escape(service['owner'] or 'None')}</p>",
                        f"<p><strong>Team:</strong> {escape(service['team'] or 'None')}</p>",
                        f"<p><strong>Support entrypoints:</strong> {escape(', '.join(service['support_entrypoints']) or 'None')}</p>",
                        f"<p><strong>Dependencies:</strong> {escape(', '.join(service['dependencies']) or 'None')}</p>",
                        f"<p><strong>Common failure modes:</strong> {escape(', '.join(service['common_failure_modes']) or 'None')}</p>",
                        f"<p><strong>Linked objects requiring attention:</strong> {escape(detail['service_posture']['degraded_count'])}</p>",
                    ]
                ),
            ),
            components.section_card(
                title="Canonical record",
                eyebrow="Source",
                body_html=(
                    link(detail["canonical_object"]["title"], f"/objects/{quoted_path(detail['canonical_object']['object_id'])}")
                    if detail["canonical_object"] is not None
                    else "<p class=\"empty-state-copy\">No canonical service record is linked.</p>"
                ),
            ),
        ]
    )
    linked_objects_html = components.section_card(
        title="Linked knowledge objects",
        eyebrow="Read",
        body_html=join_html(
            [
                f'<div class="linked-object-row">{link(item["title"], f"/objects/{quoted_path(item["object_id"])}")}<span class="list-meta">{escape(item["relationship_type"])} · trust {escape(item["trust_state"])} · approval {escape(item["approval_state"] or "unknown")}</span></div>'
                for item in detail["linked_objects"]
            ]
        ) or '<p class="empty-state-copy">No knowledge objects are linked to this service.</p>',
    )
    aside_html = join_html(
        [
            components.metadata_list(
                title="Service metadata",
                rows=[
                    ("Service ID", escape(service["service_id"])),
                    ("Status", escape(service["status"])),
                    ("Criticality", escape(service["service_criticality"])),
                    ("Owner", escape(service["owner"] or "None")),
                    ("Team", escape(service["team"] or "None")),
                ],
            )
        ]
    )
    return {
        "page_template": "pages/service_detail.html",
        "page_title": service["service_name"],
        "headline": service["service_name"],
        "kicker": "Services",
        "intro": "Service detail keeps criticality, support posture, dependencies, and linked knowledge visible in one operator view.",
        "active_nav": "services",
        "aside_html": aside_html,
        "page_context": {
            "header_html": header_html,
            "overview_html": overview_html,
            "linked_objects_html": linked_objects_html,
        },
    }


def present_service_catalog(renderer: TemplateRenderer, *, services: list[dict[str, Any]]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    rows = [
        [
            link(service["service_name"], f"/services/{quoted_path(service['service_id'])}"),
            escape(service["service_criticality"]),
            escape(service["status"]),
            escape(service["owner"] or "None"),
            escape(service["team"] or "None"),
            escape(service["linked_object_count"]),
        ]
        for service in services
    ]
    services_html = components.section_card(
        title="Service catalog",
        eyebrow="Services",
        body_html=components.queue_table(
            headers=["Service", "Criticality", "Status", "Owner", "Team", "Linked objects"],
            rows=rows,
            table_id="service-catalog",
        ),
    )
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "headline": "Services",
        "kicker": "Services",
        "intro": "Canonical service records and their linked operational knowledge stay close to the rest of the operator shell.",
        "active_nav": "services",
        "aside_html": components.validation_summary(
            title="Service cues",
            findings=[
                "Critical services should have an obvious canonical record.",
                "Linked object counts help spot thin documentation coverage.",
                "Ownership gaps surface quickly in the shared shell.",
            ],
        ),
        "page_context": {"services_html": services_html},
    }
