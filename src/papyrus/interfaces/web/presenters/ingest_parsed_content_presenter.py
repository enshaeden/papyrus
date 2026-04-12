from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape


def render_ingest_parsed_content(*, normalized: dict[str, object], surface: str) -> str:
    return (
        f'<section class="ingest-parsed-content" data-component="ingest-parsed-content" data-surface="{escape(surface)}">'
        '<p class="ingest-parsed-content__kicker">Import</p>'
        "<h2>Parsed content</h2>"
        f"<p><strong>Title:</strong> {escape(normalized.get('title') or 'Untitled')}</p>"
        f"<p><strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}</p>"
        f"<p><strong>Lists:</strong> {escape(len(normalized.get('lists', [])))}</p>"
        f"<p><strong>Tables:</strong> {escape(len(normalized.get('tables', [])))}</p>"
        f"<p><strong>Links:</strong> {escape(len(normalized.get('links', [])))}</p>"
        "</section>"
    )
