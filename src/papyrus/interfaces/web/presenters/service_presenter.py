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
            components.badge(label="Linked objects", value=len(detail["linked_objects"]), tone="brand"),
        ],
        actions_html=link("Impact view", f"/impact/service/{quoted_path(service['service_id'])}", css_class="button button-secondary"),
    )
    overview_html = join_html(
        [
            components.section_card(
                title="When to use this service context",
                eyebrow="Services",
                body_html=join_html(
                    [
                        "<p>Open this service view when you need the canonical service record, the linked operational guidance path, or the service-level blast radius before acting.</p>",
                        f"<p><strong>Support entrypoints:</strong> {escape(', '.join(service['support_entrypoints']) or 'None')}</p>",
                        f"<p><strong>Dependencies:</strong> {escape(', '.join(service['dependencies']) or 'None')}</p>",
                        f"<p><strong>Common failure modes:</strong> {escape(', '.join(service['common_failure_modes']) or 'None')}</p>",
                    ]
                ),
            ),
            components.section_card(
                title="Start with the canonical record",
                eyebrow="Services",
                body_html=(
                    link(detail["canonical_object"]["title"], f"/objects/{quoted_path(detail['canonical_object']['object_id'])}")
                    if detail["canonical_object"] is not None
                    else "<p class=\"empty-state-copy\">No canonical service record is linked.</p>"
                ),
            ),
            components.section_card(
                title="What needs attention",
                eyebrow="Services",
                body_html=(
                    f"<p><strong>Linked guidance:</strong> {escape(detail['service_posture']['linked_object_count'])}</p>"
                    f"<p><strong>Non-approved items:</strong> {escape(detail['service_posture']['non_approved_count'])}</p>"
                    f"<p><strong>Degraded items:</strong> {escape(detail['service_posture']['degraded_count'])}</p>"
                ),
            ),
        ]
    )
    linked_objects_html = components.section_card(
        title="Guidance path for this service",
        eyebrow="Read",
        body_html=components.queue_table(
            headers=["Guidance", "When to open it", "Safe now?", "Relationship"],
            rows=[
                [
                    link(item["title"], f"/objects/{quoted_path(item['object_id'])}"),
                    escape("Use this item when you need the service-specific operational answer."),
                    escape(f"{item['trust_state']} / {item['approval_state'] or 'unknown'}"),
                    escape(item["relationship_type"]),
                ]
                for item in detail["linked_objects"]
            ],
            table_id="service-guidance-path",
        ) if detail["linked_objects"] else '<p class="empty-state-copy">No knowledge objects are linked to this service.</p>',
    )
    aside_html = join_html(
        [
            components.metadata_list(
                title="Service reference",
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
        "intro": "Move from a service issue into the right operational guidance path with service context, dependencies, and linked knowledge kept together.",
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
        title="Service entry points",
        eyebrow="Services",
        body_html=components.queue_table(
            headers=["Service", "Criticality", "Status", "Owner", "Team", "Linked guidance"],
            rows=rows,
            table_id="service-catalog",
        ),
    )
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "headline": "Services",
        "kicker": "Services",
        "intro": "Use services as an operational starting point when the incident, request, or review begins with service context instead of a known document.",
        "active_nav": "services",
        "aside_html": components.validation_summary(
            title="How to use services",
            findings=[
                "Open the service first when the problem is clearly service-scoped.",
                "Linked guidance counts help spot thin or missing knowledge coverage.",
                "Use the service path to move into the right runbook, known error, or service record.",
            ],
        ),
        "page_context": {"services_html": services_html},
    }
