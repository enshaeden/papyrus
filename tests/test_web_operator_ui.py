from __future__ import annotations

import io
import json
import sqlite3
import sys
import tempfile
import urllib.parse
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.web import app as web_app


def call_wsgi(
    application,
    path: str,
    *,
    method: str = "GET",
    form: dict[str, object] | None = None,
    cookies: dict[str, str] | None = None,
) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

    body = urllib.parse.urlencode(form or {}, doseq=True).encode("utf-8")
    if "?" in path:
        path_info, query_string = path.split("?", 1)
    else:
        path_info, query_string = path, ""
    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path_info,
        "QUERY_STRING": query_string,
        "CONTENT_TYPE": "application/x-www-form-urlencoded",
        "CONTENT_LENGTH": str(len(body)),
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(body),
        "wsgi.errors": io.StringIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
        "codex.status_holder": status_holder,
    }
    if cookies:
        environ["HTTP_COOKIE"] = "; ".join(f"{name}={value}" for name, value in cookies.items())
    response_body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), response_body


def request_path_without_fragment(path: str) -> str:
    return path.split("#", 1)[0]


def read_row(database_path: Path, query: str, parameters: tuple = ()) -> sqlite3.Row | None:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(query, parameters).fetchone()
    finally:
        connection.close()


PRIMARY_SYSTEM = "Remote Access Gateway"
PRIMARY_CITATION_TITLE = "Remote access gateway import record"
PRIMARY_CITATION_REF = "records/remote-access-gateway-import-record.md"
PRIMARY_CITATION_NOTE = "Captured from the initial repository bootstrap record."


def guided_runbook_section_forms(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    summary: str,
    change_summary: str,
    citation_title: str = PRIMARY_CITATION_TITLE,
    citation_ref: str = PRIMARY_CITATION_REF,
    citation_note: str = PRIMARY_CITATION_NOTE,
    related_object_id: str = "kb-troubleshooting-vpn-connectivity",
) -> list[dict[str, str]]:
    return [
        {
            "section_id": "identity",
            "object_id": object_id,
            "title": title,
            "canonical_path": canonical_path,
        },
        {
            "section_id": "stewardship",
            "summary": summary,
            "owner": "workflow_owner",
            "team": "IT Operations",
            "object_lifecycle_state": "draft",
            "review_cadence": "quarterly",
            "audience": "service_desk",
            "systems": PRIMARY_SYSTEM,
            "tags": "vpn",
            "related_services": "Remote Access",
            "related_object_ids": related_object_id,
            "change_summary": change_summary,
        },
        {
            "section_id": "purpose",
            "use_when": "Use this when the governed workflow needs validation.",
        },
        {
            "section_id": "prerequisites",
            "prerequisites": "Open the ticket.",
        },
        {
            "section_id": "procedure",
            "steps": "Run the first step.",
        },
        {
            "section_id": "verification",
            "verification": "Confirm the operator outcome.",
        },
        {
            "section_id": "rollback",
            "rollback": "Undo the step.",
        },
        {
            "section_id": "boundaries",
            "boundaries_and_escalation": "Escalate when the workflow fails twice.",
            "related_knowledge_notes": "Pair with the VPN troubleshooting article.",
        },
        {
            "section_id": "evidence",
            "citation_1_source_title": citation_title,
            "citation_1_source_type": "document",
            "citation_1_source_ref": citation_ref,
            "citation_1_note": citation_note,
            "citation_2_source_type": "document",
            "citation_3_source_type": "document",
        },
        {
            "section_id": "relationships",
            "related_object_ids": related_object_id,
        },
    ]


def apply_guided_sections(
    application,
    start_path: str,
    section_forms: list[dict[str, str]],
    *,
    cookies: dict[str, str] | None = None,
) -> str:
    current_path = request_path_without_fragment(start_path)
    for form in section_forms:
        status, headers, body = call_wsgi(
            application,
            current_path,
            method="POST",
            form=form,
            cookies=cookies,
        )
        if status != "303 See Other":
            raise AssertionError(f"guided section {form['section_id']!r} failed with {status}: {body[:800]}")
        current_path = request_path_without_fragment(headers["Location"])
    return current_path


def complete_guided_runbook_revision(
    application,
    revision_form_path: str,
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    summary: str,
    change_summary: str,
    citation_title: str = PRIMARY_CITATION_TITLE,
    citation_ref: str = PRIMARY_CITATION_REF,
    citation_note: str = PRIMARY_CITATION_NOTE,
    cookies: dict[str, str] | None = None,
) -> str:
    return apply_guided_sections(
        application,
        revision_form_path,
        guided_runbook_section_forms(
            object_id=object_id,
            title=title,
            canonical_path=canonical_path,
            summary=summary,
            change_summary=change_summary,
            citation_title=citation_title,
            citation_ref=citation_ref,
            citation_note=citation_note,
        ),
        cookies=cookies,
    )


def runbook_payload(object_id: str, canonical_path: str, title: str) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Runbook payload for {title.lower()}",
        "knowledge_object_type": "runbook",
        "legacy_article_type": None,
        "object_lifecycle_state": "active",
        "owner": "workflow_owner",
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": [PRIMARY_SYSTEM],
        "tags": ["vpn"],
        "created": "2026-04-09",
        "updated": "2026-04-09",
        "last_reviewed": "2026-04-09",
        "review_cadence": "quarterly",
        "audience": "service_desk",
        "related_services": ["Remote Access"],
        "prerequisites": ["Open the incident ticket."],
        "steps": ["Perform the primary remediation step."],
        "verification": ["Confirm the workflow completed successfully."],
        "rollback": ["Undo the last remediation step."],
        "citations": [
            {
                "source_title": "Remote access gateway import record",
                "source_type": "document",
                "source_ref": "docs/reference/remote-access-gateway-import-record.md",
                "note": "Archive acknowledgement rendering coverage.",
            }
        ],
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": ["Remote Access"],
        "related_articles": [],
        "references": [
            {
                "title": "Remote access gateway import record",
                "path": "docs/reference/remote-access-gateway-import-record.md",
            }
        ],
        "change_log": [{"date": "2026-04-09", "summary": "Initial draft.", "author": "tests"}],
    }


class WebOperatorUiTests(unittest.TestCase):
    def test_write_and_manage_approval_flow_updates_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-approve",
                    "object_type": "runbook",
                    "title": "Operator UI Approval Flow",
                    "summary": "Approval flow exercised through the web interface.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/operator-ui-approval-flow.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")
            revision_form_path = headers["Location"]

            submit_path = complete_guided_runbook_revision(
                application,
                revision_form_path,
                object_id="kb-operator-ui-approve",
                title="Operator UI Approval Flow",
                canonical_path="knowledge/runbooks/operator-ui-approval-flow.md",
                summary="Approval flow exercised through the web interface.",
                change_summary="Initial draft through web UI.",
            )
            self.assertIn("/submit?revision_id=", submit_path)

            revision_id = urllib.parse.parse_qs(submit_path.split("?", 1)[1])["revision_id"][0]
            status, _, submit_body = call_wsgi(application, submit_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Step 3 of 3", submit_body)
            self.assertIn("Pre-submit validation", submit_body)
            self.assertIn("How to strengthen weak evidence", submit_body)
            self.assertIn("/manage/objects/kb-operator-ui-approve/evidence/revalidate", submit_body)
            self.assertIn("Send to review", submit_body)

            status, headers, _ = call_wsgi(
                application,
                submit_path,
                method="POST",
                form={"notes": "Ready for governance review."},
            )
            self.assertEqual(status, "303 See Other")
            assign_path = headers["Location"]

            status, _, assign_body = call_wsgi(application, assign_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Assign reviewer", assign_body)

            status, headers, _ = call_wsgi(
                application,
                assign_path,
                method="POST",
                form={"reviewer": "reviewer_a", "notes": "Review the draft.", "due_at": "2026-04-09"},
            )
            self.assertEqual(status, "303 See Other")
            decision_path = headers["Location"]

            status, _, decision_body = call_wsgi(application, decision_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Approve revision", decision_body)
            self.assertIn("Writeback contract", decision_body)
            self.assertIn("Writeback acknowledgement requirements", decision_body)
            self.assertIn("Likely downstream effect", decision_body)

            status, headers, _ = call_wsgi(
                application,
                decision_path,
                method="POST",
                form={"decision": "approve", "reviewer": "reviewer_a", "notes": "Approved in test."},
                cookies={"papyrus_actor": "local.reviewer"},
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("/objects/kb-operator-ui-approve", headers["Location"])

            revision_row = read_row(
                database_path,
                "SELECT revision_review_state FROM knowledge_revisions WHERE revision_id = ?",
                (revision_id,),
            )
            self.assertIsNotNone(revision_row)
            self.assertEqual(revision_row["revision_review_state"], "approved")

            assignment_row = read_row(
                database_path,
                "SELECT state FROM review_assignments WHERE revision_id = ? ORDER BY assigned_at DESC LIMIT 1",
                (revision_id,),
            )
            self.assertIsNotNone(assignment_row)
            self.assertEqual(assignment_row["state"], "approved")

            search_row = read_row(
                database_path,
                "SELECT revision_review_state FROM search_documents WHERE object_id = ?",
                ("kb-operator-ui-approve",),
            )
            self.assertIsNotNone(search_row)
            self.assertEqual(search_row["revision_review_state"], "approved")

    def test_rejection_flow_and_validation_messages_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, _, body = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "not-valid",
                    "object_type": "runbook",
                    "title": "",
                    "summary": "",
                    "owner": "",
                    "team": "Unknown Team",
                    "canonical_path": "bad-path.md",
                    "review_cadence": "weekly",
                    "object_lifecycle_state": "invalid",
                    "systems": "",
                    "tags": "",
                },
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Draft setup not saved. Fix the blocking fields below.", body)
            self.assertIn("Blocking validation", body)
            self.assertIn("Reference code: Reference code must use the kb-slug format.", body)
            self.assertIn("Title: Title is required.", body)
            self.assertIn("Reference code must use the kb-slug format.", body)
            self.assertIn("Publishing location must stay under knowledge/", body)

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-reject",
                    "object_type": "runbook",
                    "title": "Operator UI Rejection Flow",
                    "summary": "Rejection flow exercised through the web interface.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/operator-ui-rejection-flow.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            revision_form_path = headers["Location"]

            guided_forms = guided_runbook_section_forms(
                object_id="kb-operator-ui-reject",
                title="Operator UI Rejection Flow",
                canonical_path="knowledge/runbooks/operator-ui-rejection-flow.md",
                summary="Rejection flow exercised through the web interface.",
                change_summary="Initial draft through web UI.",
            )
            evidence_form = dict(guided_forms[-2])
            evidence_form["citation_1_source_title"] = ""
            evidence_form["citation_1_source_ref"] = ""
            evidence_form["citation_1_note"] = ""

            current_path = apply_guided_sections(
                application,
                revision_form_path,
                guided_forms[:-2],
            )
            status, _, body = call_wsgi(
                application,
                current_path,
                method="POST",
                form=evidence_form,
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Section not saved. Fix the blocking fields below.", body)
            self.assertIn("Blocking validation", body)
            self.assertIn("Citations: At least one citation is required.", body)

            submit_path = apply_guided_sections(application, current_path, guided_forms[-2:])
            revision_id = urllib.parse.parse_qs(submit_path.split("?", 1)[1])["revision_id"][0]
            status, headers, _ = call_wsgi(application, submit_path, method="POST", form={"notes": "Ready for review."})
            assign_path = headers["Location"]
            status, headers, _ = call_wsgi(
                application,
                assign_path,
                method="POST",
                form={"reviewer": "reviewer_b", "notes": "Please review.", "due_at": "2026-04-09"},
            )
            decision_path = headers["Location"]
            status, _, body = call_wsgi(
                application,
                decision_path,
                method="POST",
                form={"decision": "reject", "reviewer": "reviewer_b", "notes": ""},
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("A rejection rationale is required.", body)

            status, headers, _ = call_wsgi(
                application,
                decision_path,
                method="POST",
                form={"decision": "reject", "reviewer": "reviewer_b", "notes": "Rejecting in test."},
            )
            self.assertEqual(status, "303 See Other")

            revision_row = read_row(
                database_path,
                "SELECT revision_review_state FROM knowledge_revisions WHERE revision_id = ?",
                (revision_id,),
            )
            self.assertIsNotNone(revision_row)
            self.assertEqual(revision_row["revision_review_state"], "rejected")

    def test_manage_forms_capture_suspect_and_validation_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-manage",
                    "object_type": "runbook",
                    "title": "Operator UI Manage Flow",
                    "summary": "Manage-side workflow coverage.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/operator-ui-manage-flow.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            revision_form_path = headers["Location"]
            submit_path = complete_guided_runbook_revision(
                application,
                revision_form_path,
                object_id="kb-operator-ui-manage",
                title="Operator UI Manage Flow",
                canonical_path="knowledge/runbooks/operator-ui-manage-flow.md",
                summary="Manage-side workflow coverage.",
                change_summary="Initial draft through web UI.",
            )
            status, headers, _ = call_wsgi(application, submit_path, method="POST", form={"notes": "Ready for review."})
            self.assertEqual(status, "303 See Other")
            object_id = "kb-operator-ui-manage"

            status, _, body = call_wsgi(application, f"/manage/objects/{object_id}/suspect")
            self.assertEqual(status, "200 OK")
            self.assertIn("Suspect contract", body)
            self.assertIn("Mark object suspect", body)

            status, _, body = call_wsgi(
                application,
                f"/manage/objects/{object_id}/suspect",
                method="POST",
                form={"changed_entity_type": "", "changed_entity_id": "", "reason": ""},
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("A suspect rationale is required.", body)

            status, headers, _ = call_wsgi(
                application,
                f"/manage/objects/{object_id}/suspect",
                method="POST",
                form={
                    "changed_entity_type": "service",
                    "changed_entity_id": "Remote Access",
                    "reason": "Dependency changed during test execution.",
                },
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("/objects/kb-operator-ui-manage", headers["Location"])

            status, _, body = call_wsgi(application, f"/manage/objects/{object_id}/supersede")
            self.assertEqual(status, "200 OK")
            self.assertIn("Supersession contract", body)
            self.assertIn("Supersede object", body)

            status, _, body = call_wsgi(application, f"/manage/objects/{object_id}/archive")
            self.assertEqual(status, "200 OK")
            self.assertIn("Archive contract", body)
            self.assertIn("Required acknowledgements", body)
            self.assertIn("No acknowledgements are required.", body)

            status, _, body = call_wsgi(
                application,
                f"/manage/objects/{object_id}/archive",
                method="POST",
                form={"retirement_reason": "", "notes": ""},
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("A retirement rationale is required.", body)
            self.assertNotIn("You must acknowledge: canonical path will move to archive.", body)

            status, _, body = call_wsgi(
                application,
                f"/manage/objects/{object_id}/supersede",
                method="POST",
                form={"replacement_object_id": "", "notes": ""},
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Replacement object ID is required.", body)
            self.assertIn("A supersession rationale is required.", body)

            status, headers, _ = call_wsgi(
                application,
                "/manage/validation-runs/new",
                method="POST",
                form={
                    "run_id": "web-ui-validation-run",
                    "run_type": "manual_check",
                    "status": "warning",
                    "finding_count": "2",
                    "details": "Smoke-test findings",
                },
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("/manage/validation-runs", headers["Location"])

    def test_actor_selection_and_evidence_revalidation_actions_use_selected_actor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )
            actor_cookie = {"papyrus_actor": "local.manager"}

            status, headers, _ = call_wsgi(
                application,
                "/actor/select",
                method="POST",
                form={"actor": "local.manager", "next_path": "/queue"},
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("papyrus_actor=local.manager", headers["Set-Cookie"])

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-evidence",
                    "object_type": "runbook",
                    "title": "Operator UI Evidence Flow",
                    "summary": "Evidence revalidation coverage.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/operator-ui-evidence-flow.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
                cookies=actor_cookie,
            )
            revision_form_path = headers["Location"]
            submit_path = complete_guided_runbook_revision(
                application,
                revision_form_path,
                object_id="kb-operator-ui-evidence",
                title="Operator UI Evidence Flow",
                canonical_path="knowledge/runbooks/operator-ui-evidence-flow.md",
                summary="Evidence revalidation coverage.",
                change_summary="Seed evidence flow through web UI.",
                cookies=actor_cookie,
            )
            self.assertIn("/submit?revision_id=", submit_path)

            status, _, body = call_wsgi(
                application,
                "/manage/objects/kb-operator-ui-evidence/evidence/revalidate",
                cookies=actor_cookie,
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Revalidate evidence", body)

            status, headers, _ = call_wsgi(
                application,
                "/manage/objects/kb-operator-ui-evidence/evidence/revalidate",
                method="POST",
                form={"notes": "Operator requested a refreshed evidence snapshot."},
                cookies=actor_cookie,
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("/objects/kb-operator-ui-evidence", headers["Location"])

            connection = sqlite3.connect(database_path)
            connection.row_factory = sqlite3.Row
            try:
                audit_rows = connection.execute(
                    """
                    SELECT event_type, actor
                    FROM audit_events
                    WHERE object_id = ?
                      AND event_type IN ('object_created', 'evidence_revalidation_requested')
                    ORDER BY event_type
                    """,
                    ("kb-operator-ui-evidence",),
                ).fetchall()
            finally:
                connection.close()

            actors = {str(row["event_type"]): str(row["actor"]) for row in audit_rows}
            self.assertEqual(actors["object_created"], "local.manager")
            self.assertEqual(actors["evidence_revalidation_requested"], "local.manager")

    def test_archive_form_renders_backend_required_acknowledgements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            replacement = workflow.create_object(
                object_id="kb-archive-replacement-ui",
                object_type="runbook",
                title="Archive Replacement UI",
                summary="Replacement object for archive UI coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/archive-replacement-ui.md",
                actor="tests",
            )
            archived = workflow.create_object(
                object_id="kb-archive-ui",
                object_type="runbook",
                title="Archive UI",
                summary="Archive acknowledgement rendering coverage.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/archive-ui.md",
                actor="tests",
            )
            revision = workflow.create_revision(
                object_id=archived.object_id,
                normalized_payload=runbook_payload(archived.object_id, archived.canonical_path, archived.title),
                body_markdown="## Use When\n\nExercise archive acknowledgement rendering.\n",
                actor="tests",
                change_summary="Archive acknowledgement rendering coverage.",
            )
            workflow.submit_for_review(object_id=archived.object_id, revision_id=revision.revision_id, actor="tests")
            workflow.assign_reviewer(
                object_id=archived.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=archived.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approve before archive UI test.",
            )
            workflow.supersede_object(
                object_id=archived.object_id,
                replacement_object_id=replacement.object_id,
                actor="tests",
                notes="Deprecate before archive UI test.",
            )

            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )
            status, _, body = call_wsgi(application, f"/manage/objects/{archived.object_id}/archive")
            self.assertEqual(status, "200 OK")
            self.assertIn("Archive contract", body)
            self.assertIn("canonical path will move to archive", body)
            self.assertIn('name="acknowledgements"', body)

    def test_object_and_review_pages_render_single_shared_governed_panels(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            created = workflow.create_object(
                object_id="kb-single-governed-panels",
                object_type="runbook",
                title="Single Governed Panels",
                summary="Ensure shared governed panels do not duplicate.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/single-governed-panels.md",
                actor="tests",
            )
            initial_revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
                body_markdown="## Use When\n\nSeed approved revision for panel counting.\n",
                actor="tests",
                change_summary="Seed approved revision.",
            )
            workflow.submit_for_review(object_id=created.object_id, revision_id=initial_revision.revision_id, actor="tests")
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=initial_revision.revision_id,
                reviewer="reviewer_a",
                actor="tests",
            )
            workflow.approve_revision(
                object_id=created.object_id,
                revision_id=initial_revision.revision_id,
                reviewer="reviewer_a",
                actor="local.reviewer",
                notes="Approve seed revision.",
            )

            revision = workflow.create_revision(
                object_id=created.object_id,
                normalized_payload=runbook_payload(created.object_id, created.canonical_path, created.title),
                body_markdown="## Use When\n\nPanel counting review revision.\n",
                actor="tests",
                change_summary="Review revision for panel counting.",
            )
            workflow.submit_for_review(object_id=created.object_id, revision_id=revision.revision_id, actor="tests")
            workflow.assign_reviewer(
                object_id=created.object_id,
                revision_id=revision.revision_id,
                reviewer="reviewer_b",
                actor="tests",
            )

            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, _, object_body = call_wsgi(application, f"/objects/{created.object_id}")
            self.assertEqual(status, "200 OK")
            self.assertEqual(object_body.count("Governed actions"), 1)

            status, _, history_body = call_wsgi(application, f"/objects/{created.object_id}/revisions")
            self.assertEqual(status, "200 OK")
            self.assertEqual(history_body.count("Current governed actions"), 1)

            status, _, review_body = call_wsgi(application, f"/manage/reviews/{created.object_id}/{revision.revision_id}")
            self.assertEqual(status, "200 OK")
            self.assertEqual(review_body.count("Governed actions"), 1)
            self.assertEqual(review_body.count("Writeback contract"), 1)
            self.assertEqual(review_body.count("Writeback acknowledgement requirements"), 1)

    def test_role_selection_redirects_to_role_home_and_scopes_shell_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/actor/select",
                method="POST",
                form={"actor": "local.reviewer"},
            )
            self.assertEqual(status, "303 See Other")
            self.assertEqual(headers["Location"], "/review")
            self.assertIn("papyrus_actor=local.reviewer", headers["Set-Cookie"])

            status, _, home_body = call_wsgi(application, "/", cookies={"papyrus_actor": "local.manager"})
            self.assertEqual(status, "200 OK")
            self.assertIn("<title>Home | Papyrus</title>", home_body)
            self.assertIn("Local Manager", home_body)
            self.assertIn('class="topbar-menu"', home_body)
            self.assertIn("Working as", home_body)
            self.assertNotIn('<aside class="context-column">', home_body)
            self.assertNotIn('class="actor-banner', home_body)

            status, _, operator_body = call_wsgi(application, "/queue", cookies={"papyrus_actor": "local.operator"})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local Operator", operator_body)
            self.assertIn("Working as", operator_body)
            self.assertIn('class="topbar-menu"', operator_body)
            self.assertNotIn("Reader / Writer", operator_body)
            self.assertIn('class="topbar-menu-chip is-active" href="/read">Read</a>', operator_body)
            self.assertIn('class="topbar-menu-chip" href="/write/objects/new">Write</a>', operator_body)
            self.assertIn('class="topbar-menu-chip" href="/services">Services</a>', operator_body)
            self.assertIn("Navigation", operator_body)
            self.assertEqual(operator_body.count('class="sidebar-block"'), 1)
            self.assertNotIn("Start Here", operator_body)
            self.assertNotIn('<aside class="context-column">', operator_body)
            self.assertIn('href="/write/objects/new"', operator_body)
            self.assertIn('/static/js/shell.js', operator_body)
            self.assertNotIn('class="actor-banner', operator_body)

            status, _, reviewer_body = call_wsgi(application, "/queue", cookies={"papyrus_actor": "local.reviewer"})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local Reviewer", reviewer_body)
            self.assertIn('class="topbar-menu"', reviewer_body)
            self.assertNotIn(">Reviewer<", reviewer_body)
            self.assertIn("Review / Approvals", reviewer_body)
            self.assertIn("Knowledge Health", reviewer_body)
            self.assertIn("Activity / History", reviewer_body)
            self.assertIn('href="/review"', reviewer_body)
            self.assertIn('href="/activity"', reviewer_body)
            self.assertNotIn("Start Here", reviewer_body)
            self.assertNotIn('class="actor-banner', reviewer_body)

            status, _, manager_body = call_wsgi(application, "/queue", cookies={"papyrus_actor": "local.manager"})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local Manager", manager_body)
            self.assertIn('class="topbar-menu"', manager_body)
            self.assertNotIn(">Manager<", manager_body)
            self.assertIn('href="/health"', manager_body)
            self.assertNotIn("Start Here", manager_body)
            self.assertNotIn('class="actor-banner', manager_body)
            self.assertNotIn("Papyrus Demo", operator_body)
            self.assertNotIn("Papyrus Demo", reviewer_body)
            self.assertNotIn("Papyrus Demo", manager_body)

            status, _, reviewer_review_body = call_wsgi(application, "/review", cookies={"papyrus_actor": "local.reviewer"})
            self.assertEqual(status, "200 OK")
            self.assertIn("Review / Approvals", reviewer_review_body)
            self.assertIn('topbar-menu-chip is-active', reviewer_review_body)

    def test_shell_only_object_is_searchable_and_routes_back_to_revision_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-shell-search",
                    "object_type": "runbook",
                    "title": "Shell Search Runbook",
                    "summary": "Draft shell should be discoverable before its first revision.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/shell-search-runbook.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")
            revision_form_path = headers["Location"]
            self.assertTrue(
                revision_form_path.startswith(
                    "/write/objects/kb-operator-ui-shell-search/revisions/new?notice=Draft+setup+saved."
                )
            )
            self.assertTrue(revision_form_path.endswith("#revision-form"))

            status, _, body = call_wsgi(application, request_path_without_fragment(revision_form_path))
            self.assertEqual(status, "200 OK")
            self.assertIn('class="write-workspace"', body)
            self.assertIn("Draft Runbook", body)
            self.assertIn("Step 2 of 3", body)
            self.assertIn("Save and continue", body)
            self.assertIn("Check review handoff", body)
            self.assertIn('id="revision-form"', body)
            self.assertIn('method="post" action="/write/objects/kb-operator-ui-shell-search/revisions/new?revision_id=', body)
            self.assertIn("&section=", body)
            self.assertIn('class="sidebar"', body)
            self.assertIn('class="topbar-menu"', body)
            self.assertIn('class="topbar-menu-chip is-active" href="/write/objects/new">Write</a>', body)
            self.assertNotIn("shell-columns-focus", body)
            self.assertIn("/static/js/citation_picker.js", body)
            self.assertIn("/static/js/multi_value_picker.js", body)
            self.assertNotIn("/revisions/fallback", body)
            self.assertNotIn("Advanced draft editor", body)

            status, _, body = call_wsgi(
                application,
                "/queue?query=Shell+Search+Runbook&object_type=runbook&review_state=draft",
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("kb-operator-ui-shell-search", body)
            self.assertIn("/write/objects/kb-operator-ui-shell-search/revisions/new#revision-form", body)

    def test_manage_queue_exposes_next_governance_actions_for_shells_and_drafts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-manage-shell",
                    "object_type": "runbook",
                    "title": "Manage Queue Shell",
                    "summary": "Manage queue should show the next authoring step.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/manage-queue-shell.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")

            status, _, body = call_wsgi(application, "/manage/queue")
            self.assertEqual(status, "200 OK")
            self.assertIn("Manage Queue Shell", body)
            self.assertIn("/write/objects/kb-operator-ui-manage-shell/revisions/new#revision-form", body)
            self.assertIn("Draft first revision", body)

            complete_guided_runbook_revision(
                application,
                request_path_without_fragment(headers["Location"]),
                object_id="kb-operator-ui-manage-shell",
                title="Manage Queue Shell",
                canonical_path="knowledge/runbooks/manage-queue-shell.md",
                summary="Manage queue should show the next authoring step.",
                change_summary="Seed first draft for manage queue testing.",
            )

            status, _, body = call_wsgi(application, "/manage/queue")
            self.assertEqual(status, "200 OK")
            self.assertIn("Submit for review", body)
            self.assertIn("/write/objects/kb-operator-ui-manage-shell/revisions/new#revision-form", body)
            self.assertIn("/write/objects/kb-operator-ui-manage-shell/submit?revision_id=", body)

    def test_revision_citation_search_exposes_article_lookup_and_finds_existing_objects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-citation-search",
                    "object_type": "runbook",
                    "title": "Citation Search Runbook",
                    "summary": "Citation search should find existing governed knowledge.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/citation-search-runbook.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "citation-search-tag",
                },
            )
            self.assertEqual(status, "303 See Other")
            revision_form_path = request_path_without_fragment(headers["Location"])

            status, _, body = call_wsgi(application, revision_form_path + "&section=evidence")
            self.assertEqual(status, "200 OK")
            self.assertIn("Evidence handling", body)
            self.assertIn("data-citation-picker", body)
            self.assertIn("Search by title, tag, or reference code", body)
            self.assertIn("/static/js/citation_picker.js", body)
            self.assertIn("/write/citations/search", body)

            status, _, payload = call_wsgi(application, "/write/citations/search?query=kb-operator-ui-citation-search")
            self.assertEqual(status, "200 OK")
            self.assertEqual(json.loads(payload), {"items": []})

            submit_path = complete_guided_runbook_revision(
                application,
                revision_form_path,
                object_id="kb-operator-ui-citation-search",
                title="Citation Search Runbook",
                canonical_path="knowledge/runbooks/citation-search-runbook.md",
                summary="Citation search should find existing governed knowledge.",
                change_summary="Seed draft for citation search coverage.",
                citation_title="VPN Troubleshooting",
                citation_ref="knowledge/troubleshooting/vpn-connectivity.md",
                citation_note="Use the governed source article as supporting evidence.",
            )

            status, _, submit_body = call_wsgi(application, submit_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("governed Papyrus reference", submit_body)
            self.assertNotIn("How to strengthen weak evidence", submit_body)

            citation_row = read_row(
                database_path,
                """
                SELECT validity_status
                FROM citations
                WHERE revision_id = (
                    SELECT current_revision_id
                    FROM knowledge_objects
                    WHERE object_id = ?
                )
                ORDER BY citation_id
                LIMIT 1
                """,
                ("kb-operator-ui-citation-search",),
            )
            self.assertIsNotNone(citation_row)
            self.assertEqual(citation_row["validity_status"], "verified")

            for query in ("Citation Search Runbook", "kb-operator-ui-citation-search"):
                status, _, payload = call_wsgi(
                    application,
                    f"/write/citations/search?query={urllib.parse.quote_plus(query)}",
                )
                self.assertEqual(status, "200 OK")
                items = json.loads(payload)["items"]
                matching = [item for item in items if item["object_id"] == "kb-operator-ui-citation-search"]
                self.assertTrue(matching, msg=f"expected citation search result for query {query!r}")
                self.assertIn("Current revision can be referenced", matching[0]["summary"])
                self.assertIn("review", matching[0]["detail"])
                self.assertIn("trust", matching[0]["detail"])

    def test_revision_multiselect_fields_render_search_controls_and_object_lookup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
            )

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
                method="POST",
                form={
                    "object_id": "kb-operator-ui-multiselect",
                    "object_type": "runbook",
                    "title": "Multi Select Runbook",
                    "summary": "Revision form should render searchable multi-select controls.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/multi-select-runbook.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": PRIMARY_SYSTEM,
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")
            revision_form_path = request_path_without_fragment(headers["Location"])

            status, _, body = call_wsgi(application, revision_form_path + "&section=stewardship")
            self.assertEqual(status, "200 OK")
            self.assertIn("/static/js/multi_value_picker.js", body)
            self.assertIn('data-multi-value-picker', body)
            self.assertIn('data-static-options="', body)
            self.assertIn('data-search-url="/write/objects/search"', body)
            self.assertIn("Manual tag entry", body)
            self.assertIn("Manual service entry", body)
            self.assertIn("Manual reference entry", body)
            self.assertIn("/write/objects/search", body)
            self.assertIn("Search controlled tags", body)
            self.assertIn("Search related services", body)
            self.assertIn("Search related guidance", body)
            self.assertNotIn("/revisions/fallback", body)

            status, _, payload = call_wsgi(
                application,
                "/write/objects/search?query=VPN&exclude_object_id=kb-operator-ui-multiselect",
            )
            self.assertEqual(status, "200 OK")
            items = json.loads(payload)["items"]
            self.assertTrue(
                any(item["value"] == "kb-troubleshooting-vpn-connectivity" for item in items),
                msg="expected related object search to return a real runtime object",
            )


if __name__ == "__main__":
    unittest.main()
