from __future__ import annotations

import re
from typing import Any

from papyrus.application.authoring_flow import derive_section_content
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    projection_state,
    render_governed_action_panel,
    render_projection_status_panel,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import (
    escape,
    format_timestamp,
    join_html,
    link,
    quoted_path,
    render_list,
    tone_for_approval,
    tone_for_health,
    tone_for_trust,
)


SECTION_PATTERN = re.compile(r"^## (?P<title>.+?)\n\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def _body_sections(body_markdown: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in SECTION_PATTERN.finditer(str(body_markdown or "").strip())
    }


def _runbook_guidance(components: ComponentPresenter, metadata: dict[str, Any], sections: dict[str, str]) -> list[str]:
    return [
        components.section_card(
            title="When to use this",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Use When') or 'No trigger guidance recorded.')}</p>",
        ),
        components.section_card(
            title="Preconditions",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("prerequisites", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No prerequisites recorded.</p>',
        ),
        components.section_card(
            title="Verification",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("verification", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No verification steps recorded.</p>',
        ),
        components.section_card(
            title="If this fails / next escalation",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Boundaries And Escalation') or 'No escalation boundary recorded.')}</p>",
        ),
    ]


def _known_error_guidance(components: ComponentPresenter, metadata: dict[str, Any], sections: dict[str, str]) -> list[str]:
    return [
        components.section_card(
            title="When this applies",
            eyebrow="Guidance",
            body_html=(
                f"<p><strong>Symptoms:</strong> {escape(', '.join(metadata.get('symptoms', [])) or 'None recorded.')}</p>"
                f"<p><strong>Scope:</strong> {escape(metadata.get('scope') or 'None recorded.')}</p>"
            ),
        ),
        components.section_card(
            title="Diagnostic checks",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("diagnostic_checks", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No diagnostic checks recorded.</p>',
        ),
        components.section_card(
            title="Mitigations",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("mitigations", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No mitigations recorded.</p>',
        ),
        components.section_card(
            title="If this fails / next escalation",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Escalation Threshold') or 'No escalation threshold recorded.')}</p>",
        ),
    ]


def _service_record_guidance(components: ComponentPresenter, metadata: dict[str, Any], sections: dict[str, str]) -> list[str]:
    return [
        components.section_card(
            title="Operational scope",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Scope') or 'No scope notes recorded.')}</p>",
        ),
        components.section_card(
            title="Dependencies",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("dependencies", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No dependencies recorded.</p>',
        ),
        components.section_card(
            title="Support entrypoints",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("support_entrypoints", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No support entrypoints recorded.</p>',
        ),
        components.section_card(
            title="If this fails / next escalation",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Operational Notes') or 'No operational notes recorded.')}</p>",
        ),
    ]


def _policy_guidance(components: ComponentPresenter, metadata: dict[str, Any], sections: dict[str, str]) -> list[str]:
    return [
        components.section_card(
            title="Policy scope",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Policy Scope') or metadata.get('policy_scope') or 'No policy scope recorded.')}</p>",
        ),
        components.section_card(
            title="Controls",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("controls", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No controls recorded.</p>',
        ),
        components.section_card(
            title="Exceptions",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Exceptions') or metadata.get('exceptions') or 'No exceptions recorded.')}</p>",
        ),
    ]


def _system_design_guidance(components: ComponentPresenter, metadata: dict[str, Any], sections: dict[str, str]) -> list[str]:
    return [
        components.section_card(
            title="Architecture",
            eyebrow="Guidance",
            body_html=f"<p>{escape(sections.get('Architecture') or metadata.get('architecture') or 'No architecture recorded.')}</p>",
        ),
        components.section_card(
            title="Interfaces",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("interfaces", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No interfaces recorded.</p>',
        ),
        components.section_card(
            title="Dependencies",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("dependencies", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No dependencies recorded.</p>',
        ),
        components.section_card(
            title="Failure modes",
            eyebrow="Guidance",
            body_html=render_list([escape(item) for item in metadata.get("common_failure_modes", [])], css_class="panel-list")
            or '<p class="empty-state-copy">No failure modes recorded.</p>',
        ),
    ]


def _guidance_cards(
    components: ComponentPresenter,
    *,
    item: dict[str, Any],
    metadata: dict[str, Any],
    sections: dict[str, str],
) -> list[str]:
    object_type = str(item["object_type"])
    if object_type == "runbook":
        return _runbook_guidance(components, metadata, sections)
    if object_type == "known_error":
        return _known_error_guidance(components, metadata, sections)
    if object_type == "service_record":
        return _service_record_guidance(components, metadata, sections)
    if object_type == "policy":
        return _policy_guidance(components, metadata, sections)
    if object_type == "system_design":
        return _system_design_guidance(components, metadata, sections)
    return []


def present_object_detail(renderer: TemplateRenderer, *, detail: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    item = detail["object"]
    revision = detail["current_revision"]
    metadata = detail.get("metadata") or {}
    ui_projection = detail.get("ui_projection") or {}
    projection_state_values = projection_state(ui_projection)
    evidence_status = detail.get("evidence_status") or {}
    body_sections = _body_sections(revision["body_markdown"] if revision is not None else "")
    if revision is not None and not revision.get("section_content"):
        revision["section_content"] = derive_section_content(
            blueprint_id=str(revision.get("blueprint_id") or item["object_type"]),
            metadata=metadata,
            body_markdown=str(revision["body_markdown"]),
        )
    latest_audit = detail["audit_events"][0] if detail["audit_events"] else None

    header_html = components.object_header(
        object_type=item["object_type"],
        object_id=item["object_id"],
        title=item["title"],
        summary=item["summary"],
        badges=[
            components.badge(
                label="Trust",
                value=projection_state_values.get("trust_state") or "unknown",
                tone=tone_for_trust(str(projection_state_values.get("trust_state") or "unknown")),
            ),
            components.badge(
                label="Approval",
                value=projection_state_values.get("approval_state") or "unknown",
                tone=tone_for_approval(str(projection_state_values.get("approval_state") or "unknown")),
            ),
            components.badge(label="Freshness", value=item["freshness_rank"], tone=tone_for_health(item["freshness_rank"])),
            components.badge(label="Evidence", value=item["citation_health_rank"], tone=tone_for_health(item["citation_health_rank"])),
        ],
        actions_html=join_html(
            [
                link("Revision history", f"/objects/{quoted_path(item['object_id'])}/revisions", css_class="button button-secondary"),
                link("Revise guidance", f"/write/objects/{quoted_path(item['object_id'])}/revisions/new", css_class="button button-primary"),
                link("Impact view", f"/impact/object/{quoted_path(item['object_id'])}", css_class="button button-secondary"),
            ],
            " ",
        ),
    )

    top_cards = [
        render_projection_status_panel(
            components,
            title="Current governed posture",
            ui_projection=ui_projection,
            footer_html=(
                f'<p class="section-footer">Last reviewed {escape(item["last_reviewed"])} · cadence {escape(item["review_cadence"])}</p>'
            ),
        ),
        render_governed_action_panel(
            components,
            title="Governed actions",
            ui_projection=ui_projection,
            object_id=str(item["object_id"]),
            revision_id=str(revision["revision_id"]) if revision is not None else None,
        ),
        components.section_card(
            title="Linked service context",
            eyebrow="Use",
            body_html=(
                render_list(
                    [
                        f"{link(service['service_name'], f'/services/{quoted_path(service['service_id'])}')}"
                        f'<span class="list-meta">{escape(service["service_criticality"])} · {escape(service["status"])}</span>'
                        for service in detail["related_services"]
                    ],
                    css_class="panel-list",
                )
                or '<p class="empty-state-copy">No linked service context is recorded.</p>'
            ),
        ),
        components.section_card(
            title="What changed recently",
            eyebrow="Change",
            body_html=(
                f"<p>{escape(revision['change_summary'] or 'No revision change summary recorded.')}</p>"
                + (
                    f"<p><strong>Latest audit:</strong> {escape(latest_audit['event_type'])} at {escape(format_timestamp(latest_audit['occurred_at']))} by {escape(latest_audit['actor'])}</p>"
                    if latest_audit
                    else "<p>No recent audit activity is recorded.</p>"
                )
            ),
        ),
    ]

    guidance_html = join_html(
        top_cards
        + _guidance_cards(
            components,
            item=item,
            metadata=metadata,
            sections=body_sections,
        )
        + [
            components.section_card(
                title="Core steps and recovery",
                eyebrow="Guidance",
                body_html=join_html(
                    [
                        f"<h3>Steps</h3>{render_list([escape(step) for step in metadata.get('steps', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">No steps recorded.</p>'}",
                        f"<h3>Rollback</h3>{render_list([escape(step) for step in metadata.get('rollback', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">No rollback recorded.</p>'}",
                    ]
                ),
            ),
            components.section_card(
                title="Revision narrative",
                eyebrow="Change",
                body_html=(
                    f'<pre class="prose-block">{escape(revision["body_markdown"])}</pre>'
                    if revision is not None
                    else '<p class="empty-state-copy">No current revision is attached to this object.</p>'
                ),
                footer_html=(
                    f'<p class="section-footer">Revision #{revision["revision_number"]} · {escape(revision["revision_review_state"])} · {escape(format_timestamp(revision["imported_at"]))}</p>'
                    if revision is not None
                    else ""
                ),
            ),
        ]
    )

    related_sections_html = join_html(
        [
            components.citations_panel(
                title="Supporting evidence",
                items=[
                    (
                        f"<strong>{escape(citation['source_title'])}</strong>"
                        f"<span class=\"list-meta\">{escape(citation['source_ref'])} · {escape(citation['validity_status'])}</span>"
                        f"<span class=\"list-meta\">snapshot: {escape(citation.get('evidence_snapshot_path') or 'missing')}</span>"
                    )
                    for citation in detail["citations"]
                ],
                empty_label="No citations are attached to the current revision.",
            ),
            components.relationships_panel(
                title="Related knowledge",
                items=[
                    f"{escape(relationship['relationship_type'])}: {link(relationship['title'], f'/objects/{quoted_path(relationship['object_id'])}')}"
                    for relationship in detail["outbound_relationships"] + detail["inbound_relationships"]
                ],
                empty_label="No related knowledge links were recorded.",
            ),
            components.audit_panel(
                title="Recent audit trail",
                items=[
                    (
                        f"{escape(format_timestamp(event['occurred_at']))} · {escape(event['event_type'])} · {escape(event['actor'])}"
                        + (
                            f'<span class="list-meta"> · {escape(", ".join(f"{key}={value}" for key, value in event["details"].items() if value))}</span>'
                            if event["details"]
                            else ""
                        )
                    )
                    for event in detail["audit_events"]
                ],
                empty_label="No audit events recorded.",
            ),
        ]
    )

    aside_html = join_html(
        [
            components.trust_summary(
                title="Safety and lifecycle",
                badges=[
                    components.badge(
                        label="Trust",
                        value=projection_state_values.get("trust_state") or "unknown",
                        tone=tone_for_trust(str(projection_state_values.get("trust_state") or "unknown")),
                    ),
                    components.badge(
                        label="Approval",
                        value=projection_state_values.get("approval_state") or "unknown",
                        tone=tone_for_approval(str(projection_state_values.get("approval_state") or "unknown")),
                    ),
                    components.badge(
                        label="Status",
                        value=projection_state_values.get("object_lifecycle_state") or "unknown",
                        tone="context",
                    ),
                ],
                summary=str(
                    (ui_projection.get("use_guidance") or {}).get("detail")
                    or "Papyrus did not return governed detail for this object."
                ),
            ),
            components.section_card(
                title="Evidence follow-up",
                eyebrow="Evidence",
                body_html=(
                    f"<p>{escape(evidence_status.get('summary') or 'No evidence summary available.')}</p>"
                    f"<p><strong>Missing snapshots:</strong> {escape(evidence_status.get('missing_snapshot_count', 0))}</p>"
                    f"<p><strong>Needs revalidation:</strong> {escape(evidence_status.get('revalidation_count', 0))}</p>"
                ),
                footer_html=link(
                    "Request evidence revalidation",
                    f"/manage/objects/{quoted_path(item['object_id'])}/evidence/revalidate",
                    css_class="button button-secondary",
                ),
            ),
            components.metadata_list(
                title="Reference metadata",
                rows=[
                    ("Owner", escape(item["owner"])),
                    ("Team", escape(item["team"])),
                    ("Canonical path", escape(item["canonical_path"])),
                    ("Systems", escape(", ".join(item["systems"]))),
                    ("Tags", escape(", ".join(item["tags"]))),
                ],
            ),
        ]
    )

    return {
        "page_template": "pages/object_detail.html",
        "page_title": item["title"],
        "headline": item["title"],
        "kicker": "Use",
        "intro": "Use the current guidance with visible safety, freshness, service context, and change history before you act.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "header_html": header_html,
            "content_sections_html": guidance_html,
            "related_sections_html": related_sections_html,
        },
    }
