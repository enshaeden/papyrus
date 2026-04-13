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
from papyrus.interfaces.web import app as web_app
from tests.web_assertions import SemanticHookAssertions


def call_wsgi(
    application,
    path: str,
    *,
    method: str = "GET",
    form: dict[str, object] | None = None,
    json_payload: dict[str, object] | None = None,
) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

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
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), body


class InterfaceSurfaceTests(SemanticHookAssertions, unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.database_path = Path(cls.temp_dir.name) / "runtime.db"
        build_search_projection(cls.database_path)
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

    def test_json_api_exposes_required_phase8_views(self) -> None:
        application = api_app(self.database_path)

        status, _, body = call_wsgi(application, "/queue")
        self.assertEqual(status, "200 OK")
        queue_payload = json.loads(body)
        self.assertIn("queue", queue_payload)
        self.assertTrue(queue_payload["queue"])

        status, _, body = call_wsgi(application, "/objects/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        object_payload = json.loads(body)
        self.assertEqual(object_payload["object"]["title"], "VPN Troubleshooting")

        status, _, body = call_wsgi(application, "/objects/kb-troubleshooting-vpn-connectivity/revisions")
        self.assertEqual(status, "200 OK")
        revision_payload = json.loads(body)
        self.assertTrue(revision_payload["revisions"])

        status, _, body = call_wsgi(application, f"/services/{self.remote_access_service_id}")
        self.assertEqual(status, "200 OK")
        service_payload = json.loads(body)
        self.assertEqual(service_payload["service"]["service_name"], "Remote Access")

        status, _, body = call_wsgi(application, "/dashboard/trust")
        self.assertEqual(status, "200 OK")
        dashboard_payload = json.loads(body)
        self.assertIn("object_count", dashboard_payload)
        self.assertIn("queue", dashboard_payload)

        status, _, body = call_wsgi(
            application,
            "/events",
            method="POST",
            json_payload={
                "actor": "tests",
                "event_type": "service_change",
                "entity_type": "service",
                "entity_id": "Remote Access",
                "payload": {"summary": "API event coverage."},
            },
        )
        self.assertEqual(status, "201 Created")

        status, _, body = call_wsgi(application, "/events?entity_type=service&entity_id=Remote%20Access")
        self.assertEqual(status, "200 OK")
        events_payload = json.loads(body)
        self.assertTrue(events_payload["events"])
        self.assertEqual(events_payload["events"][0]["event_type"], "service_change")
        self.assertIn("what_happened", events_payload["events"][0])
        self.assertIn("next_action", events_payload["events"][0])

        status, _, body = call_wsgi(application, "/services")
        self.assertEqual(status, "200 OK")
        services_payload = json.loads(body)
        self.assertIn("services", services_payload)

        status, _, body = call_wsgi(application, "/manage/queue")
        self.assertEqual(status, "200 OK")
        manage_payload = json.loads(body)
        self.assertIn("review_required", manage_payload)

        status, _, body = call_wsgi(application, "/impact/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        impact_payload = json.loads(body)
        self.assertEqual(impact_payload["entity"]["object_id"], "kb-troubleshooting-vpn-connectivity")

        status, _, body = call_wsgi(application, "/operator/read")
        self.assertEqual(status, "404 Not Found")
        api_error = json.loads(body)
        self.assertEqual(api_error["error"], "not_found")

    def test_web_surface_exposes_required_phase8_views(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/")
        self.assertEqual(status, "303 See Other")
        self.assertEqual(headers["Location"], "/operator")
        self.assertEqual(body, "")

        status, _, body = call_wsgi(application, "/operator")
        self.assertEqual(status, "200 OK")
        self.assertIn("<title>Home | Papyrus</title>", body)
        self.assert_primary_surface(body, "home")
        self.assertNotIn('<aside class="context-column">', body)
        self.assertNotIn('class="dual-grid"', body)

        status, _, body = call_wsgi(application, "/operator/read")
        self.assertEqual(status, "200 OK")
        self.assertIn("<title>Read Guidance | Papyrus</title>", body)
        self.assert_page_contract(body, primary_surface="read-queue", action_ids=("open-primary-surface",))
        self.assertNotIn('<aside class="context-column">', body)

        status, _, body = call_wsgi(application, "/operator/read/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assertIn("VPN Troubleshooting", body)
        self.assert_page_contract(body, primary_surface="object-detail", components=("article-section", "article-context-panel"))
        self.assertNotIn('<aside class="context-column">', body)
        self.assert_not_component(body, "object-header")

        status, _, body = call_wsgi(application, "/reader/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assertIn("VPN Troubleshooting", body)
        self.assert_page_contract(body, primary_surface="object-detail", components=("article-section", "article-context-panel"))
        self.assertIn('class="sidebar"', body)
        self.assertIn('href="/reader/browse"', body)
        self.assertNotIn("/operator/review/object/", body)

        status, _, body = call_wsgi(application, "/operator/read/object/kb-troubleshooting-vpn-connectivity/revisions")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="revision-history", components=("table",))

        status, _, body = call_wsgi(application, f"/operator/read/services/{self.remote_access_service_id}")
        self.assertEqual(status, "200 OK")
        self.assert_primary_surface(body, "services")
        self.assertIn("Remote Access", body)

        status, _, body = call_wsgi(application, "/operator/review/governance")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="knowledge-health", components=("health-board",))
        self.assertIn("Cleanup and trust debt", body)

        status, _, body = call_wsgi(application, "/operator/read/services")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="services", components=("service-map",))
        self.assertNotIn('<aside class="context-column">', body)

        status, _, body = call_wsgi(application, "/operator/review")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="review", components=("review-lane",))

        status, _, body = call_wsgi(application, "/operator/review/activity")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="activity", components=("activity-event",))

        status, _, body = call_wsgi(application, "/operator/review/impact/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assert_page_contract(body, primary_surface="impact-object", components=("impact-summary", "impact-trace"))

        for removed_path in (
            "/read",
            "/objects/kb-troubleshooting-vpn-connectivity",
            "/services",
            f"/services/{self.remote_access_service_id}",
            "/review",
            "/write/objects/new",
            "/ingest",
        ):
            with self.subTest(removed_path=removed_path):
                status, _, removed_body = call_wsgi(application, removed_path)
                self.assertEqual(status, "404 Not Found")
                self.assert_primary_surface(removed_body, "system-error")

    def test_static_theme_assets_expose_governed_brand_tokens(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/static/css/tokens.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertIn("--color-brand-hero: #5D3754;", body)
        self.assertIn("--color-brand-depth: #6A3460;", body)
        self.assertIn("--color-brand-context: #9991A4;", body)
        self.assertIn("--color-accent-primary: var(--color-brand-hero);", body)
        self.assertIn("--color-topbar-bg: var(--color-brand-hero);", body)
        self.assertIn("--color-accent-secondary-selected-bg: var(--color-brand-context-soft);", body)
        self.assertIn("--color-panel-governance-label: var(--color-brand-depth);", body)
        self.assertIn("--color-panel-governance-bg: var(--color-brand-context-panel);", body)

    def test_static_layout_assets_keep_topbar_search_centered(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/static/css/layout.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertIn("grid-template-columns: minmax(0, 1fr) minmax(18rem, 42rem) minmax(0, 1fr);", body)
        self.assertIn(".topbar-shell-controls {", body)
        self.assertIn("grid-column: 3;", body)
        self.assertIn("justify-self: end;", body)
        self.assertIn("grid-column: 2;", body)

    def test_static_read_assets_protect_dense_admin_results_table_layout(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/static/css/read.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertIn(".read-results-table .workbench-table {", body)
        self.assertIn("min-width: 56rem;", body)
        self.assertIn(".read-results-table .workbench-table th:nth-child(5),", body)
        self.assertIn("white-space: nowrap;", body)
        self.assertIn(".read-results-table .button {", body)
        self.assertIn("min-width: 5.5rem;", body)

    def test_static_health_assets_prevent_stretched_empty_governance_columns(self) -> None:
        application = web_app(self.database_path)

        status, headers, body = call_wsgi(application, "/static/css/health.css")
        self.assertEqual(status, "200 OK")
        self.assertEqual(headers["Content-Type"], "text/css")
        self.assertIn(".health-board__grid {", body)
        self.assertIn("align-items: start;", body)
        self.assertIn(".health-board__column {", body)
        self.assertIn("align-content: start;", body)
        self.assertIn(".health-board__card .button {", body)
        self.assertIn("justify-self: start;", body)

    def test_web_errors_and_method_guards_render_explicit_pages(self) -> None:
        application = web_app(self.database_path)

        status, _, body = call_wsgi(application, "/not-a-real-route")
        self.assertEqual(status, "404 Not Found")
        self.assert_primary_surface(body, "system-error")
        self.assertIn("shell-columns-minimal", body)
        self.assertNotIn("actor-banner", body)
        self.assertNotIn("page-kicker", body)

        status, _, body = call_wsgi(application, "/operator/read", method="POST", form={"query": "vpn"})
        self.assertEqual(status, "405 Method Not Allowed")
        self.assert_primary_surface(body, "system-error")
        self.assertIn("shell-columns-minimal", body)
        self.assertNotIn("actor-banner", body)
        self.assertNotIn("page-intro", body)

    def test_shell_templates_keep_behavior_in_static_script(self) -> None:
        topbar_template = (
            ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates" / "partials" / "topbar.html"
        ).read_text(encoding="utf-8")
        base_template = (ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates" / "base.html").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("<script", topbar_template)
        self.assertIn("{{ topbar_menu_html }}", topbar_template)
        self.assertIn('/static/js/shell.js', base_template)

    def test_api_write_endpoint_creates_object(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "workflow.db"
            build_search_projection(database_path)
            application = api_app(database_path)

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
            payload = json.loads(body)
            self.assertEqual(payload["object_id"], "kb-api-created-object")


if __name__ == "__main__":
    unittest.main()
