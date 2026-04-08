from __future__ import annotations

from urllib.parse import quote_plus

from papyrus.application.commands import create_object_command, create_revision_command, submit_for_review_command
from papyrus.application.queries import knowledge_object_detail, review_detail
from papyrus.interfaces.web.forms.object_forms import default_object_values, validate_object_form
from papyrus.interfaces.web.forms.revision_forms import build_revision_defaults, build_submission_findings, validate_revision_form
from papyrus.interfaces.web.forms.review_forms import validate_submit_form
from papyrus.interfaces.web.http import Request, html_response, redirect_response
from papyrus.interfaces.web.presenters.common import ComponentPresenter
from papyrus.interfaces.web.presenters.form_presenter import FormPresenter
from papyrus.interfaces.web.route_utils import flash_html_for_request
from papyrus.interfaces.web.view_helpers import escape, link, quoted_path


def _render_object_form(runtime, values: dict[str, str], errors: dict[str, list[str]]) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    controls = [
        forms.field(
            field_id="object_type",
            label="Object type",
            control_html=forms.select(field_id="object_type", name="object_type", value=values["object_type"], options=["runbook", "known_error", "service_record"]),
            hint="Choose the governed object type before drafting the first revision.",
            errors=errors.get("object_type"),
        ),
        forms.field(
            field_id="object_id",
            label="Object ID",
            control_html=forms.input(field_id="object_id", name="object_id", value=values["object_id"], placeholder="kb-remote-access-example"),
            hint="Stable control-plane identifier in kb-slug format.",
            errors=errors.get("object_id"),
        ),
        forms.field(
            field_id="title",
            label="Title",
            control_html=forms.input(field_id="title", name="title", value=values["title"], placeholder="Remote Access VPN recovery"),
            hint="Operator-facing title used in read surfaces and audit history.",
            errors=errors.get("title"),
        ),
        forms.field(
            field_id="summary",
            label="Summary",
            control_html=forms.textarea(field_id="summary", name="summary", value=values["summary"], rows=3, placeholder="Concise operational summary."),
            hint="Short operational summary shown above the fold.",
            errors=errors.get("summary"),
        ),
        forms.field(
            field_id="owner",
            label="Owner",
            control_html=forms.input(field_id="owner", name="owner", value=values["owner"], placeholder="team_or_person"),
            hint="Visible ownership is required for trust posture.",
            errors=errors.get("owner"),
        ),
        forms.field(
            field_id="team",
            label="Team",
            control_html=forms.select(field_id="team", name="team", value=values["team"], options=runtime.taxonomies["teams"]["allowed_values"]),
            hint="Primary accountable team.",
            errors=errors.get("team"),
        ),
        forms.field(
            field_id="canonical_path",
            label="Canonical path",
            control_html=forms.input(field_id="canonical_path", name="canonical_path", value=values["canonical_path"], placeholder="knowledge/runbooks/remote-access-vpn-recovery.md"),
            hint="Guidance only at this stage, but it must remain under knowledge/ for durable source placement.",
            errors=errors.get("canonical_path"),
        ),
        forms.field(
            field_id="review_cadence",
            label="Review cadence",
            control_html=forms.select(field_id="review_cadence", name="review_cadence", value=values["review_cadence"], options=runtime.taxonomies["review_cadences"]["allowed_values"]),
            hint="Controls stale posture in the trust model.",
            errors=errors.get("review_cadence"),
        ),
        forms.field(
            field_id="status",
            label="Lifecycle status",
            control_html=forms.select(field_id="status", name="status", value=values["status"], options=runtime.taxonomies["statuses"]["allowed_values"]),
            hint="New operator-authored objects should usually begin as draft.",
            errors=errors.get("status"),
        ),
        forms.field(
            field_id="systems",
            label="Systems",
            control_html=forms.input(field_id="systems", name="systems", value=values["systems"], placeholder="<VPN_SERVICE>, <IDENTITY_PROVIDER>"),
            hint="Comma-separated controlled system references.",
            errors=errors.get("systems"),
        ),
        forms.field(
            field_id="tags",
            label="Tags",
            control_html=forms.input(field_id="tags", name="tags", value=values["tags"], placeholder="vpn, service-desk"),
            hint="Comma-separated controlled tags for discovery and reporting.",
            errors=errors.get("tags"),
        ),
    ]
    body_html = (
        '<form class="governed-form" method="post">'
        + "".join(controls)
        + forms.button(label="Create object shell")
        + "</form>"
    )
    guidance_html = components.section_card(
        title="Governed authorship guidance",
        eyebrow="Write",
        body_html=(
            "<p>Create the object shell first, then move directly into a structured revision draft. This keeps source-path intent visible without forcing raw Markdown as the starting point.</p>"
        ),
    )
    return {
        "form_html": components.section_card(title="Create knowledge object", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }


def _common_revision_aside(runtime, detail) -> str:
    components = ComponentPresenter(runtime.template_renderer)
    item = detail["object"]
    return (
        components.trust_summary(
            title="Current object posture",
            badges=[
                components.badge(label="Trust", value=item["trust_state"], tone="approved" if item["trust_state"] == "trusted" else "warning"),
                components.badge(label="Approval", value=item["approval_state"] or "unknown", tone="approved" if item["approval_state"] == "approved" else "pending"),
                components.badge(label="Owner", value=item["owner"], tone="muted"),
            ],
            summary="Trust-relevant metadata remains visible while the author drafts the next revision.",
        )
    )


def _render_revision_form(runtime, detail, values: dict[str, str], errors: dict[str, list[str]], findings: list[str] | None = None) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    object_type = detail["object"]["object_type"]

    def multiline_field(name: str, label: str, hint: str) -> str:
        return forms.field(
            field_id=name,
            label=label,
            control_html=forms.textarea(field_id=name, name=name, value=values.get(name, ""), rows=4),
            hint=hint,
            errors=errors.get(name),
        )

    sections = [
        forms.field(field_id="title", label="Title", control_html=forms.input(field_id="title", name="title", value=values["title"]), errors=errors.get("title")),
        forms.field(field_id="summary", label="Summary", control_html=forms.textarea(field_id="summary", name="summary", value=values["summary"], rows=3), errors=errors.get("summary")),
        forms.field(field_id="change_summary", label="Change summary", control_html=forms.input(field_id="change_summary", name="change_summary", value=values["change_summary"]), hint="Short audit-facing summary of this revision.", errors=errors.get("change_summary")),
        forms.field(field_id="owner", label="Owner", control_html=forms.input(field_id="owner", name="owner", value=values["owner"]), errors=errors.get("owner")),
        forms.field(field_id="team", label="Team", control_html=forms.select(field_id="team", name="team", value=values["team"], options=runtime.taxonomies["teams"]["allowed_values"]), errors=errors.get("team")),
        forms.field(field_id="status", label="Lifecycle status", control_html=forms.select(field_id="status", name="status", value=values["status"], options=runtime.taxonomies["statuses"]["allowed_values"]), errors=errors.get("status")),
        forms.field(field_id="review_cadence", label="Review cadence", control_html=forms.select(field_id="review_cadence", name="review_cadence", value=values["review_cadence"], options=runtime.taxonomies["review_cadences"]["allowed_values"]), errors=errors.get("review_cadence")),
        forms.field(field_id="audience", label="Audience", control_html=forms.select(field_id="audience", name="audience", value=values["audience"], options=runtime.taxonomies["audiences"]["allowed_values"]), errors=errors.get("audience")),
        multiline_field("systems", "Systems", "One controlled system reference per line."),
        multiline_field("tags", "Tags", "One controlled tag per line."),
        multiline_field("related_services", "Related services", "One related service per line."),
        multiline_field("related_object_ids", "Related object IDs", "Link upstream, fallback, or sibling knowledge objects for impact tracing."),
    ]
    if object_type == "runbook":
        sections.extend(
            [
                multiline_field("prerequisites", "Prerequisites", "Operator prerequisites, access, or approvals."),
                multiline_field("steps", "Steps", "One operator step per line."),
                multiline_field("verification", "Verification", "How to confirm the expected outcome."),
                multiline_field("rollback", "Rollback", "Recovery actions if the procedure fails."),
                multiline_field("use_when", "Use when", "Narrative trigger condition and intended operator outcome."),
                multiline_field("boundaries_and_escalation", "Boundaries and escalation", "Where the runbook stops and escalation begins."),
                multiline_field("related_knowledge_notes", "Related knowledge notes", "Notes about adjacent procedures or follow-on documentation."),
            ]
        )
    elif object_type == "known_error":
        sections.extend(
            [
                multiline_field("symptoms", "Symptoms", "Observable failure signals."),
                forms.field(field_id="scope", label="Scope", control_html=forms.textarea(field_id="scope", name="scope", value=values["scope"], rows=3), errors=errors.get("scope")),
                forms.field(field_id="cause", label="Cause", control_html=forms.textarea(field_id="cause", name="cause", value=values["cause"], rows=3), errors=errors.get("cause")),
                multiline_field("diagnostic_checks", "Diagnostic checks", "One diagnostic check per line."),
                multiline_field("mitigations", "Mitigations", "One mitigation or containment step per line."),
                forms.field(field_id="permanent_fix_status", label="Permanent fix status", control_html=forms.select(field_id="permanent_fix_status", name="permanent_fix_status", value=values["permanent_fix_status"], options=runtime.taxonomies["permanent_fix_status"]["allowed_values"]), errors=errors.get("permanent_fix_status")),
                multiline_field("detection_notes", "Detection notes", "How operators recognize the issue."),
                multiline_field("escalation_threshold", "Escalation threshold", "When mitigations are exhausted or specialist takeover is required."),
                multiline_field("evidence_notes", "Evidence notes", "Any evidence handling notes relevant to operators or reviewers."),
            ]
        )
    else:
        sections.extend(
            [
                forms.field(field_id="service_name", label="Service name", control_html=forms.input(field_id="service_name", name="service_name", value=values["service_name"]), errors=errors.get("service_name")),
                forms.field(field_id="service_criticality", label="Service criticality", control_html=forms.select(field_id="service_criticality", name="service_criticality", value=values["service_criticality"], options=runtime.taxonomies["service_criticality"]["allowed_values"]), errors=errors.get("service_criticality")),
                multiline_field("dependencies", "Dependencies", "One dependency per line."),
                multiline_field("support_entrypoints", "Support entrypoints", "Primary support channels or escalation doors."),
                multiline_field("common_failure_modes", "Common failure modes", "One common failure mode per line."),
                multiline_field("related_runbooks", "Related runbooks", "One related runbook object ID per line."),
                multiline_field("related_known_errors", "Related known errors", "One related known error object ID per line."),
                multiline_field("scope_notes", "Scope", "Narrative service boundary and exclusions."),
                multiline_field("operational_notes", "Operational notes", "Support posture, caveats, and operating model."),
                multiline_field("evidence_notes", "Evidence notes", "Evidence caveats or capture instructions."),
            ]
        )

    citation_fields = []
    for index in range(1, 4):
        citation_fields.extend(
            [
                forms.field(field_id=f"citation_{index}_source_title", label=f"Citation {index} title", control_html=forms.input(field_id=f"citation_{index}_source_title", name=f"citation_{index}_source_title", value=values.get(f"citation_{index}_source_title", "")), errors=errors.get("citations")),
                forms.field(field_id=f"citation_{index}_source_type", label=f"Citation {index} type", control_html=forms.input(field_id=f"citation_{index}_source_type", name=f"citation_{index}_source_type", value=values.get(f"citation_{index}_source_type", "document")), hint="document, url, or system reference."),
                forms.field(field_id=f"citation_{index}_source_ref", label=f"Citation {index} reference", control_html=forms.input(field_id=f"citation_{index}_source_ref", name=f"citation_{index}_source_ref", value=values.get(f"citation_{index}_source_ref", "")), errors=errors.get("citations")),
                forms.field(field_id=f"citation_{index}_note", label=f"Citation {index} note", control_html=forms.textarea(field_id=f"citation_{index}_note", name=f"citation_{index}_note", value=values.get(f"citation_{index}_note", ""), rows=2), hint="Why this evidence supports the draft."),
            ]
        )

    validation_html = ""
    if findings:
        validation_html = components.validation_findings(title="Pre-submit findings", items=[escape(item) for item in findings], tone="warning")

    body_html = (
        '<form class="governed-form" method="post">'
        + "".join(sections)
        + '<section class="form-section"><h3>Evidence</h3>'
        + "".join(citation_fields)
        + "</section>"
        + forms.button(label="Save draft revision")
        + "</form>"
    )
    guidance_html = components.section_card(
        title="Authorship guidance",
        eyebrow="Write",
        body_html="<p>Structured fields feed trust, discovery, and governance surfaces directly. Narrative sections support operator judgment without hiding the metadata.</p>",
    )
    return {
        "validation_html": validation_html,
        "form_html": components.section_card(title="Create revision", eyebrow="Write", body_html=body_html),
        "guidance_html": guidance_html,
    }


def _render_submit_page(runtime, detail, findings: list[str], form_errors: dict[str, list[str]], values: dict[str, str]) -> dict[str, str]:
    forms = FormPresenter(runtime.template_renderer)
    components = ComponentPresenter(runtime.template_renderer)
    revision = detail["revision"]
    form_html = components.section_card(
        title="Submit for review",
        eyebrow="Write",
        body_html=(
            '<form class="governed-form" method="post">'
            + forms.field(
                field_id="notes",
                label="Submission notes",
                control_html=forms.textarea(field_id="notes", name="notes", value=values.get("notes", ""), rows=3),
                hint="Optional notes for reviewers and assignment triage.",
                errors=form_errors.get("notes"),
            )
            + forms.button(label="Submit revision")
            + "</form>"
        ),
    )
    summary_html = components.section_card(
        title="Submission summary",
        eyebrow="Write",
        body_html=(
            f"<p><strong>Revision:</strong> #{escape(revision['revision_number'])} · {escape(revision['revision_state'])}</p>"
            f"<p><strong>Change summary:</strong> {escape(revision['change_summary'] or 'No change summary recorded.')}</p>"
            f"<p><strong>Citations:</strong> {escape(len(detail['citations']))}</p>"
        ),
    )
    findings_html = components.validation_findings(title="Pre-submit validation", items=[escape(item) for item in findings] or ["No blocking findings detected."], tone="warning" if findings else "approved")
    return {
        "summary_html": summary_html,
        "findings_html": findings_html,
        "form_html": form_html,
    }


def register(router, runtime) -> None:
    def create_object_page(request: Request):
        values = default_object_values()
        errors: dict[str, list[str]] = {}
        if request.method == "POST":
            values = {key: request.form_value(key) for key in values}
            result = validate_object_form(values, taxonomies=runtime.taxonomies)
            if result.is_valid:
                created = create_object_command(database_path=runtime.database_path, actor="papyrus-web", **result.cleaned_data)
                return redirect_response(
                    f"/write/objects/{quoted_path(created.object_id)}/revisions/new?notice={quote_plus('Object shell created')}"
                )
            errors = result.errors
        page_context = _render_object_form(runtime, values, errors)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_object_new.html",
                page_title="Create knowledge object",
                headline="Create Knowledge Object",
                kicker="Write",
                intro="Start with a governed object shell, then move directly into a structured revision draft.",
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                action_bar_html="",
                aside_html="",
                page_context=page_context,
            )
        )

    def create_revision_page(request: Request):
        object_id = request.route_value("object_id")
        detail = knowledge_object_detail(object_id, database_path=runtime.database_path)
        values = build_revision_defaults(detail)
        errors: dict[str, list[str]] = {}
        findings: list[str] | None = None
        if request.method == "POST":
            values.update({key: request.form_value(key) for key in values})
            result = validate_revision_form(values=values, object_detail=detail, taxonomies=runtime.taxonomies)
            findings = result.cleaned_data["validation_findings"]
            if result.is_valid:
                revision = create_revision_command(
                    database_path=runtime.database_path,
                    object_id=object_id,
                    normalized_payload=result.cleaned_data["normalized_payload"],
                    body_markdown=result.cleaned_data["body_markdown"],
                    actor="papyrus-web",
                    legacy_metadata=detail.get("metadata") or {},
                    change_summary=result.cleaned_data["change_summary"],
                )
                return redirect_response(
                    f"/write/objects/{quoted_path(object_id)}/submit?revision_id={quoted_path(revision.revision_id)}&notice={quote_plus('Draft revision saved')}"
                )
            errors = result.errors
        page_context = _render_revision_form(runtime, detail, values, errors, findings)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/write_revision_new.html",
                page_title="Create revision",
                headline="Create Revision",
                kicker="Write",
                intro="Draft governed revisions with structured fields first, then narrative sections and evidence.",
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                aside_html=_common_revision_aside(runtime, detail),
                page_context=page_context,
            )
        )

    def submit_revision_page(request: Request):
        object_id = request.route_value("object_id")
        revision_id = request.query_value("revision_id")
        detail = review_detail(object_id, revision_id, database_path=runtime.database_path)
        values = {"notes": request.form_value("notes")}
        form_errors: dict[str, list[str]] = {}
        findings = build_submission_findings(
            object_type=detail["object"]["object_type"],
            payload=detail["revision"]["metadata"],
        )
        if request.method == "POST":
            result = validate_submit_form(values)
            if result.is_valid:
                submit_for_review_command(
                    database_path=runtime.database_path,
                    object_id=object_id,
                    revision_id=revision_id,
                    actor="papyrus-web",
                    notes=result.cleaned_data["notes"],
                )
                return redirect_response(
                    f"/manage/reviews/{quoted_path(object_id)}/{quoted_path(revision_id)}/assign?notice={quote_plus('Revision submitted for review')}"
                )
            form_errors = result.errors
        page_context = _render_submit_page(runtime, detail, findings, form_errors, values)
        return html_response(
            runtime.page_renderer.render_page(
                page_template="pages/review_submit.html",
                page_title="Submit for review",
                headline="Submit For Review",
                kicker="Write",
                intro="Inspect readiness before review. Missing structure or weak evidence should be explicit before handoff.",
                active_nav="write",
                flash_html=flash_html_for_request(runtime, request),
                aside_html=_common_revision_aside(runtime, {"object": detail["object"]}),
                page_context=page_context,
            )
        )

    router.add(["GET", "POST"], "/write/objects/new", create_object_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/revisions/new", create_revision_page)
    router.add(["GET", "POST"], "/write/objects/{object_id}/submit", submit_revision_page)
