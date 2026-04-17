from __future__ import annotations

import io
import sys
import tempfile
import urllib.parse
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.web.app import app as web_app
from tests.source_workspace import fixture_source_root
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


class WriteUiTests(SemanticHookAssertions, unittest.TestCase):
    def test_write_entry_page_keeps_shared_shell_navigation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root)

            status, _, body = call_wsgi(application, "/write")
            self.assertEqual(status, "303 See Other")

            status, _, body = call_wsgi(application, "/write/new")
            self.assertEqual(status, "200 OK")
            self.assert_primary_surface(body, "write")
            self.assertIn("Start draft", body)
            self.assertIn('class="sidebar"', body)
            self.assertIn('class="topbar-menu"', body)
            self.assertIn('class="sidebar-link is-active" href="/write/new">Write</a>', body)
            self.assertIn('option value="runbook"', body)
            self.assertIn('option value="known_error"', body)
            self.assertIn('option value="service_record"', body)
            self.assertNotIn('option value="policy"', body)
            self.assertNotIn('option value="system_design"', body)

    def test_removed_advanced_write_route_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            application = web_app(Path(temp_dir) / "runtime.db", source_root=Path(temp_dir) / "repo")
            status, _, body = call_wsgi(application, "/write/advanced")
            self.assertEqual(status, "404 Not Found")
            self.assert_primary_surface(body, "system-error")

    def test_primary_write_route_rejects_deferred_blueprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root)

            status, _, body = call_wsgi(
                application,
                "/write/new",
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

    def test_guided_revision_page_owns_search_backed_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root)

            status, headers, _ = call_wsgi(
                application,
                "/write/new",
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
            self.assertIn('class="sidebar-link is-active" href="/write/new">Write</a>', guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)

            status, _, bad_load_body = call_wsgi(application, "/write/object/kb-ui-empty-shell")
            self.assertEqual(status, "400 Bad Request")
            self.assertIn("knowledge object not found: kb-ui-empty-shell", bad_load_body)

    def test_search_helpers_use_canonical_shared_routes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root)

            status, _, body = call_wsgi(
                application, "/write/citations/search?query=kb-troubleshooting-vpn-connectivity"
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("kb-troubleshooting-vpn-connectivity", body)

            status, _, body = call_wsgi(
                application,
                "/write/objects/search?query=VPN&exclude_object_id=kb-troubleshooting-vpn-connectivity",
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Remote Access Service Record", body)

    def test_read_surface_does_not_offer_deferred_blueprints(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path, workspace_root=fixture_source_root())
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root)

            status, _, body = call_wsgi(application, "/read")
            self.assertEqual(status, "200 OK")
            self.assertNotIn('option value="policy"', body)
            self.assertNotIn('option value="system_design"', body)


if __name__ == "__main__":
    unittest.main()
