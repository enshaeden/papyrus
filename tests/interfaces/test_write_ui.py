from __future__ import annotations

import io
import sqlite3
import tempfile
import urllib.parse
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.sync_flow import build_search_projection
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.interfaces.web.app import app as web_app
from tests.web_assertions import SemanticHookAssertions


def call_wsgi(
    application, path: str, *, method: str = "GET", form: dict[str, object] | None = None
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
    }
    response_body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), response_body


def request_path_without_fragment(path: str) -> str:
    return path.split("#", 1)[0]


def read_count(database_path: Path, query: str, parameters: tuple = ()) -> int:
    connection = sqlite3.connect(database_path)
    try:
        row = connection.execute(query, parameters).fetchone()
        return int(row[0] if row is not None else 0)
    finally:
        connection.close()


class WriteUiTests(SemanticHookAssertions, unittest.TestCase):
    def test_write_entry_page_keeps_operator_shell_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, _, body = call_wsgi(application, "/operator/write/new")
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(body, "write")
            self.assertIn("Start draft", body)
            self.assertIn('class="sidebar"', body)
            self.assertIn('class="topbar-menu"', body)
            self.assertIn(
                'class="sidebar-link is-active" href="/operator/write/new">Authoring</a>', body
            )
            self.assertIn('option value="runbook"', body)
            self.assertIn('option value="known_error"', body)
            self.assertIn('option value="service_record"', body)
            self.assertNotIn('option value="policy"', body)
            self.assertNotIn('option value="system_design"', body)
            self.assertIn('href="/operator/write/advanced"', body)

    def test_advanced_write_entry_page_exposes_all_blueprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, _, body = call_wsgi(application, "/operator/write/advanced")
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(body, "write")
            self.assertIn("Advanced authoring", body)
            self.assertIn('option value="runbook"', body)
            self.assertIn('option value="known_error"', body)
            self.assertIn('option value="service_record"', body)
            self.assertIn('option value="policy"', body)
            self.assertIn('option value="system_design"', body)

    def test_primary_write_route_rejects_deferred_blueprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, _, body = call_wsgi(
                application,
                "/operator/write/new",
                method="POST",
                form={
                    "object_id": "kb-ui-policy-rejected",
                    "object_type": "policy",
                    "title": "Policy Rejected On Primary Route",
                    "summary": "Primary route should reject deferred blueprint types.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/policies/policy-rejected-on-primary-route.md",
                    "review_cadence": "annual",
                    "object_lifecycle_state": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Choose a supported object type.", body)

    def test_policy_revision_page_shows_guided_policy_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, headers, _ = call_wsgi(
                application,
                "/operator/write/advanced",
                method="POST",
                form={
                    "object_id": "kb-ui-policy",
                    "object_type": "policy",
                    "title": "UI Policy",
                    "summary": "Policy UI parity coverage.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/policies/ui-policy.md",
                    "review_cadence": "annual",
                    "object_lifecycle_state": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])
            self.assertIn("revision_id=", guided_path)

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(guided_body, "write")
            self.assertIn("Draft Policy", guided_body)
            self.assertIn("Policy scope", guided_body)
            self.assertNotIn("Service name", guided_body)
            self.assertNotIn("Service criticality", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)

            guided_base, guided_query = guided_path.split("?", 1)
            invalid_guided_path = guided_base + "/fallback?" + guided_query
            status, _, removed_body = call_wsgi(application, invalid_guided_path)
            self.assertEqual(status, "404 Not Found")
            self.assert_primary_surface(removed_body, "system-error")
            self.assertIn("Not found", removed_body)

    def test_system_design_revision_page_shows_guided_system_design_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, headers, _ = call_wsgi(
                application,
                "/operator/write/advanced",
                method="POST",
                form={
                    "object_id": "kb-ui-system-design",
                    "object_type": "system_design",
                    "title": "UI System Design",
                    "summary": "System design UI parity coverage.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/system-designs/ui-system-design.md",
                    "review_cadence": "after_change",
                    "object_lifecycle_state": "draft",
                    "systems": "Identity Platform",
                    "tags": "identity",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])
            self.assertIn("revision_id=", guided_path)

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(guided_body, "write")
            self.assertIn("Draft System Design", guided_body)
            self.assertIn("Architecture", guided_body)
            self.assertNotIn("Service name", guided_body)
            self.assertNotIn("Service criticality", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)

    def test_read_filters_hide_policy_and_system_design_types_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, _, body = call_wsgi(application, "/operator/read")
            self.assertEqual(status, "200 OK")
            self.assertNotIn('option value="policy"', body)
            self.assertNotIn('option value="system_design"', body)

    def test_guided_revision_page_owns_search_backed_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, headers, _ = call_wsgi(
                application,
                "/operator/write/new",
                method="POST",
                form={
                    "object_id": "kb-ui-guided-route",
                    "object_type": "runbook",
                    "title": "Guided Route",
                    "summary": "Route isolation coverage.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/guided-route.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])
            self.assertIn("revision_id=", guided_path)

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(guided_body, "write")
            self.assertIn("Save and continue", guided_body)
            self.assertIn('class="sidebar"', guided_body)
            self.assertIn('class="topbar-menu"', guided_body)
            self.assertIn(
                'class="sidebar-link is-active" href="/operator/write/new">Authoring</a>', guided_body
            )
            self.assertNotIn("shell-columns-focus", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)
            self.assertNotIn("Advanced draft editor", guided_body)

            status, _, stewardship_body = call_wsgi(
                application, guided_path + "&section=stewardship"
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("data-multi-value-picker", stewardship_body)
            self.assertIn('data-search-url="/operator/write/objects/search"', stewardship_body)
            self.assertIn("Search controlled tags", stewardship_body)
            self.assertIn("Search related services", stewardship_body)

            status, _, evidence_body = call_wsgi(application, guided_path + "&section=evidence")
            self.assertEqual(status, "200 OK")
            self.assertIn("data-citation-picker", evidence_body)
            self.assertIn('data-search-url="/operator/write/citations/search"', evidence_body)

    def test_guided_revision_get_reload_is_side_effect_free(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, headers, _ = call_wsgi(
                application,
                "/operator/write/new",
                method="POST",
                form={
                    "object_id": "kb-ui-get-reload",
                    "object_type": "runbook",
                    "title": "Guided Reload",
                    "summary": "Guided reload should not mutate state.",
                    "owner": "workflow_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/guided-reload.md",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")
            guided_path = request_path_without_fragment(headers["Location"])
            revision_count_before = read_count(
                database_path,
                "SELECT COUNT(*) FROM knowledge_revisions WHERE object_id = ?",
                ("kb-ui-get-reload",),
            )
            audit_count_before = read_count(
                database_path,
                "SELECT COUNT(*) FROM audit_events WHERE object_id = ? AND event_type = 'revision_created'",
                ("kb-ui-get-reload",),
            )

            first_status, _, _ = call_wsgi(application, guided_path)
            second_status, _, _ = call_wsgi(application, guided_path)

            self.assertEqual(first_status, "200 OK")
            self.assertEqual(second_status, "200 OK")
            self.assertEqual(
                read_count(
                    database_path,
                    "SELECT COUNT(*) FROM knowledge_revisions WHERE object_id = ?",
                    ("kb-ui-get-reload",),
                ),
                revision_count_before,
            )
            self.assertEqual(
                read_count(
                    database_path,
                    "SELECT COUNT(*) FROM audit_events WHERE object_id = ? AND event_type = 'revision_created'",
                    ("kb-ui-get-reload",),
                ),
                audit_count_before,
            )

    def test_guided_revision_get_without_existing_draft_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            workflow = GovernanceWorkflow(database_path, source_root=source_root)
            workflow.create_object(
                object_id="kb-ui-empty-shell",
                object_type="runbook",
                title="Empty Shell",
                summary="Shell object without a draft.",
                owner="workflow_owner",
                team="IT Operations",
                canonical_path="knowledge/runbooks/empty-shell.md",
                actor="tests",
            )
            application = web_app(
                database_path, source_root=source_root, allow_noncanonical_source_root=True
            )

            status, _, body = call_wsgi(application, "/operator/write/object/kb-ui-empty-shell")

            self.assertEqual(status, "400 Bad Request")
            self.assert_primary_surface(body, "system-error")
            self.assertIn("Start a draft before loading this page", body)
