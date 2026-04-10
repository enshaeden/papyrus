from __future__ import annotations

import json
from typing import Any

from papyrus.domain.ingestion import IngestionStatus, has_mapping_result
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import (
    render_action_descriptor_panel,
    render_workflow_projection_panel,
    workflow_actions,
)
from papyrus.interfaces.web.rendering import TemplateRenderer
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path, render_list, slugify


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


def _progress_bar_html(renderer: TemplateRenderer, *, detail: dict[str, object]) -> str:
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
    return renderer.render(
        "partials/progress_bar.html",
        {
            "percentage": escape(percentage),
            "summary": escape(f"{len(completed_stages)} of {len(INGEST_STAGES)} ingestion stages complete"),
            "items_json": escape(json.dumps(items, ensure_ascii=True)),
        },
    )


def _ingestion_action_href(*, detail: dict[str, object], action: dict[str, object]) -> str | None:
    ingestion_id = quoted_path(str(detail["ingestion_id"]))
    action_id = str(action.get("action_id") or "")
    if action_id == "review_ingestion_mapping":
        return f"/ingest/{ingestion_id}/review"
    if action_id == "convert_ingestion_to_draft":
        return f"/ingest/{ingestion_id}/review#convert-to-draft-form"
    if action_id == "open_converted_draft" and detail.get("converted_object_id") and detail.get("converted_revision_id"):
        return (
            f"/write/objects/{quoted_path(str(detail['converted_object_id']))}/revisions/new"
            f"?revision_id={quoted_path(str(detail['converted_revision_id']))}"
        )
    return None


def _parser_assessment_panel(components: ComponentPresenter, *, detail: dict[str, object]) -> str:
    normalized = detail["normalized_content"]
    warnings = [escape(str(item)) for item in normalized.get("parser_warnings", [])]
    degradation_notes = [escape(str(item)) for item in normalized.get("degradation_notes", [])]
    extraction_quality = normalized.get("extraction_quality") or {}
    quality_state = str(extraction_quality.get("state") or "unknown")
    quality_score = float(extraction_quality.get("score") or 0.0)
    summary = str(extraction_quality.get("summary") or "No parser assessment was recorded.")
    tone = "warning" if quality_state == "degraded" or warnings or degradation_notes else "approved"
    body_parts = [
        f"<p><strong>Extraction quality:</strong> {escape(quality_state)} ({escape(round(quality_score, 2))})</p>",
        f"<p>{escape(summary)}</p>",
        "<p><strong>Parser warnings</strong></p>",
        render_list(warnings, css_class="validation-findings")
        or '<p class="empty-state-copy">No parser warnings were recorded.</p>',
        "<p><strong>Degradation notes</strong></p>",
        render_list(degradation_notes, css_class="validation-findings")
        or '<p class="empty-state-copy">No degradation notes were recorded.</p>',
    ]
    return components.surface_panel(
        title="Parser assessment",
        eyebrow="Import",
        tone=tone,
        body_html=join_html(body_parts),
        variant="parser-assessment",
        surface="ingest",
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


def _stage_summary_html(components: ComponentPresenter, *, detail: dict[str, object]) -> str:
    normalized = detail["normalized_content"]
    classification = detail["classification"]
    mapping = detail.get("mapping_result") or {}
    mapping_generated = has_mapping_result(mapping)
    extraction_quality = normalized.get("extraction_quality") or {}
    parser_warnings = normalized.get("parser_warnings") or []
    parse_tone = "warning" if str(extraction_quality.get("state") or "") == "degraded" or parser_warnings else "approved"
    stage_cards = [
        components.surface_panel(
            title="Upload",
            eyebrow="Import",
            tone="approved",
            body_html=(
                f"<p><strong>File:</strong> {escape(detail['filename'])}</p>"
                f"<p><strong>Media type:</strong> {escape(detail['media_type'])}</p>"
            ),
            variant="stage-upload",
            surface="ingest",
        ),
        components.surface_panel(
            title="Parse",
            eyebrow="Import",
            tone=parse_tone,
            body_html=(
                f"<p><strong>Parser:</strong> {escape(detail['parser_name'])}</p>"
                f"<p><strong>Headings:</strong> {escape(len(normalized.get('headings', [])))}</p>"
                f"<p><strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}</p>"
                f"<p><strong>Extraction quality:</strong> {escape(extraction_quality.get('state') or 'unknown')}</p>"
                f"<p><strong>Parser warnings:</strong> {escape(len(parser_warnings))}</p>"
            ),
            variant="stage-parse",
            surface="ingest",
        ),
        components.surface_panel(
            title="Classify",
            eyebrow="Import",
            tone="approved",
            body_html=(
                f"<p><strong>Suggested content type:</strong> {escape(classification.get('blueprint_id') or 'unknown')}</p>"
                f"<p><strong>Confidence:</strong> {escape(classification.get('confidence') or 0.0)}</p>"
            ),
            variant="stage-classify",
            surface="ingest",
        ),
        components.surface_panel(
            title="Map",
            eyebrow="Import",
            tone="warning"
            if mapping_generated and (mapping.get("missing_sections") or mapping.get("low_confidence") or mapping.get("conflicts"))
            else "approved"
            if mapping_generated
            else "default",
            body_html=(
                (
                    f"<p><strong>Missing required sections:</strong> {escape(len(mapping.get('missing_sections', [])))}</p>"
                    f"<p><strong>Low-confidence mappings:</strong> {escape(len(mapping.get('low_confidence', [])))}</p>"
                    f"<p><strong>Mapping conflicts:</strong> {escape(len(mapping.get('conflicts', [])))}</p>"
                    f"<p><strong>Unmapped content blocks:</strong> {escape(len(mapping.get('unmapped_content', [])))}</p>"
                )
                if mapping_generated
                else "<p>Mapping has not been generated yet.</p><p>Review the mapping to generate section matches and inspect gaps.</p>"
            ),
            variant="stage-map",
            surface="ingest",
        ),
    ]
    return join_html(stage_cards)


def _mapping_gaps_html(components: ComponentPresenter, *, mapping: dict[str, object]) -> str:
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
    return join_html(
        [
            components.surface_panel(
                title="Missing required sections",
                eyebrow="Review",
                tone="warning" if missing_items else "approved",
                body_html=components.list_body(
                    items=missing_items,
                    empty_label="No required blueprint sections are missing from the current mapping.",
                    css_class="validation-findings",
                ),
                variant="missing-sections",
                surface="ingest-review",
            ),
            components.surface_panel(
                title="Low-confidence mappings",
                eyebrow="Review",
                tone="warning" if low_confidence_items else "approved",
                body_html=components.list_body(
                    items=low_confidence_items,
                    empty_label="No low-confidence mappings are currently flagged.",
                    css_class="validation-findings",
                ),
                variant="low-confidence",
                surface="ingest-review",
            ),
            components.surface_panel(
                title="Mapping conflicts",
                eyebrow="Review",
                tone="warning" if conflict_items else "approved",
                body_html=components.list_body(
                    items=conflict_items,
                    empty_label="No duplicate source-fragment conflicts are currently flagged.",
                    css_class="validation-findings",
                ),
                variant="mapping-conflicts",
                surface="ingest-review",
            ),
            components.surface_panel(
                title="Unmapped content",
                eyebrow="Review",
                tone="warning" if unmapped_items else "approved",
                body_html=components.list_body(
                    items=unmapped_items,
                    empty_label="All detected content blocks are currently represented in the mapping.",
                    css_class="validation-findings",
                ),
                variant="unmapped-content",
                surface="ingest-review",
            ),
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
    rows = [
        [
            link(str(item["filename"]), f"/ingest/{quoted_path(str(item['ingestion_id']))}"),
            escape(item["ingestion_state"]),
            escape(item.get("blueprint_id") or "unclassified"),
            escape(item["updated_at"]),
            link(
                "Review import",
                f"/ingest/{quoted_path(str(item['ingestion_id']))}",
                css_class="button button-primary",
                attrs={"data-component": "action-link", "data-action-id": "review-ingestion"},
            ),
        ]
        for item in ingestions
    ]
    ingestions_html = (
        components.surface_panel(
            title="Recent imports",
            eyebrow="Import",
            body_html=components.table(
                headers=["File", "Status", "Content type", "Updated", "Next"],
                rows=rows,
                table_id="ingestion-workbench",
                surface="ingest",
            ),
            variant="ingestion-table",
            surface="ingest",
        )
        if ingestions
        else components.empty_state(
            title="No ingestions yet",
            description=(
                "Upload a Markdown, DOCX, or PDF file to start import review."
                if not allow_web_ingest_local_paths
                else "Upload a file or point to a local source file to start import review."
            ),
            surface="ingest",
        )
    )
    local_path_html = (
        forms.field(
            field_id="source_path",
            label="Local source file",
            control_html=forms.input(field_id="source_path", name="source_path", value="", placeholder="/absolute/path/to/file.md"),
            hint="Use an absolute path on this computer. Use this only in a trusted local session.",
        )
        if allow_web_ingest_local_paths
        else components.surface_panel(
            title="Local source file unavailable",
            eyebrow="Import",
            tone="context",
            body_html=(
                "<p>This session accepts uploaded files only.</p>"
                "<p>Start the app with <code>--allow-web-ingest-local-paths</code> if you intentionally want to read a file from this same computer.</p>"
            ),
            variant="local-source-unavailable",
            surface="ingest",
        )
    )
    error_html = (
        components.surface_panel(
            title="Import blockers",
            eyebrow="Validation",
            body_html=components.list_body(
                items=[escape(item) for item in errors or []],
                empty_label="",
                css_class="validation-findings",
            ),
            tone="context",
            variant="import-blockers",
            surface="ingest",
        )
        if errors
        else ""
    )
    upload_html = components.surface_panel(
        title="Upload document",
        eyebrow="Import",
        body_html=(
            error_html
            + '<form class="governed-form" method="post" enctype="multipart/form-data">'
            + forms.field(
                field_id="upload",
                label="File upload",
                control_html='<input id="upload" name="upload" type="file" accept=".md,.markdown,.docx,.pdf" data-component="form-control" data-control-type="file" />',
                hint="Upload Markdown, DOCX, or PDF. Text-based PDFs work best and may still need cleanup after import.",
            )
            + local_path_html
            + forms.button(label="Import document", action_id="start-ingestion")
            + "</form>"
        ),
        variant="upload-form",
        surface="ingest",
    )
    return {
        "page_template": "pages/ingest_list.html",
        "page_title": "Import workbench",
        "page_header": {
            "headline": "Import workbench",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": "",
        "page_context": {"upload_html": upload_html, "ingestions_html": ingestions_html},
        "page_surface": "ingest",
    }


def present_ingestion_detail_page(renderer: TemplateRenderer, *, detail: dict[str, object]) -> dict[str, Any]:
    components = ComponentPresenter(renderer)
    normalized = detail["normalized_content"]
    parsed_content_html = components.surface_panel(
        title="Parsed content",
        eyebrow="Import",
        body_html=(
            f"<p><strong>Title:</strong> {escape(normalized.get('title') or 'Untitled')}</p>"
            f"<p><strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}</p>"
            f"<p><strong>Lists:</strong> {escape(len(normalized.get('lists', [])))}</p>"
            f"<p><strong>Tables:</strong> {escape(len(normalized.get('tables', [])))}</p>"
            f"<p><strong>Links:</strong> {escape(len(normalized.get('links', [])))}</p>"
        ),
        variant="parsed-content",
        surface="ingest-detail",
    )
    aside_html = join_html(
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
            _parser_assessment_panel(components, detail=detail),
        ]
    )
    return {
        "page_template": "pages/ingest_detail.html",
        "page_title": f"Ingestion {detail['filename']}",
        "page_header": {
            "headline": detail["filename"],
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": aside_html,
        "page_context": {
            "progress_html": _progress_bar_html(renderer, detail=detail),
            "stage_html": _stage_summary_html(components, detail=detail),
            "detail_html": parsed_content_html,
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
    mapping_table_html = (
        components.table(
            headers=["Draft section", "Matched passage", "Matched heading", "Confidence", "Review state"],
            rows=section_rows,
            table_id="mapping-review",
            surface="ingest-review",
        )
        if section_rows
        else '<p class="empty-state-copy">No mapping summary available.</p>'
    )
    error_html = (
        components.surface_panel(
            title="Conversion blockers",
            eyebrow="Validation",
            body_html=components.list_body(
                items=[escape(item) for item in errors or []],
                empty_label="",
                css_class="validation-findings",
            ),
            tone="context",
            variant="conversion-blockers",
            surface="ingest-review",
        )
        if errors
        else ""
    )
    slug = slugify(str(detail["normalized_content"].get("title") or detail["filename"]))
    convert_form = components.surface_panel(
        title="Create draft",
        eyebrow="Import",
        body_html=(
            error_html
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
            + forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=""))
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
            + "</form>"
        ),
        variant="convert-form",
        surface="ingest-review",
    )
    aside_html = join_html(
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
            _parser_assessment_panel(components, detail=detail),
        ]
    )
    return {
        "page_template": "pages/ingest_mapping_review.html",
        "page_title": f"Review mapping for {detail['filename']}",
        "page_header": {
            "headline": f"Review mapping for {detail['filename']}",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        "active_nav": "import",
        "aside_html": aside_html,
        "page_context": {
            "progress_html": _progress_bar_html(renderer, detail=detail),
            "mapping_html": components.surface_panel(
                title="Mapping review",
                eyebrow="Import",
                body_html=mapping_table_html,
                variant="mapping-review",
                surface="ingest-review",
            ),
            "gaps_html": _mapping_gaps_html(components, mapping=mapping),
            "convert_html": convert_form,
        },
        "page_surface": "ingest-review",
    }
