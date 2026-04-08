from __future__ import annotations

import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.sync_flow import build_search_projection
from papyrus.interfaces.api import app as api_app
from papyrus.interfaces.web import app as web_app


def call_wsgi(application, path: str) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

    environ = {
        "REQUEST_METHOD": "GET",
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "SERVER_NAME": "testserver",
        "SERVER_PORT": "80",
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(b""),
        "wsgi.errors": io.StringIO(),
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(status_holder["status"]), dict(status_holder["headers"]), body


class InterfaceSurfaceTests(unittest.TestCase):
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

        status, _, body = call_wsgi(application, "/impact/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        impact_payload = json.loads(body)
        self.assertEqual(impact_payload["entity"]["object_id"], "kb-troubleshooting-vpn-connectivity")

    def test_web_surface_exposes_required_phase8_views(self) -> None:
        application = web_app(self.database_path)

        status, _, body = call_wsgi(application, "/queue")
        self.assertEqual(status, "200 OK")
        self.assertIn("Knowledge Queue", body)
        self.assertIn("/objects/", body)
        self.assertIn("citation:", body)

        status, _, body = call_wsgi(application, "/objects/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assertIn("VPN Troubleshooting", body)
        self.assertIn("Revision History", body)

        status, _, body = call_wsgi(application, "/objects/kb-troubleshooting-vpn-connectivity/revisions")
        self.assertEqual(status, "200 OK")
        self.assertIn("Revision history", body)

        status, _, body = call_wsgi(application, f"/services/{self.remote_access_service_id}")
        self.assertEqual(status, "200 OK")
        self.assertIn("Remote Access", body)

        status, _, body = call_wsgi(application, "/dashboard/trust")
        self.assertEqual(status, "200 OK")
        self.assertIn("Trust Dashboard", body)

        status, _, body = call_wsgi(application, "/impact/object/kb-troubleshooting-vpn-connectivity")
        self.assertEqual(status, "200 OK")
        self.assertIn("Impact", body)


if __name__ == "__main__":
    unittest.main()
