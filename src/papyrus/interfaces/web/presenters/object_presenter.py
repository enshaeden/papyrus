from __future__ import annotations

from typing import Any

from papyrus.application.role_visibility import ADMIN_ROLE, READER_ROLE
from papyrus.interfaces.web.experience import ExperienceContext
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.governed_presenter import compact_action_menu_html
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import impact_object_url, object_history_url, review_decision_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link
from papyrus.interfaces.web.view_models.content_projection import build_content_projection

from .article_content_presenter import render_article_block
from .reader_object_tree_presenter import render_reader_object_tree_nav


def render_content_section(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    body_html = (
        join_html([render_article_block(block) for block in blocks])
        if blocks
        else f'<p class="content-empty">{escape(section.get("empty") or "No content recorded.")}</p>'
    )
    return (
        '<section class="content-section" data-component="content-section" data-surface="object-detail">'
        f'<p class="content-section__kicker">{escape(section["eyebrow"])}</p>'
        f"<h2>{escape(section['title'])}</h2>"
        f"{body_html}</section>"
    )


def render_context_panel(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    raw_markdown = str(section.get("raw_markdown") or "").strip()
    section_surface = (
        "posture" if str(section.get("section_id") or "") == "governance" else "object-detail"
    )
    body_html = join_html([render_article_block(block) for block in blocks]) if blocks else ""
    if raw_markdown:
        body_html += (
            '<details class="context-panel__source" data-component="inline-disclosure">'
            "<summary>View revision source</summary>"
            f'<pre class="source-markdown">{escape(raw_markdown)}</pre>'
            "</details>"
        )
    if not body_html:
        body_html = f'<p class="content-empty">{escape(section.get("empty") or "No supporting context recorded.")}</p>'
    return (
        f'<section class="context-panel" data-component="context-panel" data-surface="{section_surface}">'
        f'<p class="context-panel__kicker">{escape(section["eyebrow"])}</p>'
        f"<h3>{escape(section['title'])}</h3>"
        f"{body_html}</section>"
    )


def present_object_detail(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, Any],
    experience: ExperienceContext,
    reader_object_nav: dict[str, Any] | None = None,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    content = build_content_projection(
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
        [render_content_section(section=section) for section in content["sections"]]
    )
    secondary_html = join_html(
        [render_context_panel(section=section) for section in content["secondary_sections"]]
    )
    if experience.role == READER_ROLE:
        appendix_html = secondary_html
        aside_html = render_reader_object_tree_nav(reader_object_nav)
    else:
        appendix_html = "" if content["show_context_rail"] else secondary_html
        aside_html = secondary_html if content["show_context_rail"] else ""
    use_now = str(content["hero"].get("use_now") or "").strip()
    return {
        "page_template": "pages/object_detail.html",
        "page_title": item["title"],
        "page_header": {
            "headline": item["title"],
            "kicker": content["hero"]["eyebrow"],
            "context_html": f"<p><strong>Use now:</strong> {escape(use_now)}</p>"
            if use_now
            else "",
            "actions_html": join_html([action for action in actions if action]),
        },
        "active_nav": "inspect" if experience.role == ADMIN_ROLE else "read",
        "aside_html": aside_html,
        "page_context": {
            "content_html": primary_html,
            "context_html": appendix_html,
        },
        "page_surface": "object-detail",
    }
