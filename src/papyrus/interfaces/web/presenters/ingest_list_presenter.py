from __future__ import annotations

from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.urls import import_detail_url
from papyrus.interfaces.web.view_helpers import escape, link


def render_ingest_list(*, components: ComponentPresenter, ingestions: list[dict[str, object]], allow_web_ingest_local_paths: bool) -> str:
    if not ingestions:
        description = (
            "Upload a Markdown, DOCX, or PDF file to start import review."
            if not allow_web_ingest_local_paths
            else "Upload a file or point to a local source file to start import review."
        )
        return (
            '<section class="ingest-list" data-component="ingest-list" data-surface="ingest">'
            '<p class="ingest-list__kicker">Import</p>'
            "<h2>Recent imports</h2>"
            f'<p class="ingest-list__empty">{escape(description)}</p></section>'
        )
    rows = [
        [
            link(str(item["filename"]), import_detail_url(str(item["ingestion_id"]))),
            escape(item["ingestion_state"]),
            escape(item.get("blueprint_id") or "unclassified"),
            escape(item["updated_at"]),
            link(
                "Review import",
                import_detail_url(str(item["ingestion_id"])),
                css_class="button button-primary",
                attrs={"data-component": "action-link", "data-action-id": "review-ingestion"},
            ),
        ]
        for item in ingestions
    ]
    return (
        '<section class="ingest-list" data-component="ingest-list" data-surface="ingest">'
        '<p class="ingest-list__kicker">Import</p>'
        "<h2>Recent imports</h2>"
        + components.table(
            headers=["File", "Status", "Content type", "Updated", "Next"],
            rows=rows,
            table_id="ingestion-workbench",
            surface="ingest",
        )
        + "</section>"
    )
