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


def _hero_meta(
    *, item: dict[str, Any], content: dict[str, Any], experience: ExperienceContext
) -> str:
    owner = str(item.get("owner") or "Anonymous")
    initial = owner[0].upper() if owner else "?"
    role = str(item.get("owner_role") or "Contributor")
    date = str(item.get("last_reviewed") or item.get("created_at") or "Unknown Date")
    revision = str(
        (content.get("metadata") or {}).get("revision_id") or item.get("revision_id") or "v1.0"
    )

    return join_html(
        [
            '<div class="article-meta-row">',
            '  <div class="article-author">',
            f'    <div class="avatar">{escape(initial)}</div>',
            '    <div class="article-author-info">',
            f'      <div class="article-author-name">{escape(owner)}</div>',
            f'      <div class="article-author-role">{escape(role)}</div>',
            "    </div>",
            "  </div>",
            '  <div class="article-meta-item">',
            '    <i data-lucide="calendar" style="width: 14px; height: 14px;"></i>',
            f"    Published {escape(date)}",
            "  </div>",
            '  <div class="article-meta-item">',
            '    <i data-lucide="git-commit" style="width: 14px; height: 14px;"></i>',
            f"    Revision {escape(revision)}",
            "  </div>",
            "</div>",
        ]
    )


def render_content_section(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    body_html = (
        join_html([render_article_block(block) for block in blocks])
        if blocks
        else f'<p class="content-empty">{escape(section.get("empty") or "No content recorded.")}</p>'
    )
    title = str(section.get("title") or "").strip()
    title_html = f"<h2>{escape(title)}</h2>" if title else ""
    return (
        '<div class="article-section" data-component="content-section">'
        f"{title_html}"
        f"{body_html}</div>"
    )


def render_context_panel(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    raw_markdown = str(section.get("raw_markdown") or "").strip()
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

    title = str(section.get("title") or "").strip()
    title_html = f"<h3>{escape(title)}</h3>" if title else ""

    return (
        '<div class="card article-section context-panel" style="margin: var(--space-6) 0;">'
        f"{title_html}"
        f"{body_html}</div>"
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
                    object_history_url(str(item["object_id"])),
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
                    impact_object_url(str(item["object_id"])),
                    css_class="button button-ghost",
                ),
            ]
        )
    if experience.role == ADMIN_ROLE and revision is not None:
        actions.insert(
            0,
            link(
                "Open review context",
                review_decision_url(str(item["object_id"]), str(revision["revision_id"])),
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
            "context_html": join_html(
                [
                    f'<p class="page-header-dek">{escape(use_now)}</p>' if use_now else "",
                    _hero_meta(item=item, content=content, experience=experience),
                ]
            ),
            "actions_html": join_html([action for action in actions if action]),
        },
        "active_nav": "inspect" if experience.role == ADMIN_ROLE else "read",
        "aside_html": aside_html,
        "page_context": {
            "content_html": f'<div class="article-layout"><div class="article-body">{primary_html}</div></div>',
            "context_html": appendix_html,
        },
        "page_surface": "object-detail",
    }
