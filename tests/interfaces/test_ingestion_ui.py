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


def governed_ingest_path(temp_dir: str, filename: str) -> tuple[Path, Path]:
    source_root = Path(temp_dir) / "repo"
    source_path = source_root / "build" / "local-ingest" / filename
    source_path.parent.mkdir(parents=True, exist_ok=True)
    return source_root, source_path


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


def call_wsgi_multipart(
    application,
    path: str,
    *,
    fields: dict[str, str] | None = None,
    files: dict[str, tuple[str, str, bytes]] | None = None,
) -> tuple[str, dict[str, str], str]:
    status_holder: dict[str, object] = {}

    def start_response(status: str, headers: list[tuple[str, str]]) -> None:
        status_holder["status"] = status
        status_holder["headers"] = {name: value for name, value in headers}

    boundary = "----PapyrusMultipartBoundary"
    body_parts: list[bytes] = []
    for field_name, value in (fields or {}).items():
        body_parts.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode("utf-8"),
                str(value).encode("utf-8"),
                b"\r\n",
            ]
        )
    for field_name, (filename, content_type, payload) in (files or {}).items():
        body_parts.extend(
            [
                f"--{boundary}\r\n".encode("utf-8"),
                f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode("utf-8"),
                f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"),
                payload,
                b"\r\n",
            ]
        )
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(body_parts)
    if "?" in path:
        path_info, query_string = path.split("?", 1)
    else:
        path_info, query_string = path, ""
    environ = {
        "REQUEST_METHOD": "POST",
        "PATH_INFO": path_info,
        "QUERY_STRING": query_string,
        "CONTENT_TYPE": f"multipart/form-data; boundary={boundary}",
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
    def test_local_path_ingestion_is_disabled_by_default_in_web_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_file = Path(temp_dir) / "import.md"
            source_file.write_text("# Import coverage\n", encoding="utf-8")
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, _, body = call_wsgi(application, "/ingest")
            self.assertEqual(status, "200 OK")
            self.assertNotIn("Local file path (operator-only)", body)
            self.assertNotIn('name="source_path"', body)
            self.assertIn("Browser-submitted local file paths are disabled on this web server.", body)

            status, _, body = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(source_file)})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local file path ingestion is disabled on this web server.", body)

    def test_ingestion_workbench_requires_review_before_conversion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_file = governed_ingest_path(temp_dir, "import.md")
            source_file.write_text("# Import coverage\n\n## Steps\n\n- Review the import\n", encoding="utf-8")
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
                allow_web_ingest_local_paths=True,
            )

            status, headers, _ = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(source_file)})
            self.assertEqual(status, "303 See Other")
            detail_path = headers["Location"]

            status, _, body = call_wsgi(application, detail_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("upload, parse, and classify", body)
            self.assertIn("Import workflow contract", body)
            self.assertIn("Import workflow actions", body)
            self.assertIn("Mapping has not been generated yet.", body)
            self.assertIn("Generate mapping review", body)
            self.assertIn("Upload", body)
            self.assertIn("Classify", body)
            self.assertIn("Convert to draft", body)
            self.assertNotIn("#convert-to-draft-form", body)

            review_path = detail_path.split("?", 1)[0].rstrip("/") + "/review"
            status, _, review_body = call_wsgi(application, review_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Import workflow contract", review_body)
            self.assertIn("Import workflow actions", review_body)
            self.assertIn("Mapping review", review_body)
            self.assertIn("Missing required sections", review_body)
            self.assertIn("Convert to draft", review_body)
            self.assertNotIn("<h2>Next action</h2>", review_body)

    def test_ingestion_entry_shows_inline_error_when_no_source_is_provided(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, _, body = call_wsgi(application, "/ingest", method="POST", form={})
            self.assertEqual(status, "200 OK")
            self.assertIn("Import blockers", body)
            self.assertIn("Select a file upload before starting ingestion.", body)

    def test_local_path_ingestion_requires_explicit_opt_in_and_absolute_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
                allow_web_ingest_local_paths=True,
            )

            status, _, body = call_wsgi(application, "/ingest")
            self.assertEqual(status, "200 OK")
            self.assertIn("Local file path (operator-only)", body)
            self.assertIn("machine running Papyrus", body)

            status, _, invalid_body = call_wsgi(application, "/ingest", method="POST", form={"source_path": "relative.md"})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local file path ingestion requires an absolute path", invalid_body)

            missing_path = (Path(temp_dir) / "missing.md").resolve()
            status, _, missing_body = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(missing_path)})
            self.assertEqual(status, "200 OK")
            self.assertIn("Local source path not found.", missing_body)

    def test_ingestion_detail_surfaces_parser_warnings_for_degraded_input(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_file = governed_ingest_path(temp_dir, "empty.md")
            source_file.write_text("", encoding="utf-8")
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
                allow_web_ingest_local_paths=True,
            )

            status, headers, _ = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(source_file)})
            self.assertEqual(status, "303 See Other")
            detail_path = headers["Location"]

            status, _, body = call_wsgi(application, detail_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Parser assessment", body)
            self.assertIn("Markdown file is empty.", body)
            self.assertIn("Extraction quality:", body)

            review_path = detail_path.split("?", 1)[0].rstrip("/") + "/review"
            status, _, review_body = call_wsgi(application, review_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Parser assessment", review_body)
            self.assertIn("Markdown file is empty.", review_body)

    def test_mapping_review_surfaces_conflicts_and_fragment_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_file = governed_ingest_path(temp_dir, "conflicted-known-error.md")
            source_file.write_text(
                "# Login failure\n\n"
                "## Symptoms\n\n"
                "Users cannot sign in.\n\n"
                "## Diagnostic mitigation\n\n"
                "Diagnostic check mitigation workaround for cache corruption.\n",
                encoding="utf-8",
            )
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
                allow_web_ingest_local_paths=True,
            )

            status, headers, _ = call_wsgi(application, "/ingest", method="POST", form={"source_path": str(source_file)})
            self.assertEqual(status, "303 See Other")
            review_path = headers["Location"].split("?", 1)[0].rstrip("/") + "/review"

            status, _, body = call_wsgi(application, review_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("Import workflow contract", body)
            self.assertIn("Mapping conflicts", body)
            self.assertIn("Source fragment", body)
            self.assertIn("blocked_duplicate_source_reuse", body)

    def test_multipart_upload_sanitizes_browser_filename_before_storage(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            application = web_app(database_path, source_root=source_root, allow_noncanonical_source_root=True)

            status, headers, _ = call_wsgi_multipart(
                application,
                "/ingest",
                files={"upload": ("..\\..\\unsafe-import.md", "text/markdown", b"# Safe upload\n")},
            )
            self.assertEqual(status, "303 See Other")
            detail_path = headers["Location"]

            status, _, body = call_wsgi(application, detail_path)
            self.assertEqual(status, "200 OK")
            self.assertIn("unsafe-import.md", body)
            self.assertNotIn("..\\..\\unsafe-import.md", body)
            self.assertNotIn("..\\\\..\\\\unsafe-import.md", body)

    def test_ingest_entry_rejects_mixed_upload_and_local_path_submission(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = Path(temp_dir) / "repo"
            source_file = Path(temp_dir) / "import.md"
            source_file.write_text("# Mixed source\n", encoding="utf-8")
            application = web_app(
                database_path,
                source_root=source_root,
                allow_noncanonical_source_root=True,
                allow_web_ingest_local_paths=True,
            )

            status, _, body = call_wsgi_multipart(
                application,
                "/ingest",
                fields={"source_path": str(source_file)},
                files={"upload": ("upload.md", "text/markdown", b"# Upload copy\n")},
            )
            self.assertEqual(status, "200 OK")
            self.assertIn("Choose either a browser upload or a local operator file path, not both.", body)
