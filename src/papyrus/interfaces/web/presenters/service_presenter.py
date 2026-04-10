from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def _service_bucket(service: dict[str, Any]) -> str:
    status = str(service.get("status") or "").lower()
    criticality = str(service.get("service_criticality") or "").lower()
    linked_object_count = int(service.get("linked_object_count") or 0)
    if status != "active" or linked_object_count == 0:
        return "attention"
    if criticality in {"critical", "high"}:
        return "review"
    return "safe"


def _service_card_action_label(bucket: str) -> str:
    if bucket == "safe":
        return "Use service path"
    if bucket == "review":
        return "Review service path"
    return "Resolve service risk"


def _service_badges_html(components: ComponentPresenter, service: dict[str, Any]) -> str:
    return join_html(
        [
            components.badge(
                label="Criticality",
                value=service["service_criticality"],
                tone="warning" if service["service_criticality"] in {"high", "critical"} else "approved",
            ),
            components.badge(
                label="Status",
                value=service["status"],
                tone="approved" if service["status"] == "active" else "warning",
            ),
            components.badge(
                label="Linked guidance",
                value=service["linked_object_count"],
                tone="brand" if int(service["linked_object_count"] or 0) else "warning",
            ),
        ],
        " ",
    )


def _service_decision_card_html(components: ComponentPresenter, service: dict[str, Any]) -> str:
    bucket = _service_bucket(service)
    owner = service["owner"] or "Unassigned"
    team = service["team"] or "No team"
    summary = {
        "attention": "This service needs attention before operators rely on it as a starting point.",
        "review": "This service is usable, but the path still deserves review before it becomes the default choice.",
        "safe": "This service has linked guidance and is ready to use as an entry point.",
    }[bucket]
    return components.decision_card(
        title_html=link(service["service_name"], f"/services/{quoted_path(service['service_id'])}"),
        summary=summary,
        meta=[
            escape(service["service_id"]),
            f"Owner {escape(owner)} · {escape(team)}",
        ],
        badges=[_service_badges_html(components, service)],
        actions_html=link(
            _service_card_action_label(bucket),
            f"/services/{quoted_path(service['service_id'])}",
            css_class="button button-secondary",
            attrs={"data-component": "action-link", "data-action-id": "open-service-path"},
        ),
        tone=bucket,
        surface="services",
    )


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
        actions_html=link("Review service impact", f"/impact/service/{quoted_path(service['service_id'])}", css_class="button button-primary"),
    )
    overview_html = join_html(
        [
            components.section_card(
                title="When to use this service context",
                eyebrow="Services",
                body_html=join_html(
                    [
                        "<p>Use this service record to move from a service issue into the right guidance path.</p>",
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
                    f"<p><strong>Items needing review:</strong> {escape(detail['service_posture']['review_required_count'])}</p>"
                    f"<p><strong>Degraded items:</strong> {escape(detail['service_posture']['degraded_count'])}</p>"
                ),
            ),
        ]
    )
    linked_objects_html = components.section_card(
        title="Guidance path for this service",
        eyebrow="Read",
        body_html=components.queue_table(
            headers=["Guidance", "Status", "Relationship", "Do next"],
            rows=[
                [
                    components.decision_cell(
                        title_html=link(item["title"], f"/objects/{quoted_path(item['object_id'])}"),
                        meta=[escape(item["object_id"])],
                    ),
                    components.decision_cell(
                        title_html=escape(f"{item['trust_state']} / {item['revision_review_state'] or 'unknown'}"),
                        supporting_html=escape("Use this item when you need the service-specific operational answer."),
                    ),
                    components.decision_cell(
                        title_html=escape(item["relationship_type"]),
                    ),
                    link("Read guidance", f"/objects/{quoted_path(item['object_id'])}", css_class="button button-primary"),
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
        "page_header": {
            "headline": service["service_name"],
            "show_actor_banner": True,
            "show_actor_links": True,
        },
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
    grouped_services: dict[str, list[dict[str, Any]]] = {"safe": [], "review": [], "attention": []}
    for service in services:
        grouped_services[_service_bucket(service)].append(service)
    lead_service = next(
        (
            service
            for group_key in ("attention", "review", "safe")
            for service in grouped_services[group_key]
        ),
        None,
    )
    summary_html = components.trust_summary(
        title="Service decision view",
        badges=[
            components.badge(label="Requires attention", value=len(grouped_services["attention"]), tone="danger"),
            components.badge(label="Needs review", value=len(grouped_services["review"]), tone="warning"),
            components.badge(label="Safe", value=len(grouped_services["safe"]), tone="approved"),
        ],
        summary="Services are grouped by how safely they can guide the next operational decision.",
    )
    lead_html = (
        components.section_card(
            title="Service entry points",
            eyebrow="Services",
            tone="warning" if _service_bucket(lead_service) != "safe" else "approved",
            body_html=(
                f"<p>Start with {escape(lead_service['service_name'])} if you need the strongest next action on this screen.</p>"
                f"<p><strong>Why now:</strong> {escape('No linked guidance is attached yet.' if int(lead_service['linked_object_count'] or 0) == 0 else 'This service carries the highest current operational weight.')}</p>"
            ),
            footer_html=link(
                "Inspect service path",
                f"/services/{quoted_path(lead_service['service_id'])}",
                css_class="button button-primary",
            ),
        )
        if lead_service is not None
        else ""
    )
    group_config = {
        "attention": ("Requires attention", "These services need cleanup before they become safe entry points.", "danger"),
        "review": ("Needs review", "These services have guidance, but the path still needs operator judgment.", "warning"),
        "safe": ("Safe", "These services are ready to route operators into linked guidance.", "approved"),
    }
    group_sections = []
    for group_key in ("attention", "review", "safe"):
        group_items = grouped_services[group_key]
        if not group_items:
            continue
        title, description, tone = group_config[group_key]
        group_sections.append(
            components.section_card(
                title=title,
                eyebrow="Services",
                tone=tone,
                body_html=f'<p class="decision-group-summary">{escape(description)}</p>' + join_html(
                    [_service_decision_card_html(components, service) for service in group_items]
                ),
            )
        )
    services_html = join_html([summary_html, lead_html] + group_sections)
    return {
        "page_template": "pages/services.html",
        "page_title": "Services",
        "page_header": {
            "headline": "Services",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        "active_nav": "services",
        "aside_html": "",
        "page_context": {"services_html": services_html},
    }
