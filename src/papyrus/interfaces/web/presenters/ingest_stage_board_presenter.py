from __future__ import annotations

from papyrus.domain.ingestion import has_mapping_result
from papyrus.interfaces.web.view_helpers import escape, join_html


def _stage_card(*, title: str, tone: str, body_lines: list[str]) -> str:
    return (
        f'<article class="ingest-stage-board__card tone-{escape(tone)}" data-component="ingest-stage-card" data-surface="ingest-detail">'
        f"<h3>{escape(title)}</h3>"
        + join_html([f"<p>{line}</p>" for line in body_lines])
        + "</article>"
    )


def render_ingest_stage_board(*, detail: dict[str, object]) -> str:
    normalized = detail["normalized_content"]
    classification = detail["classification"]
    mapping = detail.get("mapping_result") or {}
    mapping_generated = has_mapping_result(mapping)
    extraction_quality = normalized.get("extraction_quality") or {}
    parser_warnings = normalized.get("parser_warnings") or []
    parse_tone = (
        "warning"
        if str(extraction_quality.get("state") or "") == "degraded" or parser_warnings
        else "approved"
    )
    cards = [
        _stage_card(
            title="Upload",
            tone="approved",
            body_lines=[
                f"<strong>File:</strong> {escape(detail['filename'])}",
                f"<strong>Media type:</strong> {escape(detail['media_type'])}",
            ],
        ),
        _stage_card(
            title="Parse",
            tone=parse_tone,
            body_lines=[
                f"<strong>Parser:</strong> {escape(detail['parser_name'])}",
                f"<strong>Headings:</strong> {escape(len(normalized.get('headings', [])))}",
                f"<strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}",
                f"<strong>Extraction quality:</strong> {escape(extraction_quality.get('state') or 'unknown')}",
                f"<strong>Parser warnings:</strong> {escape(len(parser_warnings))}",
            ],
        ),
        _stage_card(
            title="Classify",
            tone="approved",
            body_lines=[
                f"<strong>Suggested content type:</strong> {escape(classification.get('blueprint_id') or 'unknown')}",
                f"<strong>Confidence:</strong> {escape(classification.get('confidence') or 0.0)}",
            ],
        ),
        _stage_card(
            title="Map",
            tone=(
                "warning"
                if mapping_generated
                and (
                    mapping.get("missing_sections")
                    or mapping.get("low_confidence")
                    or mapping.get("conflicts")
                )
                else "approved"
                if mapping_generated
                else "default"
            ),
            body_lines=(
                [
                    f"<strong>Missing required sections:</strong> {escape(len(mapping.get('missing_sections', [])))}",
                    f"<strong>Low-confidence mappings:</strong> {escape(len(mapping.get('low_confidence', [])))}",
                    f"<strong>Mapping conflicts:</strong> {escape(len(mapping.get('conflicts', [])))}",
                    f"<strong>Unmapped content blocks:</strong> {escape(len(mapping.get('unmapped_content', [])))}",
                ]
                if mapping_generated
                else [
                    "Mapping has not been generated yet.",
                    "Review the mapping to generate section matches and inspect gaps.",
                ]
            ),
        ),
    ]
    return (
        '<section class="ingest-stage-board" data-component="ingest-stage-board" data-surface="ingest-detail">'
        '<p class="ingest-stage-board__kicker">Import</p>'
        "<h2>Stage summary</h2>"
        '<div class="ingest-stage-board__grid">' + join_html(cards) + "</div></section>"
    )
