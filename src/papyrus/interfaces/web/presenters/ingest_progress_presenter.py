from __future__ import annotations

import json

from papyrus.domain.ingestion import IngestionStatus
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape


INGEST_STAGES = ("upload", "parse", "classify", "map", "review", "convert")


def _completed_stages(detail: dict[str, object]) -> set[str]:
    status = IngestionStatus(str(detail.get("ingestion_state") or IngestionStatus.UPLOADED.value))
    completed: set[str] = {"upload"}
    if status in {IngestionStatus.PARSED, IngestionStatus.CLASSIFIED, IngestionStatus.MAPPED, IngestionStatus.CONVERTED}:
        completed.add("parse")
    if status in {IngestionStatus.CLASSIFIED, IngestionStatus.MAPPED, IngestionStatus.CONVERTED}:
        completed.add("classify")
    if status in {IngestionStatus.MAPPED, IngestionStatus.CONVERTED}:
        completed.add("map")
    if status == IngestionStatus.CONVERTED:
        completed.update({"review", "convert"})
    return completed


def _current_stage(detail: dict[str, object]) -> str:
    if detail.get("converted_revision_id"):
        return ""
    status = str(detail.get("ingestion_state") or "")
    if status == "mapped":
        return "review"
    if status == "classified":
        return "map"
    if status == "parsed":
        return "classify"
    if status == "uploaded":
        return "parse"
    return "upload"


def render_ingest_progress(renderer: TemplateRenderer, *, detail: dict[str, object], surface: str) -> str:
    items = []
    current_stage = _current_stage(detail)
    completed_stages = _completed_stages(detail)
    for stage in INGEST_STAGES:
        items.append(
            {
                "label": stage.replace("_", " ").title(),
                "state": "complete" if stage in completed_stages else "current" if stage == current_stage else "upcoming",
                "required": True,
            }
        )
    percentage = int((len(completed_stages) / len(INGEST_STAGES)) * 100)
    progress_html = renderer.render(
        "partials/progress_bar.html",
        {
            "percentage": escape(percentage),
            "summary": escape(f"{len(completed_stages)} of {len(INGEST_STAGES)} ingestion stages complete"),
            "items_json": escape(json.dumps(items, ensure_ascii=True)),
        },
    )
    return (
        f'<section class="ingest-progress" data-component="ingest-progress" data-surface="{escape(surface)}">'
        '<p class="ingest-progress__kicker">Import</p>'
        "<h2>Ingestion progress</h2>"
        f"{progress_html}</section>"
    )
