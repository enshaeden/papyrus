from __future__ import annotations

import json
from urllib.parse import quote_plus

from papyrus.application.ingestion_flow import ingest_file, ingestion_detail, list_ingestions
from papyrus.application.mapping_flow import convert_to_draft, map_to_blueprint
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.route_utils import actor_for_request, flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, join_html, link, quoted_path, render_list, slugify


INGEST_STAGES = ("upload", "parse", "classify", "map", "review", "convert")


def _current_stage(detail: dict[str, object]) -> str:
    if detail.get("converted_revision_id"):
        return "convert"
    status = str(detail.get("status") or "")
    if status == "reviewed":
        return "review"
    if status == "mapped":
        return "review"
    if status == "classified":
        return "classify"
    if status == "parsed":
        return "parse"
    return "upload"


def _stage_progress_html(runtime, *, detail: dict[str, object]) -> str:
    items = []
    current_stage = _current_stage(detail)
    current_index = INGEST_STAGES.index(current_stage) if current_stage in INGEST_STAGES else 0
    for index, stage in enumerate(INGEST_STAGES):
        items.append(
            {
                "label": stage.replace("_", " ").title(),
                "state": "complete" if index < current_index else "current" if index == current_index else "upcoming",
                "required": True,
            }
        )
    percentage = int(((current_index + 1) / len(INGEST_STAGES)) * 100)
    return runtime.template_renderer.render(
        "partials/progress_bar.html",
        {
            "percentage": escape(percentage),
            "summary": escape(f"{current_index + 1} of {len(INGEST_STAGES)} ingestion stages complete"),
            "items_json": escape(json.dumps(items, ensure_ascii=True)),
        },
    )


def _stage_summary_html(components, *, detail: dict[str, object]) -> str:
    normalized = detail["normalized_content"]
    classification = detail["classification"]
    mapping = detail.get("mapping_result") or {}
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
            tone="approved",
            body_html=(
                f"<p><strong>Parser:</strong> {escape(detail['parser_name'])}</p>"
                f"<p><strong>Headings:</strong> {escape(len(normalized.get('headings', [])))}</p>"
                f"<p><strong>Paragraphs:</strong> {escape(len(normalized.get('paragraphs', [])))}</p>"
            ),
        ),
        components.section_card(
            title="Classify",
            eyebrow="Import",
            tone="approved",
            body_html=(
                f"<p><strong>Suggested blueprint:</strong> {escape(classification.get('blueprint_id') or 'unknown')}</p>"
                f"<p><strong>Confidence:</strong> {escape(classification.get('confidence') or 0.0)}</p>"
            ),
        ),
        components.section_card(
            title="Map",
            eyebrow="Import",
            tone="warning" if mapping.get("missing_sections") or mapping.get("low_confidence") else "approved",
            body_html=(
                f"<p><strong>Missing required sections:</strong> {escape(len(mapping.get('missing_sections', [])))}</p>"
                f"<p><strong>Low-confidence mappings:</strong> {escape(len(mapping.get('low_confidence', [])))}</p>"
                f"<p><strong>Unmapped content blocks:</strong> {escape(len(mapping.get('unmapped_content', [])))}</p>"
            ),
        ),
    ]
    return join_html(stage_cards)


def _mapping_gaps_html(components, *, mapping: dict[str, object]) -> str:
    missing_items = [escape(str(item)) for item in mapping.get("missing_sections", [])]
    low_confidence_items = [
        escape(f"{item.get('section_id')}: confidence {item.get('confidence')}")
        for item in mapping.get("low_confidence", [])
    ]
    unmapped_items = []
    for item in mapping.get("unmapped_content", [])[:8]:
        heading = str(item.get("heading") or "Unlabeled")
        content = item.get("content")
        if isinstance(content, list):
            preview = "; ".join(str(entry) for entry in content[:2])
        else:
            preview = str(content or "")
        unmapped_items.append(escape(f"{heading}: {preview[:160]}"))
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
            f"<td>{escape(item['status'])}</td>"
            f"<td>{escape(item.get('blueprint_id') or 'unclassified')}</td>"
            f"<td>{escape(item['updated_at'])}</td>"
            f'<td>{link("Open", f"/ingest/{quoted_path(item["ingestion_id"])}", css_class="button button-secondary")}</td></tr>'
        )
        for item in ingestions
    )
    table_html = (
        f'<table class="data-table"><thead><tr><th>File</th><th>Status</th><th>Blueprint</th><th>Updated</th><th>Next</th></tr></thead><tbody>{rows}</tbody></table>'
        if ingestions
        else components.empty_state(
            title="No ingestions yet",
            description="Upload or point Papyrus at a local Markdown, DOCX, or PDF file to start a governed import review.",
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
                hint="Papyrus parses Markdown, DOCX, and PDF locally.",
            )
            + forms.field(
                field_id="source_path",
                label="Local file path",
                control_html=forms.input(field_id="source_path", name="source_path", value="", placeholder="/path/to/file.md"),
                hint="Fallback for environments where browser upload is inconvenient.",
            )
            + forms.button(label="Start ingestion")
            + "</form>"
        ),
    )
    return runtime.page_renderer.render_page(
        page_template="pages/ingest_list.html",
        page_title="Import workbench",
        headline="Import Workbench",
        kicker="Import",
        intro="Upload, parse, classify, map, review, and convert external documents into governed drafts without skipping review.",
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html=components.section_card(
            title="Next action",
            eyebrow="Guidance",
            body_html="<p>Every import stays non-canonical until a human reviews the mapping and explicitly converts it into a draft.</p>",
        ),
        page_context={"upload_html": upload_html, "ingestions_html": table_html},
    )


def _ingestion_detail_page(runtime, *, request: Request, detail: dict[str, object]) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    mapping = detail.get("mapping_result") or {}
    mapping_summary = components.section_card(
        title="Mapping summary",
        eyebrow="Import",
        body_html=(
            f"<p><strong>Suggested blueprint:</strong> {escape(detail.get('blueprint_id') or detail['classification']['blueprint_id'])}</p>"
            f"<p><strong>Low-confidence mappings:</strong> {escape(len(mapping.get('low_confidence', [])))}</p>"
            f"<p><strong>Missing required sections:</strong> {escape(len(mapping.get('missing_sections', [])))}</p>"
        )
        + f'<p>{link("Review mapping", f"/ingest/{quoted_path(detail["ingestion_id"])}/review", css_class="button button-primary")}</p>',
    )
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
        headline=detail["filename"],
        kicker="Import",
        intro="Inspect how Papyrus parsed and classified the source before accepting any mapping or conversion.",
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html=mapping_summary,
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
        section_rows.append(
            "<tr>"
            f"<td>{escape(section_id)}</td>"
            f"<td>{escape(match.get('heading') or 'Unmapped')}</td>"
            f"<td>{escape(entry.get('confidence', 0.0))}</td>"
            "</tr>"
        )
    mapping_table = (
        f'<table class="data-table"><thead><tr><th>Blueprint section</th><th>Source heading</th><th>Confidence</th></tr></thead><tbody>{"".join(section_rows)}</tbody></table>'
        if section_rows
        else '<p class="empty-state-copy">No mapping summary available.</p>'
    )
    error_html = (
        components.validation_summary(title="Conversion blockers", findings=[escape(item) for item in errors or []], empty_label="")
        if errors
        else ""
    )
    convert_form = components.section_card(
        title="Convert to draft",
        eyebrow="Import",
        body_html=(
            error_html
            + '<form class="governed-form" method="post">'
            + forms.field(
                field_id="object_id",
                label="Object ID",
                control_html=forms.input(
                    field_id="object_id",
                    name="object_id",
                    value=f"kb-{slugify(str(detail['normalized_content'].get('title') or detail['filename']))}",
                ),
            )
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
                field_id="canonical_path",
                label="Canonical path",
                control_html=forms.input(
                    field_id="canonical_path",
                    name="canonical_path",
                    value=f"knowledge/imported/{slugify(str(detail['normalized_content'].get('title') or detail['filename']))}.md",
                ),
            )
            + forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=""))
            + forms.field(
                field_id="team",
                label="Team",
                control_html=forms.select(
                    field_id="team",
                    name="team",
                    value="IT Operations",
                    options=runtime.taxonomies["teams"]["allowed_values"],
                ),
            )
            + forms.field(
                field_id="review_cadence",
                label="Review cadence",
                control_html=forms.select(
                    field_id="review_cadence",
                    name="review_cadence",
                    value="quarterly",
                    options=runtime.taxonomies["review_cadences"]["allowed_values"],
                ),
            )
            + forms.field(
                field_id="status",
                label="Lifecycle status",
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
                    value="service_desk",
                    options=runtime.taxonomies["audiences"]["allowed_values"],
                ),
            )
            + forms.button(label="Convert to draft")
            + "</form>"
        ),
    )
    return runtime.page_renderer.render_page(
        page_template="pages/ingest_mapping_review.html",
        page_title=f"Review mapping for {detail['filename']}",
        headline=f"Review mapping for {detail['filename']}",
        kicker="Import",
        intro="Papyrus highlights mapped sections, gaps, and low-confidence matches before it will create a draft.",
        active_nav="import",
        flash_html=flash_html_for_request(runtime, request),
        actor_id=actor_for_request(request),
        current_path=request.path,
        aside_html=components.section_card(
            title="Next action",
            eyebrow="Guidance",
            body_html=(
                f"<p><strong>Missing required sections:</strong> {escape(len(mapping.get('missing_sections', [])))}</p>"
                f"<p><strong>Low-confidence matches:</strong> {escape(len(mapping.get('low_confidence', [])))}</p>"
                "<p>Review the gaps first. Convert only when the mapping is good enough to continue as a structured draft.</p>"
            ),
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
            if upload is None and not source_path:
                errors.append("Select a file upload or provide a local source path before starting ingestion.")
            else:
                try:
                    result = (
                        ingest_file(file_path=upload.filename, payload=upload.body, database_path=runtime.database_path)
                        if upload is not None
                        else ingest_file(file_path=source_path, database_path=runtime.database_path)
                    )
                    return redirect_response(
                        f"/ingest/{quoted_path(result['ingestion_id'])}?notice={quote_plus('Ingestion completed through upload, parse, classify, and initial mapping. Review the result before conversion.')}"
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
        mapping = detail.get("mapping_result") or map_to_blueprint(
            ingestion_id=ingestion_id,
            blueprint_id=detail.get("blueprint_id") or detail["classification"]["blueprint_id"],
            database_path=runtime.database_path,
        )
        errors: list[str] = []
        if request.method == "POST":
            required_fields = ["object_id", "title", "canonical_path", "owner", "team", "review_cadence", "status", "audience"]
            missing = [field for field in required_fields if not request.form_value(field).strip()]
            if missing:
                errors = [f"{field.replace('_', ' ')} is required." for field in missing]
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
                    f"/write/objects/{quoted_path(converted['object_id'])}/revisions/new?revision_id={quoted_path(converted['revision_id'])}&notice={quote_plus('Imported document converted into a governed draft.')}"
                )
        return html_response(_mapping_review_page(runtime, request=request, detail=detail, mapping=mapping, errors=errors))

    router.add(["GET", "POST"], "/ingest", ingest_list_page)
    router.add(["GET"], "/ingest/{ingestion_id}", ingest_detail_page)
    router.add(["GET", "POST"], "/ingest/{ingestion_id}/review", ingest_review_page)
