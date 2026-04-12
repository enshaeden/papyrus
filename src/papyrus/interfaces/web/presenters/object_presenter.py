from __future__ import annotations

from typing import Any

from papyrus.application.read_models.article_projection import build_article_projection
from papyrus.domain.actor import resolve_actor
from papyrus.interfaces.web.presenters.article_context_panel_presenter import render_article_context_panel
from papyrus.interfaces.web.presenters.article_hero_presenter import render_article_hero
from papyrus.interfaces.web.presenters.article_section_presenter import render_article_section
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import compact_action_menu_html
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import join_html, link, quoted_path


def present_object_detail(renderer: TemplateRenderer, *, detail: dict[str, Any], actor_id: str = "") -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    actor = resolve_actor(actor_id or "local.operator")
    article = detail.get("article_projection") or build_article_projection(
        item=detail["object"],
        revision=detail.get("current_revision"),
        metadata=detail.get("metadata") or {},
        section_content=dict((detail.get("current_revision") or {}).get("section_content") or {}),
        related_services=detail.get("related_services") or [],
        citations=detail.get("citations") or [],
        evidence_status=detail.get("evidence_status") or {},
        audit_events=detail.get("audit_events") or [],
        ui_projection=detail.get("ui_projection") or {},
        actor_id=actor.actor_id,
    )
    item = detail["object"]
    revision = detail.get("current_revision")
    actions = [
        link("See history", f"/objects/{quoted_path(item['object_id'])}/revisions", css_class="button button-ghost"),
        compact_action_menu_html(
            components,
            ui_projection=detail.get("ui_projection"),
            object_id=str(item["object_id"]),
            revision_id=str((revision or {}).get("revision_id") or "") or None,
            current_revision_id=str(item.get("current_revision_id") or "") or None,
        ),
        link("See consequences", f"/impact/object/{quoted_path(item['object_id'])}", css_class="button button-ghost"),
    ]
    if actor.actor_id == "local.reviewer" and revision is not None:
        actions.insert(
            0,
            link(
                "Open review context",
                f"/manage/reviews/{quoted_path(item['object_id'])}/{quoted_path(revision['revision_id'])}",
                css_class="button button-primary",
            ),
        )
    hero_html = render_article_hero(hero=article["hero"], actions=actions)
    primary_html = join_html([render_article_section(section=section) for section in article["sections"]])
    secondary_html = join_html([render_article_context_panel(section=section) for section in article["secondary_sections"]])
    appendix_html = "" if article["show_context_rail"] else secondary_html
    aside_html = secondary_html if article["show_context_rail"] else ""
    return {
        "page_template": "pages/object_detail.html",
        "page_title": item["title"],
        "page_header": {
            "headline": "Read",
            "kicker": actor.display_name,
            "intro": "Operational article view",
        },
        "active_nav": "read",
        "aside_html": aside_html,
        "page_context": {
            "hero_html": hero_html,
            "article_html": primary_html,
            "appendix_html": appendix_html,
        },
        "page_surface": "object-detail",
    }
