from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, READER_ROLE
from papyrus.interfaces.web.experience import ExperienceContext
from papyrus.interfaces.web.presenters.article_context_panel_presenter import (
    render_article_context_panel,
)
from papyrus.interfaces.web.presenters.article_section_presenter import render_article_section
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import compact_action_menu_html
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import impact_object_url, object_history_url, review_decision_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link
from papyrus.interfaces.web.view_models.article_projection import build_article_projection


def present_object_detail(
    renderer: TemplateRenderer, *, detail: dict[str, Any], experience: ExperienceContext
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    article = build_article_projection(
        item=detail["object"],
        revision=detail.get("current_revision"),
        metadata=detail.get("metadata") or {},
        section_content=dict(detail.get("section_content") or {}),
        related_services=detail.get("related_services") or [],
        citations=detail.get("citations") or [],
        evidence_status=detail.get("evidence_status") or {},
        audit_events=detail.get("audit_events") or [],
        ui_projection=detail.get("ui_projection") or {},
        experience=experience,
    )
    item = detail["object"]
    revision = detail.get("current_revision")
    actions: list[str] = []
    if experience.role != READER_ROLE:
        actions.extend(
            [
                link(
                    "See history",
                    object_history_url(experience.role, str(item["object_id"])),
                    css_class="button button-ghost",
                ),
                compact_action_menu_html(
                    components,
                    role=experience.role,
                    ui_projection=detail.get("ui_projection"),
                    object_id=str(item["object_id"]),
                    revision_id=str((revision or {}).get("revision_id") or "") or None,
                    current_revision_id=str(item.get("current_revision_id") or "") or None,
                ),
                link(
                    "See impact",
                    impact_object_url(experience.role, str(item["object_id"])),
                    css_class="button button-ghost",
                ),
            ]
        )
    if experience.role == ADMIN_ROLE and revision is not None:
        actions.insert(
            0,
            link(
                "Open review context",
                review_decision_url(
                    experience.role, str(item["object_id"]), str(revision["revision_id"])
                ),
                css_class="button button-primary",
            ),
        )
    primary_html = join_html(
        [render_article_section(section=section) for section in article["sections"]]
    )
    secondary_html = join_html(
        [render_article_context_panel(section=section) for section in article["secondary_sections"]]
    )
    appendix_html = "" if article["show_context_rail"] else secondary_html
    aside_html = secondary_html if article["show_context_rail"] else ""
    use_now = str(article["hero"].get("use_now") or "").strip()
    return {
        "page_template": "pages/object_detail.html",
        "page_title": item["title"],
        "page_header": {
            "headline": item["title"],
            "kicker": article["hero"]["eyebrow"],
            "intro": article["hero"]["summary"],
            "context_html": f"<p><strong>Use now:</strong> {escape(use_now)}</p>"
            if use_now
            else "",
            "actions_html": join_html([action for action in actions if action]),
        },
        "active_nav": "inspect" if experience.role == ADMIN_ROLE else "read",
        "aside_html": aside_html,
        "page_context": {
            "article_html": primary_html,
            "appendix_html": appendix_html,
        },
        "page_surface": "object-detail",
    }
