from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.presenters.governed_presenter import primary_surface_href, projection_state, projection_use_guidance
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link


def _item_href(item: dict[str, Any]) -> str:
    return primary_surface_href(
        object_id=str(item["object_id"]),
        revision_id=str(item.get("revision_id") or item.get("current_revision_id") or "").strip() or None,
        current_revision_id=str(item.get("current_revision_id") or "").strip() or None,
        ui_projection=item.get("ui_projection"),
    )


def _intervention_groups(queue: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups = {
        "trust_debt": [],
        "review_backlog": [],
        "ownership_gaps": [],
        "stable_watch": [],
    }
    for item in queue:
        state = projection_state(item.get("ui_projection"))
        trust_state = str(state.get("trust_state") or item.get("trust_state") or "unknown")
        review_state = str(state.get("revision_review_state") or item.get("revision_review_state") or "unknown")
        if trust_state in {"suspect", "stale", "weak_evidence"}:
            groups["trust_debt"].append(item)
        elif review_state in {"in_review", "rejected", "draft"}:
            groups["review_backlog"].append(item)
        elif not str(item.get("owner") or "").strip() or int(item.get("ownership_rank") or 0) > 0:
            groups["ownership_gaps"].append(item)
        else:
            groups["stable_watch"].append(item)
    return groups


def _board_column(title: str, summary: str, items: list[dict[str, Any]], *, tone: str) -> str:
    body = (
        join_html(
            [
                (
                    '<article class="health-card">'
                    f'<p class="health-card-kicker">{escape(str(item.get("object_type") or "").replace("_", " "))} · {escape(item["object_id"])}</p>'
                    f'<h3>{link(item["title"], _item_href(item))}</h3>'
                    f'<p>{escape(str(projection_use_guidance(item.get("ui_projection")).get("summary") or item.get("summary") or "No summary recorded."))}</p>'
                    f'<p class="health-card-next">{escape(str(projection_use_guidance(item.get("ui_projection")).get("next_action") or "Inspect article"))}</p>'
                    f'{link("Open", _item_href(item), css_class="button button-ghost", attrs={"data-action-id": "open-primary-surface"})}'
                    "</article>"
                )
                for item in items[:6]
            ]
        )
        if items
        else '<p class="health-empty">No items in this intervention group.</p>'
    )
    return (
        f'<section class="health-board-column tone-{escape(tone)}" data-component="health-column" data-surface="knowledge-health">'
        f'<h2>{escape(title)}</h2>'
        f'<p class="health-board-summary">{escape(summary)}</p>'
        f"{body}</section>"
    )


def present_trust_dashboard(
    renderer: TemplateRenderer,
    *,
    dashboard: dict[str, Any],
    selected_object_id: str = "",
    selected_revision_id: str = "",
) -> dict[str, Any]:
    del renderer
    groups = _intervention_groups(dashboard["queue"])
    cleanup_counts = dashboard.get("cleanup_counts") or {}
    board_html = (
        '<section class="health-board" data-component="health-board" data-surface="knowledge-health">'
        '<div class="health-board-hero">'
        "<h1>Intervene by debt type, not by generic queue order.</h1>"
        "<p>Knowledge Health is a stewardship board: trust debt, review backlog, ownership gaps, and stable watch items are grouped by the kind of intervention they need.</p>"
        "</div>"
        '<div class="health-board-grid">'
        + _board_column("Trust debt", "Weak, stale, or suspect guidance that changes whether operators should trust the surface.", groups["trust_debt"], tone="danger")
        + _board_column("Review backlog", "Guidance waiting on explicit governance decisions.", groups["review_backlog"], tone="warning")
        + _board_column("Ownership gaps", "Articles that need clearer stewardship before they age into drift.", groups["ownership_gaps"], tone="brand")
        + _board_column("Stable watch", "Items worth monitoring without immediate intervention.", groups["stable_watch"], tone="default")
        + "</div></section>"
    )
    cleanup_html = (
        '<section class="health-cleanup" data-component="cleanup-board" data-surface="knowledge-health">'
        "<h2>Cleanup and trust debt</h2>"
        '<div class="health-cleanup-grid">'
        f'<article><p class="cleanup-metric">{escape(cleanup_counts.get("placeholder-heavy", 0))}</p><p>Placeholder-heavy</p></article>'
        f'<article><p class="cleanup-metric">{escape(cleanup_counts.get("legacy-blueprint-fallback", 0))}</p><p>Legacy fallback</p></article>'
        f'<article><p class="cleanup-metric">{escape(cleanup_counts.get("unclear-ownership", 0))}</p><p>Ownership gaps</p></article>'
        f'<article><p class="cleanup-metric">{escape(cleanup_counts.get("weak-evidence", 0))}</p><p>Weak evidence</p></article>'
        f'<article><p class="cleanup-metric">{escape(cleanup_counts.get("migration-gaps", 0))}</p><p>Migration gaps</p></article>'
        "</div></section>"
    )
    validation_html = (
        '<section class="health-validation" data-component="validation-board" data-surface="knowledge-health">'
        "<h2>Validation posture</h2>"
        f'<p>{escape(dashboard["validation_posture"]["summary"])}</p>'
        f'<p>{escape(dashboard["validation_posture"]["detail"])}</p>'
        "</section>"
    )
    return {
        "page_template": "pages/dashboard_trust.html",
        "page_title": "Knowledge Health",
        "page_header": {
            "headline": "Knowledge Health",
            "intro": "Stewardship and risk board",
        },
        "active_nav": "health",
        "aside_html": "",
        "page_context": {
            "summary_cards_html": board_html + cleanup_html + validation_html,
            "primary_html": "",
        },
        "page_surface": "knowledge-health",
    }
