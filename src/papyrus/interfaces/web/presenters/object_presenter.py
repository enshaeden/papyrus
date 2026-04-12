from __future__ import annotations

from typing import Any

from papyrus.application.read_models.article_projection import build_article_projection
from papyrus.domain.actor import resolve_actor
from papyrus.interfaces.web.presenters.governed_presenter import authoring_entry_html
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path


def _render_block(block: dict[str, Any]) -> str:
    kind = str(block.get("kind") or "")
    title = str(block.get("title") or "").strip()
    title_html = f'<p class="article-block-title">{escape(title)}</p>' if title else ""
    if kind == "paragraph":
        return f'<div class="article-block article-block-paragraph">{title_html}<p>{escape(block["text"])}</p></div>'
    if kind == "list":
        return (
            f'<div class="article-block article-block-list">{title_html}<ul class="article-list">'
            + join_html([f"<li>{escape(item)}</li>" for item in block["items"]])
            + "</ul></div>"
        )
    if kind == "facts":
        return (
            f'<div class="article-block article-block-facts">{title_html}<dl class="article-facts">'
            + join_html([f"<div><dt>{escape(label)}</dt><dd>{escape(value)}</dd></div>" for label, value in block["rows"]])
            + "</dl></div>"
        )
    return ""


def _render_article_section(section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    body_html = join_html([_render_block(block) for block in blocks]) if blocks else f'<p class="article-empty">{escape(section.get("empty") or "No article content recorded.")}</p>'
    return (
        '<section class="article-section" data-component="article-section" data-surface="object-detail">'
        f'<p class="article-section-kicker">{escape(section["eyebrow"])}</p>'
        f'<h2>{escape(section["title"])}</h2>'
        f"{body_html}</section>"
    )


def _render_context_section(section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    raw_markdown = str(section.get("raw_markdown") or "").strip()
    body_html = join_html([_render_block(block) for block in blocks]) if blocks else ""
    if raw_markdown:
        body_html += (
            '<details class="source-disclosure" data-component="inline-disclosure">'
            "<summary>View revision source</summary>"
            f'<pre class="source-markdown">{escape(raw_markdown)}</pre>'
            "</details>"
        )
    if not body_html:
        body_html = f'<p class="article-empty">{escape(section.get("empty") or "No supporting context recorded.")}</p>'
    return (
        '<section class="article-context-panel" data-component="surface-panel" data-surface="object-detail">'
        f'<p class="article-context-kicker">{escape(section["eyebrow"])}</p>'
        f'<h3>{escape(section["title"])}</h3>'
        f"{body_html}</section>"
    )


def present_object_detail(renderer: TemplateRenderer, *, detail: dict[str, Any], actor_id: str = "") -> dict[str, Any]:
    del renderer
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
        authoring_entry_html(
            object_id=str(item["object_id"]),
            ui_projection=detail.get("ui_projection"),
            current_revision_id=str(item.get("current_revision_id") or "") or None,
            label_override="Revise guidance",
            allow_start_when_not_in_draft_state=True,
        )
        or "",
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
    hero_html = (
        '<section class="article-hero" data-component="article-hero" data-surface="object-detail">'
        f'<p class="article-hero-kicker">{escape(article["hero"]["eyebrow"])}</p>'
        f'<h1>{escape(article["hero"]["title"])}</h1>'
        f'<p class="article-hero-summary">{escape(article["hero"]["summary"])}</p>'
        + (
            f'<p class="article-hero-use-now">{escape(article["hero"]["use_now"])}</p>'
            if str(article["hero"].get("use_now") or "").strip()
            else ""
        )
        + f'<div class="article-hero-actions">{join_html([action for action in actions if action])}</div>'
        + "</section>"
    )
    primary_html = join_html([_render_article_section(section) for section in article["sections"]])
    secondary_html = join_html([_render_context_section(section) for section in article["secondary_sections"]])
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
