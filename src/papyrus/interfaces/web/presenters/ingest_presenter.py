from __future__ import annotations

import json
from typing import Any

from papyrus.application.blueprint_registry import (
    ADVANCED_AUTHORING_SCOPE,
    blueprint_label,
    get_blueprint,
)
from papyrus.domain.ingestion import IngestionStatus, has_mapping_result
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    render_action_descriptor_panel,
    render_workflow_projection_panel,
    workflow_actions,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.urls import import_detail_url, import_review_url, write_object_url
from papyrus.interfaces.web.view_helpers import escape, join_html, link, render_list, slugify


def _blueprint_target_label(blueprint_id: str | None, *, include_scope_note: bool = False) -> str:
    if not str(blueprint_id or "").strip():
        return "Unclassified"
    try:
        return blueprint_label(str(blueprint_id), include_scope_note=include_scope_note)
    except ValueError:
        return str(blueprint_id)


def _advanced_blueprint_notice(blueprint_id: str | None) -> str:
    if not str(blueprint_id or "").strip():
        return ""
    try:
        blueprint = get_blueprint(str(blueprint_id))
    except ValueError:
        return ""
    if blueprint.authoring_scope != ADVANCED_AUTHORING_SCOPE:
        return ""
    return (
        "This document maps to an advanced/deferred blueprint target. "
        "The primary visible template set remains runbooks, known errors, and service records."
    )


def render_ingest_upload(
    *,
    components: ComponentPresenter,
    forms: FormPresenter,
    errors: list[str] | None,
    allow_web_ingest_local_paths: bool,
) -> str:
    del components
    local_path_html = (
        forms.field(
            field_id="source_path",
            label="Local source file",
            control_html=forms.input(
                field_id="source_path",
                name="source_path",
                value="",
                placeholder="/absolute/path/to/file.md",
            ),
            hint="Use an absolute path on this computer. Use this only in a trusted local session.",
        )
        if allow_web_ingest_local_paths
        else (
            '<div class="ingest-upload__notice">'
            "<p><strong>Local source file unavailable</strong></p>"
            "<p>This session accepts uploaded files only.</p>"
            "<p>Start the app with <code>--allow-web-ingest-local-paths</code> if you intentionally want to read a file from this same computer.</p>"
            "</div>"
        )
    )
    error_html = (
        '<div class="ingest-upload__errors">'
        + "".join(f"<p>{escape(item)}</p>" for item in errors or [])
        + "</div>"
        if errors
        else ""
    )
    return (
        '<section class="ingest-upload" data-component="ingest-upload" data-surface="ingest">'
        '<p class="ingest-upload__kicker">Import</p>'
        "<h2>Upload document for review</h2>"
        f"{error_html}"
        '<form class="governed-form" method="post" enctype="multipart/form-data">'
        + forms.field(
            field_id="upload",
            label="File upload",
            control_html='<input id="upload" name="upload" type="file" accept=".md,.markdown,.docx,.pdf" data-component="form-control" data-control-type="file" />',
            hint="Upload Markdown, DOCX, or PDF. Text-based PDFs work best and may still need cleanup after import.",
        )
        + local_path_html
        + forms.button(label="Import document", action_id="start-ingestion")
        + "</form></section>"
    )


def render_ingest_list(
    *,
    components: ComponentPresenter,
    ingestions: list[dict[str, object]],
    allow_web_ingest_local_paths: bool,
) -> str:
    if not ingestions:
        description = (
            "Upload a Markdown, DOCX, or PDF file to start import-to-draft review."
            if not allow_web_ingest_local_paths
            else "Upload a file or point to a local source file to start import-to-draft review."
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
            escape(_blueprint_target_label(item.get("blueprint_id"), include_scope_note=True)),
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


INGEST_STAGES = ("upload", "parse", "classify", "map", "review", "convert")


def _completed_stages(detail: dict[str, object]) -> set[str]:
    status = IngestionStatus(str(detail.get("ingestion_state") or IngestionStatus.UPLOADED.value))
    completed: set[str] = {"upload"}
    if status in {
        IngestionStatus.PARSED,
        IngestionStatus.CLASSIFIED,
        IngestionStatus.MAPPED,
        IngestionStatus.CONVERTED,
    }:
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


def render_ingest_progress(
    renderer: TemplateRenderer, *, detail: dict[str, object], surface: str
) -> str:
    items = []
    current_stage = _current_stage(detail)
    completed_stages = _completed_stages(detail)
    for stage in INGEST_STAGES:
        items.append(
            {
                "label": stage.replace("_", " ").title(),
                "state": "complete"
                if stage in completed_stages
                else "current"
                if stage == current_stage
                else "upcoming",
                "required": True,
            }
        )
    percentage = int((len(completed_stages) / len(INGEST_STAGES)) * 100)
    progress_html = renderer.render(
        "partials/progress_bar.html",
        {
            "percentage": escape(percentage),
            "summary": escape(
                f"{len(completed_stages)} of {len(INGEST_STAGES)} ingestion stages complete"
            ),
            "items_json": escape(json.dumps(items, ensure_ascii=True)),
        },
    )
    return (
        f'<section class="ingest-progress" data-component="ingest-progress" data-surface="{escape(surface)}">'
        '<p class="ingest-progress__kicker">Import</p>'
        "<h2>Ingestion progress</h2>"
        f"{progress_html}</section>"
    )


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
                "<strong>Suggested content type:</strong> "
                + escape(
                    _blueprint_target_label(
                        classification.get("blueprint_id"), include_scope_note=True
                    )
                ),
                f"<strong>Confidence:</strong> {escape(classification.get('confidence') or 0.0)}",
                (
                    f"<strong>Authoring path:</strong> {escape(_advanced_blueprint_notice(classification.get('blueprint_id')))}"
                    if _advanced_blueprint_notice(classification.get("blueprint_id"))
                    else "<strong>Authoring path:</strong> Primary template set"
                ),
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


def render_ingest_convert_form(
    *,
    forms: FormPresenter,
    detail: dict[str, object],
    errors: list[str] | None,
    taxonomies: dict[str, Any],
) -> str:
    error_html = (
        '<div class="ingest-convert-form__errors">'
        + "".join(f"<p>{escape(item)}</p>" for item in errors or [])
        + "</div>"
        if errors
        else ""
    )
    slug = slugify(str(detail["normalized_content"].get("title") or detail["filename"]))
    target_blueprint_id = str(
        detail.get("blueprint_id")
        or (detail.get("classification") or {}).get("blueprint_id")
        or ""
    )
    target_blueprint_label = _blueprint_target_label(
        target_blueprint_id, include_scope_note=True
    )
    target_notice = _advanced_blueprint_notice(target_blueprint_id)
    return (
        '<section class="ingest-convert-form" data-component="ingest-convert-form" data-surface="ingest-review">'
        + '<p class="ingest-convert-form__kicker">Import</p>'
        + "<h2>Create draft</h2>"
        + f"{error_html}"
        + f"<p><strong>Mapped target:</strong> {escape(target_blueprint_label)}</p>"
        + (f"<p>{escape(target_notice)}</p>" if target_notice else "")
        + '<form id="convert-to-draft-form" class="governed-form" method="post">'
        + forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(
                field_id="title",
                name="title",
                value=str(detail["normalized_content"].get("title") or detail["filename"]),
            ),
        )
        + forms.field(
            field_id="owner",
            label="Owner",
            control_html=forms.input(field_id="owner", name="owner", value=""),
        )
        + forms.field(
            field_id="team",
            label="Team",
            control_html=forms.select(
                field_id="team",
                name="team",
                value="",
                options=taxonomies["teams"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(
                field_id="review_cadence",
                name="review_cadence",
                value="",
                options=taxonomies["review_cadences"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="status",
            label="Status",
            control_html=forms.select(
                field_id="status",
                name="status",
                value="draft",
                options=taxonomies["statuses"]["allowed_values"],
            ),
        )
        + forms.field(
            field_id="audience",
            label="Audience",
            control_html=forms.select(
                field_id="audience",
                name="audience",
                value="",
                options=taxonomies["audiences"]["allowed_values"],
            ),
        )
        + '<section class="form-section"><h3>Publishing details</h3><p class="section-intro">Keep the new draft traceable and ready to publish.</p>'
        + forms.field(
            field_id="object_id",
            label="Reference code",
            control_html=forms.input(
                field_id="object_id",
                name="object_id",
                value=f"kb-{slug}",
            ),
            hint="Use lowercase words separated by hyphens. This stays with the guidance in links and search.",
        )
        + forms.field(
            field_id="canonical_path",
            label="Publishing location",
            control_html=forms.input(
                field_id="canonical_path",
                name="canonical_path",
                value=f"knowledge/imported/{slug}.md",
            ),
            hint="Where the published source will live in the knowledge library.",
        )
        + "</section>"
        + forms.button(label="Create draft", action_id="convert_ingestion_to_draft")
        + "</form></section>"
    )


def _ingestion_action_href(*, detail: dict[str, object], action: dict[str, object]) -> str | None:
    action_id = str(action.get("action_id") or "")
    if action_id == "review_ingestion_mapping":
        return import_review_url(str(detail["ingestion_id"]))
    if action_id == "convert_ingestion_to_draft":
        return import_review_url(str(detail["ingestion_id"])) + "#convert-to-draft-form"
    if (
        action_id == "open_converted_draft"
        and detail.get("converted_object_id")
        and detail.get("converted_revision_id")
    ):
        return write_object_url(
            str(detail["converted_object_id"]),
            revision_id=str(detail["converted_revision_id"]),
        )
    return None


def _ingest_aside_html(
    components: ComponentPresenter, *, detail: dict[str, object], surface: str
) -> str:
    return join_html(
        [
            render_workflow_projection_panel(
                components,
                title="Import workflow contract",
                projection=detail.get("workflow_projection"),
            ),
            render_action_descriptor_panel(
                components,
                title="Import workflow actions",
                actions=workflow_actions(detail.get("workflow_projection")),
                href_resolver=lambda action: _ingestion_action_href(detail=detail, action=action),
            ),
            render_ingest_parser_assessment(detail=detail, surface=surface),
        ]
    )


def present_ingest_list_page(
    renderer: TemplateRenderer,
    *,
    ingestions: list[dict[str, object]],
    errors: list[str] | None,
    allow_web_ingest_local_paths: bool,
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    forms = FormPresenter(renderer)
    return {
        "page_template": "pages/ingest_list.html",
        "page_title": "Import",
        "page_header": {
            "headline": "Import",
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": "",
        "page_context": {
            "upload_html": render_ingest_upload(
                components=components,
                forms=forms,
                errors=errors,
                allow_web_ingest_local_paths=allow_web_ingest_local_paths,
            ),
            "ingestions_html": render_ingest_list(
                components=components,
                ingestions=ingestions,
                allow_web_ingest_local_paths=allow_web_ingest_local_paths,
            ),
        },
        "page_surface": "ingest",
    }


def present_ingestion_detail_page(
    renderer: TemplateRenderer, *, detail: dict[str, object]
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    return {
        "page_template": "pages/ingest_detail.html",
        "page_title": f"Ingestion {detail['filename']}",
        "page_header": {
            "headline": detail["filename"],
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": _ingest_aside_html(components, detail=detail, surface="ingest-detail"),
        "page_context": {
            "progress_html": render_ingest_progress(
                renderer, detail=detail, surface="ingest-detail"
            ),
            "stage_html": render_ingest_stage_board(detail=detail),
            "detail_html": render_ingest_parsed_content(
                normalized=detail["normalized_content"], surface="ingest-detail"
            ),
        },
        "page_surface": "ingest-detail",
    }


def present_mapping_review_page(
    renderer: TemplateRenderer,
    *,
    detail: dict[str, object],
    mapping: dict[str, object],
    errors: list[str] | None,
    taxonomies: dict[str, Any],
) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    forms = FormPresenter(renderer)
    return {
        "page_template": "pages/ingest_mapping_review.html",
        "page_title": f"Review mapping for {detail['filename']}",
        "page_header": {
            "headline": f"Review mapping for {detail['filename']}",
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": _ingest_aside_html(components, detail=detail, surface="ingest-review"),
        "page_context": {
            "progress_html": render_ingest_progress(
                renderer, detail=detail, surface="ingest-review"
            ),
            "mapping_html": render_ingest_mapping_table(components=components, mapping=mapping),
            "gaps_html": render_ingest_mapping_gaps(mapping=mapping),
            "convert_html": render_ingest_convert_form(
                forms=forms,
                detail=detail,
                errors=errors,
                taxonomies=taxonomies,
            ),
        },
        "page_surface": "ingest-review",
    }
