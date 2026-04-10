from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote_plus

from papyrus.application.ingestion_flow import ingest_file, ingestion_detail, list_ingestions
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.domain.ingestion import IngestionStatus, has_mapping_result
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.presenters.governed_presenter import render_action_descriptor_panel, render_workflow_projection_panel, workflow_actions
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
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


def _stage_progress_html(runtime, *, detail: dict[str, object]) -> str:
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
    return runtime.template_renderer.render(
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


def _parser_assessment_card(components, *, detail: dict[str, object]) -> str:
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
    return components.section_card(
        title="Parser assessment",
        eyebrow="Import",
        tone=tone,
        body_html=join_html(body_parts),
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


def _stage_summary_html(components, *, detail: dict[str, object]) -> str:
    normalized = detail["normalized_content"]
    classification = detail["classification"]
    mapping = detail.get("mapping_result") or {}
    mapping_generated = has_mapping_result(mapping)
    extraction_quality = normalized.get("extraction_quality") or {}
    parser_warnings = normalized.get("parser_warnings") or []
    parse_tone = "warning" if str(extraction_quality.get("state") or "") == "degraded" or parser_warnings else "approved"
    stage_cards = [
        components.section_card(
            title="Upload",
            eyebrow="Import",
            tone="approved",
            body_html=(
                f"<p><strong>File:</strong> {escape(detail['filename'])}</p>"
                f"<p><strong>Media type:</strong> {escape(detail['media_type'])}</p>"
            ),
        ),
        components.section_card(
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
        ),
        components.section_card(
            title="Classify",
            eyebrow="Import",
            tone="approved",
            body_html=(
                f"<p><strong>Suggested content type:</strong> {escape(classification.get('blueprint_id') or 'unknown')}</p>"
                f"<p><strong>Confidence:</strong> {escape(classification.get('confidence') or 0.0)}</p>"
            ),
        ),
        components.section_card(
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
        ),
    ]
    return join_html(stage_cards)


def _mapping_gaps_html(components, *, mapping: dict[str, object]) -> str:
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
            components.section_card(
                title="Missing required sections",
                eyebrow="Review",
                tone="warning" if missing_items else "approved",
                body_html=render_list(missing_items, css_class="validation-findings")
                or '<p class="empty-state-copy">No required blueprint sections are missing from the current mapping.</p>',
            ),
            components.section_card(
                title="Low-confidence mappings",
                eyebrow="Review",
                tone="warning" if low_confidence_items else "approved",
                body_html=render_list(low_confidence_items, css_class="validation-findings")
                or '<p class="empty-state-copy">No low-confidence mappings are currently flagged.</p>',
            ),
            components.section_card(
                title="Mapping conflicts",
                eyebrow="Review",
                tone="warning" if conflict_items else "approved",
                body_html=render_list(conflict_items, css_class="validation-findings")
                or '<p class="empty-state-copy">No duplicate source-fragment conflicts are currently flagged.</p>',
            ),
            components.section_card(
                title="Unmapped content",
                eyebrow="Review",
                tone="warning" if unmapped_items else "approved",
                body_html=render_list(unmapped_items, css_class="validation-findings")
                or '<p class="empty-state-copy">All detected content blocks are currently represented in the mapping.</p>',
            ),
        ]
    )


def _ingest_list_page(runtime, *, request: Request, errors: list[str] | None = None) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    forms = FormPresenter(runtime.template_renderer)
    ingestions = list_ingestions(database_path=runtime.database_path)
    rows = "".join(
        (
            f'<tr><td>{link(item["filename"], f"/ingest/{quoted_path(item["ingestion_id"])}")}</td>'
            f"<td>{escape(item['ingestion_state'])}</td>"
            f"<td>{escape(item.get('blueprint_id') or 'unclassified')}</td>"
            f"<td>{escape(item['updated_at'])}</td>"
            f'<td>{link("Review import", f"/ingest/{quoted_path(item["ingestion_id"])}", css_class="button button-primary")}</td></tr>'
        )
        for item in ingestions
    )
    table_html = (
        f'<table class="data-table"><thead><tr><th>File</th><th>Status</th><th>Content type</th><th>Updated</th><th>Next</th></tr></thead><tbody>{rows}</tbody></table>'
        if ingestions
        else components.empty_state(
            title="No ingestions yet",
            description=(
                "Upload a Markdown, DOCX, or PDF file to start import review."
                if not runtime.allow_web_ingest_local_paths
                else "Upload a file or point to a local source file to start import review."
            ),
        )
    )
    local_path_html = (
        forms.field(
            field_id="source_path",
            label="Local source file",
            control_html=forms.input(field_id="source_path", name="source_path", value="", placeholder="/absolute/path/to/file.md"),
            hint="Use an absolute path on this computer. Use this only in a trusted local session.",
        )
        if runtime.allow_web_ingest_local_paths
        else components.section_card(
            title="Local source file unavailable",
            eyebrow="Import",
            tone="context",
            body_html=(
                "<p>This session accepts uploaded files only.</p>"
                "<p>Start the app with <code>--allow-web-ingest-local-paths</code> if you intentionally want to read a file from this same computer.</p>"
            ),
        )
    )
    error_html = (
        components.validation_summary(title="Import blockers", findings=[escape(item) for item in errors or []], empty_label="")
        if errors
        else ""
    )
    upload_html = components.section_card(
        title="Upload document",
        eyebrow="Import",
        body_html=(
            error_html
            + 
            '<form class="governed-form" method="post" enctype="multipart/form-data">'
            + forms.field(
                field_id="upload",
                label="File upload",
                control_html='<input id="upload" name="upload" type="file" accept=".md,.markdown,.docx,.pdf" />',
                hint="Upload Markdown, DOCX, or PDF. Text-based PDFs work best and may still need cleanup after import.",
            )
            + local_path_html
            + forms.button(label="Import document")
            + "</form>"
        ),
    )
    return runtime.page_renderer.render_page(
        page_template="pages/ingest_list.html",
        page_title="Import workbench",
        page_header={
            "headline": "Import workbench",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html="",
        page_context={"upload_html": upload_html, "ingestions_html": table_html},
    )


def _ingestion_detail_page(runtime, *, request: Request, detail: dict[str, object]) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    normalized = detail["normalized_content"]
    content_html = components.section_card(
        title="Parsed content",
        eyebrow="Import",
        body_html=(
            f"<p><strong>Title:</strong> {escape(normalized.get('title') or 'Untitled')}</p>"
            f"<p><strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}</p>"
            f"<p><strong>Lists:</strong> {escape(len(normalized.get('lists', [])))}</p>"
            f"<p><strong>Tables:</strong> {escape(len(normalized.get('tables', [])))}</p>"
            f"<p><strong>Links:</strong> {escape(len(normalized.get('links', [])))}</p>"
        ),
    )
    return runtime.page_renderer.render_page(
        page_template="pages/ingest_detail.html",
        page_title=f"Ingestion {detail['filename']}",
        page_header={
            "headline": detail["filename"],
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html=join_html(
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
                _parser_assessment_card(components, detail=detail),
            ]
        ),
        page_context={
            "progress_html": _stage_progress_html(runtime, detail=detail),
            "stage_html": _stage_summary_html(components, detail=detail),
            "detail_html": content_html,
        },
    )


def _mapping_review_page(runtime, *, request: Request, detail: dict[str, object], mapping: dict[str, object], errors: list[str] | None = None) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    forms = FormPresenter(runtime.template_renderer)
    section_rows = []
    for section_id, entry in mapping.get("sections", {}).items():
        match = entry.get("match") or {}
        provenance = entry.get("provenance") or {}
        section_rows.append(
            "<tr>"
            f"<td>{escape(section_id)}</td>"
            f"<td>{escape(provenance.get('source_fragment_id') or 'Unmapped')}</td>"
            f"<td>{escape(provenance.get('source_heading') or match.get('heading') or 'Unmapped')}</td>"
            f"<td>{escape(entry.get('confidence', 0.0))}</td>"
            f"<td>{escape(entry.get('conflict_state') or 'clear')}</td>"
            "</tr>"
        )
    mapping_table = (
        f'<table class="data-table"><thead><tr><th>Draft section</th><th>Matched passage</th><th>Matched heading</th><th>Confidence</th><th>Review state</th></tr></thead><tbody>{"".join(section_rows)}</tbody></table>'
        if section_rows
        else '<p class="empty-state-copy">No mapping summary available.</p>'
    )
    error_html = (
        components.validation_summary(title="Conversion blockers", findings=[escape(item) for item in errors or []], empty_label="")
        if errors
        else ""
    )
    convert_form = components.section_card(
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
                    options=runtime.taxonomies["teams"]["allowed_values"],
                ),
            )
            + forms.field(
                field_id="review_cadence",
                label="Review cadence",
                control_html=forms.select(
                    field_id="review_cadence",
                    name="review_cadence",
                    value="",
                    options=runtime.taxonomies["review_cadences"]["allowed_values"],
                ),
            )
            + forms.field(
                field_id="status",
                label="Status",
                control_html=forms.select(
                    field_id="status",
                    name="status",
                    value="draft",
                    options=runtime.taxonomies["statuses"]["allowed_values"],
                ),
            )
            + forms.field(
                field_id="audience",
                label="Audience",
                control_html=forms.select(
                    field_id="audience",
                    name="audience",
                    value="",
                    options=runtime.taxonomies["audiences"]["allowed_values"],
                ),
            )
            + '<section class="form-section"><h3>Publishing details</h3><p class="section-intro">Keep the new draft traceable and ready to publish.</p>'
            + forms.field(
                field_id="object_id",
                label="Reference code",
                control_html=forms.input(
                    field_id="object_id",
                    name="object_id",
                    value=f"kb-{slugify(str(detail['normalized_content'].get('title') or detail['filename']))}",
                ),
                hint="Use lowercase words separated by hyphens. This stays with the guidance in links and search.",
            )
            + forms.field(
                field_id="canonical_path",
                label="Publishing location",
                control_html=forms.input(
                    field_id="canonical_path",
                    name="canonical_path",
                    value=f"knowledge/imported/{slugify(str(detail['normalized_content'].get('title') or detail['filename']))}.md",
                ),
                hint="Where the published source will live in the knowledge library.",
            )
            + "</section>"
            + forms.button(label="Create draft")
            + "</form>"
        ),
    )
    return runtime.page_renderer.render_page(
        page_template="pages/ingest_mapping_review.html",
        page_title=f"Review mapping for {detail['filename']}",
        page_header={
            "headline": f"Review mapping for {detail['filename']}",
            "show_actor_banner": True,
            "show_actor_links": True,
        },
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html=join_html(
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
                _parser_assessment_card(components, detail=detail),
            ]
        ),
        page_context={
            "progress_html": _stage_progress_html(runtime, detail=detail),
            "mapping_html": components.section_card(title="Mapping review", eyebrow="Import", body_html=mapping_table),
            "gaps_html": _mapping_gaps_html(components, mapping=mapping),
            "convert_html": convert_form,
        },
    )


def register(router, runtime) -> None:
    def ingest_list_page(request: Request):
        errors: list[str] = []
        if request.method == "POST":
            upload = request.uploaded_file("upload")
            source_path = request.form_value("source_path").strip()
            if upload is not None and source_path:
                errors.append("Choose either a file upload or a local source file, not both.")
            elif upload is None and not source_path:
                errors.append(
                    "Select a file upload before starting ingestion."
                    if not runtime.allow_web_ingest_local_paths
                    else "Select a file upload or provide a local source file before starting import."
                )
            elif upload is None and source_path and not runtime.allow_web_ingest_local_paths:
                errors.append("Local source file import is unavailable in this session.")
            else:
                try:
                    result = (
                        ingest_file(
                            file_path=upload.filename,
                            payload=upload.body,
                            database_path=runtime.database_path,
                            source_root=runtime.source_root,
                        )
                        if upload is not None
                        else ingest_file(
                            file_path=source_path.strip(),
                            database_path=runtime.database_path,
                            source_root=runtime.source_root,
                        )
                    )
                    return redirect_response(
                        f"/ingest/{quoted_path(result['ingestion_id'])}?notice={quote_plus('Import started. Review the mapping before creating the draft.')}"
                    )
                except ValueError as exc:
                    errors.append(str(exc))
        return html_response(_ingest_list_page(runtime, request=request, errors=errors))

    def ingest_detail_page(request: Request):
        detail = ingestion_detail(ingestion_id=request.route_value("ingestion_id"), database_path=runtime.database_path)
        return html_response(_ingestion_detail_page(runtime, request=request, detail=detail))

    def ingest_review_page(request: Request):
        ingestion_id = request.route_value("ingestion_id")
        detail = ingestion_detail(ingestion_id=ingestion_id, database_path=runtime.database_path)
        existing_mapping = detail.get("mapping_result") if has_mapping_result(detail.get("mapping_result")) else None
        mapping = existing_mapping or map_to_blueprint(
            ingestion_id=ingestion_id,
            blueprint_id=detail.get("blueprint_id") or detail["classification"]["blueprint_id"],
            database_path=runtime.database_path,
        )
        if existing_mapping is None:
            detail = ingestion_detail(ingestion_id=ingestion_id, database_path=runtime.database_path)
        errors: list[str] = []
        if request.method == "POST":
            required_fields = ["object_id", "title", "canonical_path", "owner", "team", "review_cadence", "status", "audience"]
            missing = [field for field in required_fields if not request.form_value(field).strip()]
            if missing:
                field_labels = {
                    "object_id": "Reference code",
                    "title": "Title",
                    "canonical_path": "Publishing location",
                    "owner": "Owner",
                    "team": "Team",
                    "review_cadence": "Review cadence",
                    "status": "Status",
                    "audience": "Audience",
                }
                errors = [f"{field_labels[field]} is required." for field in missing]
            else:
                converted = convert_to_draft(
                    ingestion_id=ingestion_id,
                    object_id=request.form_value("object_id").strip(),
                    title=request.form_value("title").strip(),
                    canonical_path=request.form_value("canonical_path").strip(),
                    owner=request.form_value("owner").strip(),
                    team=request.form_value("team").strip(),
                    review_cadence=request.form_value("review_cadence").strip(),
                    status=request.form_value("status").strip(),
                    audience=request.form_value("audience").strip(),
                    actor=actor_for_request(request),
                    database_path=runtime.database_path,
                    source_root=runtime.source_root,
                )
                return redirect_response(
                    f"/write/objects/{quoted_path(converted['object_id'])}/revisions/new?revision_id={quoted_path(converted['revision_id'])}&notice={quote_plus('Draft created from the imported document.')}"
                )
        return html_response(_mapping_review_page(runtime, request=request, detail=detail, mapping=mapping, errors=errors))

    router.add(["GET", "POST"], "/ingest", ingest_list_page)
    router.add(["GET"], "/ingest/{ingestion_id}", ingest_detail_page)
    router.add(["GET", "POST"], "/ingest/{ingestion_id}/review", ingest_review_page)
