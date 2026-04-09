from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def _queue_item_href(item: dict[str, Any]) -> str:
    if str(item.get("approval_state") or "") in {"draft", "rejected"}:
        return f"/write/objects/{quoted_path(item['object_id'])}/revisions/new#revision-form"
    if item.get("current_revision_id"):
        return f"/objects/{quoted_path(item['object_id'])}"
    return f"/write/objects/{quoted_path(item['object_id'])}/revisions/new#revision-form"


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
    return "Use when this item is the best available operational fit."


def _next_action_text(item: dict[str, Any]) -> str:
    approval_state = str(item.get("approval_state") or "")
    trust_state = str(item.get("trust_state") or "")
    if approval_state == "approved" and trust_state == "trusted":
        return "Safe to use now."
    if approval_state in {"draft", "rejected"}:
        return "Complete or revise this guidance before relying on it."
    if approval_state == "in_review":
        return "Use the last approved guidance and route this revision through review."
    if trust_state == "weak_evidence":
        return "Verify the supporting evidence before use."
    if trust_state == "stale":
        return "Revalidate freshness before use."
    if trust_state == "suspect":
        return "Escalate or review the object before use."
    return "Inspect the detail page for the next safe step."


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
        normalized.setdefault("posture", {"trust_summary": ", ".join(item.get("reasons", [])) or str(item.get("trust_state") or "")})
        normalized.setdefault("linked_services", [])
        normalized_items.append(normalized)
    summary_html = components.trust_summary(
        title="Read posture",
        badges=[
            components.badge(label="Items", value=len(normalized_items), tone="brand"),
            components.badge(label="Safe to use", value=sum(1 for item in normalized_items if item["approval_state"] == "approved" and item["trust_state"] == "trusted"), tone="approved"),
            components.badge(label="Review before use", value=sum(1 for item in normalized_items if item["approval_state"] != "approved" or item["trust_state"] != "trusted"), tone="pending"),
            components.badge(label="Weak evidence", value=sum(1 for item in normalized_items if item["citation_health_rank"] > 0), tone="warning"),
            components.badge(label="Needs freshness check", value=sum(1 for item in normalized_items if item["freshness_rank"] > 0), tone="danger"),
        ],
        summary="Papyrus surfaces the best current answer first, then tells you when to verify, review, or escalate before acting.",
    )
    filter_controls_html = (
        '<form class="filter-form" method="get" action="/read">'
        f'<input type="search" name="query" placeholder="Search guidance" value="{escape(query)}" data-filter-input="true" />'
        '<select name="object_type">'
        f'<option value=""{" selected" if not selected_type else ""}>All types</option>'
        f'<option value="runbook"{" selected" if selected_type == "runbook" else ""}>Runbooks</option>'
        f'<option value="known_error"{" selected" if selected_type == "known_error" else ""}>Known errors</option>'
        f'<option value="service_record"{" selected" if selected_type == "service_record" else ""}>Service records</option>'
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
        '<button class="button button-secondary" type="submit">Apply</button>'
        "</form>"
    )
    rows = [
        [
            f"{link(item['title'], _queue_item_href(item))}"
            f'<p class="cell-meta">{escape(item["object_type"])} · {escape(item["object_id"])}</p>'
            f'<p class="cell-meta">{escape(item["path"])}</p>',
            f"{escape(_use_when_text(item))}<p class=\"cell-meta\">Last reviewed {escape(item.get('last_reviewed') or 'unknown')} · cadence {escape(item.get('review_cadence') or 'unknown')}</p>",
            " ".join(
                [
                    components.badge(label="Trust", value=item["trust_state"], tone="approved" if item["trust_state"] == "trusted" else "warning"),
                    components.badge(label="Approval", value=item["approval_state"], tone="approved" if item["approval_state"] == "approved" else "pending"),
                ]
            )
            + f'<p class="cell-meta">{escape(item["posture"]["trust_summary"])}</p>',
            (
                ", ".join(
                    link(service["service_name"], f"/services/{quoted_path(service['service_id'])}")
                    for service in item["linked_services"]
                )
                if item["linked_services"]
                else '<span class="cell-meta">No linked service context.</span>'
            ),
            escape(_next_action_text(item)),
        ]
        for item in normalized_items
    ]
    queue_html = (
        components.section_card(
            title="Guidance results",
            eyebrow="Read",
            body_html=components.queue_table(
                headers=["Guidance", "When to use it", "Safe now?", "Affects / services", "Next action"],
                rows=rows,
                table_id="read-guidance",
            ),
            footer_html='<p class="section-footer">Results are ordered to surface the safest current operational answer before weaker, stale, or isolated guidance.</p>',
        )
        if rows
        else components.empty_state(
            title="No matching guidance",
            description="Adjust filters or search terms to widen the read scope.",
        )
    )
    secondary_html = components.section_card(
        title="How to use read results",
        eyebrow="Read",
        body_html=(
            "<p>Read starts with the current operational answer, not the metadata. Governance remains visible as a guardrail so the next click is informed, not blind.</p>"
        ),
    )
    aside_html = join_html(
        [
            summary_html,
            components.validation_summary(
                title="Read checklist",
                findings=[
                    "Start with items that are both approved and trusted.",
                    "If trust or approval is degraded, follow the next-action cue before using the guidance.",
                    "Use linked services to stay inside the right operational context.",
                ],
            ),
        ]
    )
    return {
        "page_template": "pages/queue.html",
        "page_title": "Read Guidance",
        "headline": "Read Operational Guidance",
        "kicker": "Read",
        "intro": "Find the right operational guidance quickly, understand when to use it, and see what to do next if it is not yet safe to rely on.",
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "filter_bar_html": components.filter_bar(title="Read filters", controls_html=filter_controls_html),
            "summary_html": summary_html,
            "queue_html": queue_html,
            "secondary_html": secondary_html,
        },
    }
