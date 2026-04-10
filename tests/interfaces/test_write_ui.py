from __future__ import annotations

import io
import tempfile
import urllib.parse
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
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


def request_path_without_fragment(path: str) -> str:
    return path.split("#", 1)[0]


class WriteUiTests(unittest.TestCase):
    def test_policy_revision_page_shows_guided_policy_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
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
                    "status": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Draft Policy", guided_body)
            self.assertIn("Policy scope", guided_body)
            self.assertNotIn("Service name", guided_body)
            self.assertNotIn("Service criticality", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)

            status, _, removed_body = call_wsgi(application, guided_path.replace("/revisions/new", "/revisions/fallback", 1))
            self.assertEqual(status, "404 Not Found")
            self.assertIn("Not found", removed_body)

    def test_system_design_revision_page_shows_guided_system_design_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
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
                    "status": "draft",
                    "systems": "Identity Platform",
                    "tags": "identity",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Draft System Design", guided_body)
            self.assertIn("Architecture", guided_body)
            self.assertNotIn("Service name", guided_body)
            self.assertNotIn("Service criticality", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)

    def test_read_filters_expose_policy_and_system_design_types(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            build_search_projection(database_path)
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, _, body = call_wsgi(application, "/read")
            self.assertEqual(status, "200 OK")
            self.assertIn('option value="policy"', body)
            self.assertIn('option value="system_design"', body)

    def test_guided_revision_page_owns_search_backed_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, headers, _ = call_wsgi(
                application,
                "/write/objects/new",
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
                    "status": "draft",
                    "systems": "Remote Access Gateway",
                    "tags": "vpn",
                },
            )
            self.assertEqual(status, "303 See Other")

            guided_path = request_path_without_fragment(headers["Location"])

            status, _, guided_body = call_wsgi(application, guided_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Save and continue", guided_body)
            self.assertIn("shell-columns-focus", guided_body)
            self.assertIn("/static/js/citation_picker.js", guided_body)
            self.assertIn("/static/js/multi_value_picker.js", guided_body)
            self.assertNotIn("/revisions/fallback", guided_body)
            self.assertNotIn("Advanced draft editor", guided_body)

            status, _, stewardship_body = call_wsgi(application, guided_path + "&section=stewardship")
            self.assertEqual(status, "200 OK")
            self.assertIn("data-multi-value-picker", stewardship_body)
            self.assertIn('data-search-url="/write/objects/search"', stewardship_body)
            self.assertIn("Search controlled tags", stewardship_body)
            self.assertIn("Search related services", stewardship_body)

            status, _, evidence_body = call_wsgi(application, guided_path + "&section=evidence")
            self.assertEqual(status, "200 OK")
            self.assertIn("data-citation-picker", evidence_body)
            self.assertIn('data-search-url="/write/citations/search"', evidence_body)
