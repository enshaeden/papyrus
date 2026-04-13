from __future__ import annotations

from typing import Any

from papyrus.interfaces.web.view_helpers import escape, join_html

from .article_content_presenter import render_article_block


def render_article_context_panel(*, section: dict[str, Any]) -> str:
    blocks = [block for block in section.get("blocks") or [] if block]
    raw_markdown = str(section.get("raw_markdown") or "").strip()
    section_surface = (
        "posture" if str(section.get("section_id") or "") == "governance" else "object-detail"
    )
    body_html = join_html([render_article_block(block) for block in blocks]) if blocks else ""
    if raw_markdown:
        body_html += (
            '<details class="article-context-panel__source" data-component="inline-disclosure">'
            "<summary>View revision source</summary>"
            f'<pre class="source-markdown">{escape(raw_markdown)}</pre>'
            "</details>"
        )
    if not body_html:
        body_html = f'<p class="article-empty">{escape(section.get("empty") or "No supporting context recorded.")}</p>'
    return (
        f'<section class="article-context-panel" data-component="article-context-panel" data-surface="{section_surface}">'
        f'<p class="article-context-panel__kicker">{escape(section["eyebrow"])}</p>'
        f"<h3>{escape(section['title'])}</h3>"
        f"{body_html}</section>"
    )
