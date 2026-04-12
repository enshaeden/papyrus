from __future__ import annotations

from papyrus.interfaces.web.view_helpers import escape, join_html


def _fragment_heading_path(item: dict[str, object]) -> str:
    heading_path = item.get("heading_path")
    if isinstance(heading_path, list):
        parts = [
            str(entry.get("text") or "").strip()
            for entry in heading_path
            if isinstance(entry, dict) and str(entry.get("text") or "").strip()
        ]
        if parts:
            return " > ".join(parts)
    return str(item.get("heading") or "Unlabeled").strip() or "Unlabeled"


def _fragment_preview(item: dict[str, object]) -> str:
    fragment_id = str(item.get("fragment_id") or "unknown-fragment")
    kind = str(item.get("kind") or "fragment")
    heading = _fragment_heading_path(item)
    text = str(item.get("text") or "")
    return f"{fragment_id} ({kind}) under {heading}: {text[:160]}"


def _gap_block(*, title: str, tone: str, items: list[str], empty_label: str) -> str:
    body_html = (
        '<ul class="validation-findings">'
        + join_html([f"<li>{item}</li>" for item in items])
        + "</ul>"
        if items
        else f'<p class="empty-state-copy">{escape(empty_label)}</p>'
    )
    return (
        f'<article class="ingest-mapping-gaps__block tone-{escape(tone)}" data-component="ingest-mapping-gap" data-surface="ingest-review">'
        f"<h3>{escape(title)}</h3>"
        f"{body_html}</article>"
    )


def render_ingest_mapping_gaps(*, mapping: dict[str, object]) -> str:
    missing_items = [escape(str(item)) for item in mapping.get("missing_sections", [])]
    low_confidence_items = [
        escape(
            f"{item.get('section_id')}: confidence {item.get('confidence')} from "
            f"{item.get('source_fragment_id') or 'unknown fragment'} under {item.get('source_heading') or 'Unlabeled'}"
        )
        for item in mapping.get("low_confidence", [])
    ]
    conflict_items = []
    for item in mapping.get("conflicts", []):
        competitors = ", ".join(
            f"{entry.get('section_id')} ({entry.get('confidence')}, {entry.get('outcome')})"
            for entry in item.get("competing_sections", [])
        )
        conflict_items.append(
            escape(
                f"{item.get('source_fragment_id')} under {item.get('source_heading') or 'Unlabeled'} "
                f"was resolved to {item.get('assigned_section_id') or 'no section'}; contenders: {competitors}"
            )
        )
    unmapped_items = []
    for item in mapping.get("unmapped_content", [])[:8]:
        if isinstance(item, dict):
            unmapped_items.append(escape(_fragment_preview(item)))
    return (
        '<section class="ingest-mapping-gaps" data-component="ingest-mapping-gaps" data-surface="ingest-review">'
        '<p class="ingest-mapping-gaps__kicker">Review</p>'
        "<h2>Mapping gaps</h2>"
        '<div class="ingest-mapping-gaps__grid">'
        + _gap_block(
            title="Missing required sections",
            tone="warning" if missing_items else "approved",
            items=missing_items,
            empty_label="No required blueprint sections are missing from the current mapping.",
        )
        + _gap_block(
            title="Low-confidence mappings",
            tone="warning" if low_confidence_items else "approved",
            items=low_confidence_items,
            empty_label="No low-confidence mappings are currently flagged.",
        )
        + _gap_block(
            title="Mapping conflicts",
            tone="warning" if conflict_items else "approved",
            items=conflict_items,
            empty_label="No duplicate source-fragment conflicts are currently flagged.",
        )
        + _gap_block(
            title="Unmapped content",
            tone="warning" if unmapped_items else "approved",
            items=unmapped_items,
            empty_label="All detected content blocks are currently represented in the mapping.",
        )
        + "</div></section>"
    )
