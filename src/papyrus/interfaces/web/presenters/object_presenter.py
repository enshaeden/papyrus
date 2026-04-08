from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, format_timestamp, join_html, link, quoted_path, render_list, tone_for_approval, tone_for_health, tone_for_trust


def present_object_detail(renderer: TemplateRenderer, *, detail: dict[str, Any]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    item = detail["object"]
    revision = detail["current_revision"]
    header_html = components.object_header(
        object_type=item["object_type"],
        object_id=item["object_id"],
        title=item["title"],
        summary=item["summary"],
        badges=[
            components.badge(label="Trust", value=item["trust_state"], tone=tone_for_trust(item["trust_state"])),
            components.badge(label="Approval", value=item["approval_state"] or "unknown", tone=tone_for_approval(item["approval_state"])),
            components.badge(label="Freshness", value=item["freshness_rank"], tone=tone_for_health(item["freshness_rank"])),
            components.badge(label="Citation health", value=item["citation_health_rank"], tone=tone_for_health(item["citation_health_rank"])),
        ],
        actions_html=join_html(
            [
                link("Revision history", f"/objects/{quoted_path(item['object_id'])}/revisions", css_class="button button-secondary"),
                link("New revision", f"/write/objects/{quoted_path(item['object_id'])}/revisions/new", css_class="button button-primary"),
                link("Impact view", f"/impact/object/{quoted_path(item['object_id'])}", css_class="button button-secondary"),
            ],
            " ",
        ),
    )
    content_cards = [
        components.section_card(
            title="Structured content",
            eyebrow="Read",
            body_html=join_html(
                [
                    f"<h3>Prerequisites</h3>{render_list([escape(item) for item in detail['metadata'].get('prerequisites', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">None recorded.</p>'}",
                    f"<h3>Steps</h3>{render_list([escape(item) for item in detail['metadata'].get('steps', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">None recorded.</p>'}",
                    f"<h3>Verification</h3>{render_list([escape(item) for item in detail['metadata'].get('verification', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">None recorded.</p>'}",
                    f"<h3>Rollback</h3>{render_list([escape(item) for item in detail['metadata'].get('rollback', [])], css_class='panel-list') or '<p class=\"empty-state-copy\">None recorded.</p>'}",
                ]
            ),
        ),
        components.section_card(
            title="Revision body",
            eyebrow="Current revision",
            body_html=(
                f'<pre class="prose-block">{escape(revision["body_markdown"])}</pre>'
                if revision is not None
                else '<p class="empty-state-copy">No current revision is attached to this object.</p>'
            ),
            footer_html=(
                f'<p class="section-footer">Revision #{revision["revision_number"]} · {escape(revision["revision_state"])} · {escape(format_timestamp(revision["imported_at"]))}</p>'
                if revision is not None
                else ""
            ),
        ),
    ]
    related_sections_html = join_html(
        [
            components.citations_panel(
                title="Supporting citations",
                items=[
                    f"<strong>{escape(citation['source_title'])}</strong><span class=\"list-meta\">{escape(citation['source_ref'])} · {escape(citation['validity_status'])}</span>"
                    for citation in detail["citations"]
                ],
                empty_label="No citations attached to the current revision.",
            ),
            components.relationships_panel(
                title="Related services",
                items=[
                    f"{link(service['service_name'], f'/services/{quoted_path(service['service_id'])}')}"
                    f'<span class="list-meta">{escape(service["service_criticality"])} · {escape(service["status"])}</span>'
                    for service in detail["related_services"]
                ],
                empty_label="No related services linked.",
            ),
            components.relationships_panel(
                title="Outbound relationships",
                items=[
                    f"{escape(relationship['relationship_type'])}: {link(relationship['title'], f'/objects/{quoted_path(relationship['object_id'])}')}"
                    for relationship in detail["outbound_relationships"]
                ],
                empty_label="No outbound relationships linked.",
            ),
            components.relationships_panel(
                title="Inbound relationships",
                items=[
                    f"{escape(relationship['relationship_type'])}: {link(relationship['title'], f'/objects/{quoted_path(relationship['object_id'])}')}"
                    for relationship in detail["inbound_relationships"]
                ],
                empty_label="No inbound relationships linked.",
            ),
        ]
    )
    aside_html = join_html(
        [
            components.trust_summary(
                title="Trust posture",
                badges=[
                    components.badge(label="Trust", value=item["trust_state"], tone=tone_for_trust(item["trust_state"])),
                    components.badge(label="Approval", value=item["approval_state"] or "unknown", tone=tone_for_approval(item["approval_state"])),
                    components.badge(label="Current revision", value=revision["revision_state"] if revision else "none", tone=tone_for_approval(revision["revision_state"] if revision else "draft")),
                ],
                summary="Object trust, approval, and evidence health stay visible while the operator reads the content.",
            ),
            components.metadata_list(
                title="Object metadata",
                rows=[
                    ("Owner", escape(item["owner"])),
                    ("Team", escape(item["team"])),
                    ("Status", escape(item["status"])),
                    ("Last reviewed", escape(item["last_reviewed"])),
                    ("Review cadence", escape(item["review_cadence"])),
                    ("Canonical path", escape(item["canonical_path"])),
                    ("Systems", escape(", ".join(item["systems"]))),
                    ("Tags", escape(", ".join(item["tags"]))),
                ],
            ),
            components.audit_panel(
                title="Recent audit",
                items=[
                    f"{escape(format_timestamp(event['occurred_at']))} · {escape(event['event_type'])} · {escape(event['actor'])}"
                    for event in detail["audit_events"]
                ],
                empty_label="No audit events recorded.",
            ),
        ]
    )
    return {
        "page_template": "pages/object_detail.html",
        "page_title": item["title"],
        "headline": item["title"],
        "kicker": "Read",
        "intro": "Operational content is separated from evidence, relationships, and audit posture so trust is readable at a glance.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "header_html": header_html,
            "content_sections_html": join_html(content_cards),
            "related_sections_html": related_sections_html,
        },
    }
