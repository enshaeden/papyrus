from __future__ import annotations

import io
import sqlite3
import sys
import tempfile
import urllib.parse
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.web import app as web_app


def call_wsgi(application, path: str, *, method: str = "GET", form: dict[str, object] | None = None) -> tuple[str, dict[str, str], str]:
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
    }
    response_body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), response_body


def read_row(database_path: Path, query: str, parameters: tuple = ()) -> sqlite3.Row | None:
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        return connection.execute(query, parameters).fetchone()
    finally:
        connection.close()


class WebOperatorUiTests(unittest.TestCase):
    def test_write_and_manage_approval_flow_updates_runtime_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            application = web_app(database_path)

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
                    "status": "draft",
                    "systems": "<VPN_SERVICE>",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")
            revision_form_path = headers["Location"]

            status, headers, body = call_wsgi(
                application,
                revision_form_path,
                method="POST",
                form={
                    "title": "Operator UI Approval Flow",
                    "summary": "Approval flow exercised through the web interface.",
                    "status": "draft",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "review_cadence": "quarterly",
                    "audience": "service_desk",
                    "systems": "<VPN_SERVICE>",
                    "tags": "vpn",
                    "related_services": "Remote Access",
                    "related_object_ids": "kb-troubleshooting-vpn-connectivity",
                    "change_summary": "Initial draft through web UI.",
                    "prerequisites": "Open the ticket.",
                    "steps": "Run the first step.",
                    "verification": "Confirm the operator outcome.",
                    "rollback": "Undo the step.",
                    "use_when": "Use this when the governed workflow needs validation.",
                    "boundaries_and_escalation": "Escalate when the workflow fails twice.",
                    "related_knowledge_notes": "Pair with the VPN troubleshooting article.",
                    "citation_1_source_title": "Seed import manifest",
                    "citation_1_source_type": "document",
                    "citation_1_source_ref": "migration/import-manifest.yml",
                    "citation_1_note": "Internal provenance placeholder.",
                    "citation_2_source_type": "document",
                    "citation_3_source_type": "document",
                },
            )
            self.assertEqual(status, "303 See Other")
            submit_path = headers["Location"]
            self.assertIn("/submit?revision_id=", submit_path)

            revision_id = urllib.parse.parse_qs(submit_path.split("?", 1)[1])["revision_id"][0]
            status, _, submit_body = call_wsgi(application, submit_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Pre-submit validation", submit_body)

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

            status, headers, _ = call_wsgi(
                application,
                decision_path,
                method="POST",
                form={"decision": "approve", "reviewer": "reviewer_a", "notes": "Approved in test."},
            )
            self.assertEqual(status, "303 See Other")
            self.assertIn("/objects/kb-operator-ui-approve", headers["Location"])

            revision_row = read_row(
                database_path,
                "SELECT revision_state FROM knowledge_revisions WHERE revision_id = ?",
                (revision_id,),
            )
            self.assertIsNotNone(revision_row)
            self.assertEqual(revision_row["revision_state"], "approved")

            assignment_row = read_row(
                database_path,
                "SELECT state FROM review_assignments WHERE revision_id = ? ORDER BY assigned_at DESC LIMIT 1",
                (revision_id,),
            )
            self.assertIsNotNone(assignment_row)
            self.assertEqual(assignment_row["state"], "approved")

            search_row = read_row(
                database_path,
                "SELECT approval_state FROM search_documents WHERE object_id = ?",
                ("kb-operator-ui-approve",),
            )
            self.assertIsNotNone(search_row)
            self.assertEqual(search_row["approval_state"], "approved")

    def test_rejection_flow_and_validation_messages_render(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            application = web_app(database_path)

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
                    "status": "invalid",
                    "systems": "",
                    "tags": "",
                },
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Object ID must match kb-slug format.", body)
            self.assertIn("Canonical path must stay under knowledge/", body)

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
                    "status": "draft",
                    "systems": "<VPN_SERVICE>",
                    "tags": "vpn",
                },
            )
            revision_form_path = headers["Location"]

            status, _, body = call_wsgi(
                application,
                revision_form_path,
                method="POST",
                form={
                    "title": "Operator UI Rejection Flow",
                    "summary": "Rejection flow exercised through the web interface.",
                    "status": "draft",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "review_cadence": "quarterly",
                    "audience": "service_desk",
                    "systems": "<VPN_SERVICE>",
                    "tags": "vpn",
                    "related_services": "Remote Access",
                    "related_object_ids": "",
                    "change_summary": "",
                    "prerequisites": "Open the ticket.",
                    "steps": "Run the first step.",
                    "verification": "Confirm the operator outcome.",
                    "rollback": "Undo the step.",
                    "use_when": "Use this when the governed workflow needs validation.",
                    "boundaries_and_escalation": "Escalate when the workflow fails twice.",
                    "related_knowledge_notes": "Pair with the VPN troubleshooting article.",
                    "citation_1_source_title": "",
                    "citation_1_source_type": "document",
                    "citation_1_source_ref": "",
                    "citation_1_note": "",
                    "citation_2_source_type": "document",
                    "citation_3_source_type": "document",
                },
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("At least one citation is required.", body)

            status, headers, _ = call_wsgi(
                application,
                revision_form_path,
                method="POST",
                form={
                    "title": "Operator UI Rejection Flow",
                    "summary": "Rejection flow exercised through the web interface.",
                    "status": "draft",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "review_cadence": "quarterly",
                    "audience": "service_desk",
                    "systems": "<VPN_SERVICE>",
                    "tags": "vpn",
                    "related_services": "Remote Access",
                    "related_object_ids": "kb-troubleshooting-vpn-connectivity",
                    "change_summary": "Initial draft through web UI.",
                    "prerequisites": "Open the ticket.",
                    "steps": "Run the first step.",
                    "verification": "Confirm the operator outcome.",
                    "rollback": "Undo the step.",
                    "use_when": "Use this when the governed workflow needs validation.",
                    "boundaries_and_escalation": "Escalate when the workflow fails twice.",
                    "related_knowledge_notes": "Pair with the VPN troubleshooting article.",
                    "citation_1_source_title": "Seed import manifest",
                    "citation_1_source_type": "document",
                    "citation_1_source_ref": "migration/import-manifest.yml",
                    "citation_1_note": "Internal provenance placeholder.",
                    "citation_2_source_type": "document",
                    "citation_3_source_type": "document",
                },
            )
            submit_path = headers["Location"]
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
                "SELECT revision_state FROM knowledge_revisions WHERE revision_id = ?",
                (revision_id,),
            )
            self.assertIsNotNone(revision_row)
            self.assertEqual(revision_row["revision_state"], "rejected")


if __name__ == "__main__":
    unittest.main()
