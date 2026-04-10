from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, link, quoted_path, tone_for_approval, tone_for_health, tone_for_trust


def _queue_item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _use_when_text(item: dict[str, Any]) -> str:
    summary = str(item.get("summary") or "").strip()
    if summary:
        return summary
    object_type = str(item.get("object_type") or "")
    if object_type == "runbook":
        return "Use when you need a step-by-step operational procedure."
    if object_type == "known_error":
        return "Use when you need symptom-driven troubleshooting guidance."
    if object_type == "service_record":
        return "Use when you need service context, dependencies, or support ownership."
    if object_type == "policy":
        return "Use when you need governed controls, scope, and exception handling."
    if object_type == "system_design":
        return "Use when you need architecture, interfaces, and operational design context."
    return "Use when this item is the best available operational fit."


def _next_action_text(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("next_action")
        or use_guidance.get("detail")
        or "Papyrus did not return a next action for this result."
    )


def _status_detail_text(item: dict[str, Any]) -> str:
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return str(
        use_guidance.get("detail")
        or use_guidance.get("summary")
        or "Papyrus did not return governed detail for this result."
    )


def _projection_state_value(item: dict[str, Any], key: str) -> str:
    return str(projection_state(item.get("ui_projection")).get(key) or "unknown")


def _queue_action_label(item: dict[str, Any]) -> str:
    if bool((item.get("ui_projection") or {}).get("use_guidance", {}).get("safe_to_use")):
        return "Use guidance"
    approval_state = _projection_state_value(item, "approval_state")
    if approval_state in {"draft", "rejected"}:
        return "Update draft"
    if approval_state == "in_review":
        return "Check review"
    return "Continue"


def _queue_status_cell(components: ComponentPresenter, item: dict[str, Any]) -> str:
    state = projection_state(item.get("ui_projection"))
    use_guidance = projection_use_guidance(item.get("ui_projection"))
    return components.decision_cell(
        title_html=escape(use_guidance.get("summary") or "Status unavailable"),
        badges=[
            components.badge(
                label="Trust",
                value=_projection_state_value(item, "trust_state"),
                tone=tone_for_trust(_projection_state_value(item, "trust_state")),
            ),
            components.badge(
                label="Approval",
                value=_projection_state_value(item, "approval_state"),
                tone=tone_for_approval(_projection_state_value(item, "approval_state")),
            ),
            components.badge(
                label="Freshness",
                value=item.get("freshness_rank", 0),
                tone=tone_for_health(int(item.get("freshness_rank") or 0)),
            ),
            components.badge(
                label="Evidence",
                value=item.get("citation_health_rank", 0),
                tone=tone_for_health(int(item.get("citation_health_rank") or 0)),
            ),
        ],
        supporting_html=escape(_status_detail_text(item)),
        meta=[
            escape(f"Revision {state.get('revision_review_state') or 'unknown'}"),
        ],
    )


def _queue_guidance_cell(components: ComponentPresenter, item: dict[str, Any]) -> str:
    services_html = (
        ", ".join(
            link(service["service_name"], f"/services/{quoted_path(service['service_id'])}")
            for service in item["linked_services"]
        )
        if item["linked_services"]
        else ""
    )
    return components.decision_cell(
        title_html=link(item["title"], _queue_item_href(item)),
        meta=[
            escape(f"{item['object_type']}"),
            escape(item["object_id"]),
            services_html,
        ],
        extra_html=components.inline_disclosure(
            label="Source details",
            body_html=f"<p>{escape(item['path'])}</p>",
        ),
    )


def _queue_attention_cell(components: ComponentPresenter, item: dict[str, Any]) -> str:
    return components.decision_cell(
        title_html=escape(_next_action_text(item)),
        supporting_html=escape(_use_when_text(item)),
        meta=[
            escape(f"Last reviewed {item.get('last_reviewed') or 'unknown'}"),
            escape(f"Cadence {item.get('review_cadence') or 'unknown'}"),
        ],
    )


def present_queue_page(
    renderer: TemplateRenderer,
    *,
    items: list[dict[str, Any]],
    query: str,
    selected_type: str,
    selected_trust: str,
    selected_approval: str,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    normalized_items = []
    for item in items:
        normalized = dict(item)
        normalized.setdefault("linked_services", [])
        normalized_items.append(normalized)
    summary_html = components.trust_summary(
        title="Read posture",
        badges=[
            components.badge(label="Items", value=len(normalized_items), tone="brand"),
            components.badge(
                label="Safe to use",
                value=sum(
                    1
                    for item in normalized_items
                    if bool((item.get("ui_projection") or {}).get("use_guidance", {}).get("safe_to_use"))
                ),
                tone="approved",
            ),
            components.badge(
                label="Review before use",
                value=sum(
                    1
                    for item in normalized_items
                    if not bool((item.get("ui_projection") or {}).get("use_guidance", {}).get("safe_to_use"))
                ),
                tone="pending",
            ),
            components.badge(label="Weak evidence", value=sum(1 for item in normalized_items if item["citation_health_rank"] > 0), tone="warning"),
            components.badge(label="Needs freshness check", value=sum(1 for item in normalized_items if item["freshness_rank"] > 0), tone="danger"),
        ],
        summary="Best match first, with trust and the next step beside it.",
    )
    filter_controls_html = (
        '<form class="filter-form" method="get" action="/read">'
        f'<input type="search" name="query" placeholder="Search guidance" value="{escape(query)}" data-filter-input="true" />'
        '<select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All types</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbooks</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known errors</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service records</option>'
        f'<option value="policy"{" selected" if selected_type == "policy" else ""}>Policies</option>'
        f'<option value="system_design"{" selected" if selected_type == "system_design" else ""}>System designs</option>'
        "</select>"
        '<select name="trust">'
        f'<option value=""{" selected" if not selected_trust else ""}>All trust</option>'
        f'<option value="trusted"{" selected" if selected_trust == "trusted" else ""}>Trusted</option>'
        f'<option value="weak_evidence"{" selected" if selected_trust == "weak_evidence" else ""}>Weak evidence</option>'
        f'<option value="stale"{" selected" if selected_trust == "stale" else ""}>Stale</option>'
        f'<option value="suspect"{" selected" if selected_trust == "suspect" else ""}>Suspect</option>'
        "</select>"
        '<select name="approval">'
        f'<option value=""{" selected" if not selected_approval else ""}>All approval</option>'
        f'<option value="approved"{" selected" if selected_approval == "approved" else ""}>Approved</option>'
        f'<option value="in_review"{" selected" if selected_approval == "in_review" else ""}>In review</option>'
        f'<option value="draft"{" selected" if selected_approval == "draft" else ""}>Draft</option>'
        f'<option value="rejected"{" selected" if selected_approval == "rejected" else ""}>Rejected</option>'
        "</select>"
        '<button class="button button-primary" type="submit">Show guidance</button>'
        "</form>"
    )
    rows = [
        [
            _queue_guidance_cell(components, item),
            _queue_status_cell(components, item),
            _queue_attention_cell(components, item),
            link(_queue_action_label(item), _queue_item_href(item), css_class="button button-primary"),
        ]
        for item in normalized_items
    ]
    queue_html = (
        components.section_card(
            title="Guidance results",
            eyebrow="Read",
            body_html=components.queue_table(
                headers=["Guidance", "Status", "What needs attention", "Do next"],
                rows=rows,
                table_id="read-guidance",
            ),
            footer_html='<p class="section-footer">Rows are ordered so the safest current answer appears first.</p>',
        )
        if rows
        else components.empty_state(
            title="No matching guidance",
            description="Adjust filters or search terms to widen the read scope.",
        )
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Read Guidance",
        "headline": "Read Operational Guidance",
        "kicker": "Read",
        "intro": "Find the right guidance and see the next step immediately.",
        "active_nav": "read",
        "aside_html": "",
        "page_context": {
            "filter_bar_html": components.filter_bar(title="Read filters", controls_html=filter_controls_html),
            "summary_html": summary_html,
            "queue_html": queue_html,
            "secondary_html": "",
        },
    }
