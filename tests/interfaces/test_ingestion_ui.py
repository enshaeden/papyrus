from __future__ import annotations

import io
import tempfile
import urllib.parse
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

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


class IngestionUiTests(unittest.TestCase):
    def test_ingestion_workbench_requires_review_before_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_file = Path(temp_dir) / "import.md"
            source_file.write_text("# Import coverage\n\n## Steps\n\n- Review the import\n", encoding="utf-8")
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, headers, _ = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(source_file)})
            self.assertEqual(status, "303 See Other")
            detail_path = headers["Location"]

            status, _, body = call_wsgi(application, detail_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Mapping summary", body)
            self.assertIn("Upload", body)
            self.assertIn("Classify", body)
            self.assertIn("Review mapping", body)

            review_path = detail_path.split("?", 1)[0].rstrip("/") + "/review"
            status, _, review_body = call_wsgi(application, review_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Missing required sections", review_body)
            self.assertIn("Convert to draft", review_body)

    def test_ingestion_entry_shows_inline_error_when_no_source_is_provided(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, _, body = call_wsgi(application, "/ingest", method="POST", form={})
            self.assertEqual(status, "200 OK")
            self.assertIn("Import blockers", body)
            self.assertIn("Select a file upload or provide a local source path", body)
