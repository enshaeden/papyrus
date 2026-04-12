from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, render_list


def render_ingest_parser_assessment(*, detail: dict[str, object], surface: str) -> str:
    normalized = detail["normalized_content"]
    warnings = [escape(str(item)) for item in normalized.get("parser_warnings", [])]
    degradation_notes = [escape(str(item)) for item in normalized.get("degradation_notes", [])]
    extraction_quality = normalized.get("extraction_quality") or {}
    quality_state = str(extraction_quality.get("state") or "unknown")
    quality_score = float(extraction_quality.get("score") or 0.0)
    summary = str(extraction_quality.get("summary") or "No parser assessment was recorded.")
    tone = "warning" if quality_state == "degraded" or warnings or degradation_notes else "approved"
    return (
        f'<section class="ingest-parser-assessment tone-{escape(tone)}" data-component="ingest-parser-assessment" data-surface="{escape(surface)}">'
        '<p class="ingest-parser-assessment__kicker">Import</p>'
        "<h2>Parser assessment</h2>"
        f"<p><strong>Extraction quality:</strong> {escape(quality_state)} ({escape(round(quality_score, 2))})</p>"
        f"<p>{escape(summary)}</p>"
        "<p><strong>Parser warnings</strong></p>"
        + (
            render_list(warnings, css_class="validation-findings")
            or '<p class="empty-state-copy">No parser warnings were recorded.</p>'
        )
        + "<p><strong>Degradation notes</strong></p>"
        + (
            render_list(degradation_notes, css_class="validation-findings")
            or '<p class="empty-state-copy">No degradation notes were recorded.</p>'
        )
        + "</section>"
    )
