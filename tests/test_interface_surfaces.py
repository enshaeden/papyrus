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

from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.web.app import app as web_app
from tests.source_workspace import fixture_source_root
from tests.web_assertions import SemanticHookAssertions


def call_wsgi(
    application,
    path: str,
    *,
    method: str = "GET",
    form: dict[str, object] | None = None,
    json_payload: dict[str, object] | None = None,
) -> tuple[str, dict[str, str], str]:
    response_status = ""
    response_headers: dict[str, str] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        nonlocal response_status, response_headers
        response_status = status
        response_headers = {name: value for name, value in headers}

    if json_payload is not None:
        body = json.dumps(json_payload).encode("utf-8")
        content_type = "application/json"
    else:
        body = urllib.parse.urlencode(form or {}, doseq=True).encode("utf-8")
        content_type = "application/x-www-form-urlencoded"

    if "?" in path:
        path_info, query_string = path.split("?", 1)
    else:
        path_info, query_string = path, ""

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path_info,
        "QUERY_STRING": query_string,
        "CONTENT_TYPE": content_type,
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
    return response_status, response_headers, response_body


class InterfaceSurfaceTests(SemanticHookAssertions, unittest.TestCase):
    temp_dir: tempfile.TemporaryDirectory[str]
    database_path: Path
    remote_access_service_id: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.database_path = Path(cls.temp_dir.name) / "runtime.db"
        build_search_projection(cls.database_path, workspace_root=fixture_source_root())
        connection = sqlite3.connect(cls.database_path)
        connection.row_factory = sqlite3.Row
        try:
            cls.remote_access_service_id = str(
                connection.execute(
                    "SELECT service_id FROM services WHERE service_name = 'Remote Access'"
                ).fetchone()["service_id"]
            )
        finally:
            connection.close()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp_dir.cleanup()

    def test_json_api_exposes_required_operator_views(self) -> None:
        application = api_app(self.database_path)

        status, _, body = call_wsgi(application, "/queue")
        self.assertEqual(status, "200 OK")
        self.assertTrue(json.loads(body)["queue"])

        status, _, body = call_wsgi(application, "/objects/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(body)["object"]["title"], "VPN Troubleshooting")

        status, _, body = call_wsgi(
            application, "/objects/kb-troubleshooting-vpn-connectivity/revisions"
        )
        self.assertEqual(status, "200 OK")
        self.assertTrue(json.loads(body)["revisions"])

        status, _, body = call_wsgi(application, f"/services/{self.remote_access_service_id}")
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(body)["service"]["service_name"], "Remote Access")

        status, _, body = call_wsgi(application, "/governance")
        self.assertEqual(status, "200 OK")
        self.assertIn("object_count", json.loads(body))

        status, _, body = call_wsgi(application, "/reviews")
        self.assertEqual(status, "200 OK")
        self.assertIn("review_required", json.loads(body))

        status, _, body = call_wsgi(
            application, "/impact/object/kb-troubleshooting-vpn-connectivity"
        )
        self.assertEqual(status, "200 OK")
        self.assertEqual(
            json.loads(body)["entity"]["object_id"], "kb-troubleshooting-vpn-connectivity"
        )

        status, _, body = call_wsgi(application, "/read")
        self.assertEqual(status, "404 Not Found")
        self.assertEqual(json.loads(body)["error"], "not_found")

    def test_web_surface_exposes_shared_routes_and_role_scoped_landings(self) -> None:
        operator_app = web_app(self.database_path)
        reader_app = web_app(self.database_path, default_role="reader")
        admin_app = web_app(self.database_path, default_role="admin")

        status, headers, body = call_wsgi(operator_app, "/")
        self.assertEqual(status, "303 See Other")
        self.assertEqual(headers["Location"], "/review")
        self.assertEqual(body, "")

        status, _, body = call_wsgi(operator_app, "/read")
        self.assertEqual(status, "200 OK")
        self.assertIn("<title>Read | Papyrus</title>", body)
        self.assert_page_contract(
            body, primary_surface="read-queue", action_ids=("open-primary-surface",)
        )

        status, _, body = call_wsgi(
            operator_app, "/read/object/kb-troubleshooting-vpn-connectivity"
        )
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(
            body,
            primary_surface="object-detail",
            components=("content-section", "context-panel"),
        )

        status, _, body = call_wsgi(operator_app, "/review")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="review", components=("review-lane",))

        status, _, body = call_wsgi(operator_app, "/governance")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(
            body, primary_surface="oversight", components=("oversight-board",)
        )

        status, _, body = call_wsgi(
            operator_app, f"/governance/services/{self.remote_access_service_id}"
        )
        self.assertEqual(status, "200 OK")
        self.assert_primary_surface(body, "services")
        self.assertIn("Remote Access", body)

        status, headers, _ = call_wsgi(reader_app, "/")
        self.assertEqual(status, "303 See Other")
        self.assertEqual(headers["Location"], "/read")

        status, _, body = call_wsgi(
            reader_app, "/read/object/kb-troubleshooting-vpn-connectivity"
        )
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(
            body,
            primary_surface="object-detail",
            components=("content-section", "context-panel"),
        )
        self.assert_component(body, "reader-object-tree-nav")
        self.assertNotIn("/review/object/", body)

        status, _, body = call_wsgi(reader_app, "/review")
        self.assertEqual(status, "404 Not Found")
        self.assert_primary_surface(body, "system-error")

        status, headers, _ = call_wsgi(admin_app, "/")
        self.assertEqual(status, "303 See Other")
        self.assertEqual(headers["Location"], "/admin/overview")

        status, _, body = call_wsgi(admin_app, "/admin/overview")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(
            body,
            primary_surface="overview",
            components=("admin-overview", "admin-overview-links"),
        )

        status, _, body = call_wsgi(admin_app, "/admin/users")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(
            body,
            primary_surface="users",
            components=("admin-control-panel", "admin-control-state"),
        )

    def test_legacy_prefixed_web_routes_fail_closed(self) -> None:
        application = web_app(self.database_path)

        for removed_path in (
            "/operator/read",
            "/reader/object/kb-troubleshooting-vpn-connectivity",
            "/admin/inspect",
            "/dashboard/oversight",
            "/review/queue",
            "/operator/import",
            "/operator/write/new",
        ):
            with self.subTest(removed_path=removed_path):
                status, _, body = call_wsgi(application, removed_path)
                self.assertEqual(status, "404 Not Found")
                self.assert_primary_surface(body, "system-error")

    def test_static_theme_assets_expose_governed_brand_tokens(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/static/css/tokens.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertIn("--color-brand-hero: #5D3754;", body)
        self.assertIn("--color-brand-depth: #6A3460;", body)
        self.assertIn("--color-brand-context: #9991A4;", body)

    def test_static_typography_assets_use_sans_contract(self) -> None:
        application = web_app(self.database_path)

        for asset_path in (
            "/static/css/layout.css",
            "/static/css/pages.css",
            "/static/css/home.css",
            "/static/css/health.css",
            "/static/css/services.css",
            "/static/css/content.css",
        ):
            with self.subTest(asset_path=asset_path):
                status, headers, body = call_wsgi(application, asset_path)
                self.assertEqual(status, "200 OK")
                self.assertEqual(headers["Content-Type"], "text/css")
                self.assertIn("font-family: var(--font-sans);", body)
                self.assertNotIn("var(--font-serif)", body)

        for asset_path in (
            "/static/css/activity.css",
            "/static/css/content.css",
            "/static/css/components.css",
        ):
            with self.subTest(mono_asset_path=asset_path):
                status, headers, body = call_wsgi(application, asset_path)
                self.assertEqual(status, "200 OK")
                self.assertEqual(headers["Content-Type"], "text/css")
                self.assertIn("font-family: var(--font-mono);", body)

    def test_web_errors_and_method_guards_render_explicit_pages(self) -> None:
        application = web_app(self.database_path)

        status, _, body = call_wsgi(application, "/not-a-real-route")
        self.assertEqual(status, "404 Not Found")
        self.assert_primary_surface(body, "system-error")

        status, _, body = call_wsgi(application, "/read", method="POST", form={"query": "vpn"})
        self.assertEqual(status, "405 Method Not Allowed")
        self.assert_primary_surface(body, "system-error")

    def test_api_write_endpoint_creates_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            source_root = Path(temp_dir) / "repo"
            build_search_projection(database_path, workspace_root=fixture_source_root())
            application = api_app(database_path, source_root=source_root)

            status, _, body = call_wsgi(
                application,
                "/objects",
                method="POST",
                json_payload={
                    "object_id": "kb-api-created-object",
                    "object_type": "runbook",
                    "title": "API Created Object",
                    "summary": "Created through API workflow coverage.",
                    "owner": "api_owner",
                    "team": "IT Operations",
                    "canonical_path": "knowledge/runbooks/api-created-object.md",
                    "actor": "tests",
                    "review_cadence": "quarterly",
                    "object_lifecycle_state": "draft",
                    "systems": ["Remote Access Gateway"],
                    "tags": ["vpn"],
                },
            )
            self.assertEqual(status, "201 Created")
            self.assertEqual(json.loads(body)["object_id"], "kb-api-created-object")


if __name__ == "__main__":
    unittest.main()
