from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.view_helpers import escape


def render_ingest_mapping_table(
    *, components: ComponentPresenter, mapping: dict[str, object]
) -> str:
    section_rows = []
    for section_id, entry in mapping.get("sections", {}).items():
        match = entry.get("match") or {}
        provenance = entry.get("provenance") or {}
        section_rows.append(
            [
                escape(section_id),
                escape(provenance.get("source_fragment_id") or "Unmapped"),
                escape(provenance.get("source_heading") or match.get("heading") or "Unmapped"),
                escape(entry.get("confidence", 0.0)),
                escape(entry.get("conflict_state") or "clear"),
            ]
        )
    body_html = (
        components.table(
            headers=[
                "Draft section",
                "Matched passage",
                "Matched heading",
                "Confidence",
                "Review state",
            ],
            rows=section_rows,
            table_id="mapping-review",
            surface="ingest-review",
        )
        if section_rows
        else '<p class="empty-state-copy">No mapping summary available.</p>'
    )
    return (
        '<section class="ingest-mapping-table" data-component="ingest-mapping-table" data-surface="ingest-review">'
        '<p class="ingest-mapping-table__kicker">Import</p>'
        "<h2>Mapping review</h2>"
        f"{body_html}</section>"
    )
