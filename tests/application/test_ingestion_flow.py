from __future__ import annotations

import io
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.application.ingestion_flow import (
    ingest_file,
    ingestion_detail,
    mark_ingestion_converted,
    update_ingestion_mapping,
)
from papyrus.application.mapping_flow import map_to_blueprint
from papyrus.infrastructure.parsers import supported_import_extensions


SUPPORTED_IMPORT_EXTENSIONS = set(supported_import_extensions())
ODT_AVAILABLE = ".odt" in SUPPORTED_IMPORT_EXTENSIONS
RTF_AVAILABLE = ".rtf" in SUPPORTED_IMPORT_EXTENSIONS


def governed_ingest_path(temp_dir: str, filename: str) -> tuple[Path, Path]:
    source_root = Path(temp_dir) / "repo"
    source_path = source_root / "build" / "local-ingest" / filename
    source_path.parent.mkdir(parents=True, exist_ok=True)
    return source_root, source_path


def upload_source_root(temp_dir: str) -> Path:
    source_root = Path(temp_dir) / "repo"
    source_root.mkdir(parents=True, exist_ok=True)
    return source_root


def _docx_payload() -> bytes:
    document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>DOCX Import Title</w:t></w:r>
    </w:p>
    <w:p><w:r><w:t>Review DOCX output.</w:t></w:r></w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Owner</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>IT Operations</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>
"""
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
    return buffer.getvalue()


def _odt_payload() -> bytes:
    from odf.opendocument import OpenDocumentText
    from odf.table import Table, TableCell, TableRow
    from odf.text import H, List as OdfList, ListItem, P

    document = OpenDocumentText()
    document.text.addElement(H(outlinelevel=1, text="ODT Import Title"))
    document.text.addElement(P(text="Review ODT output."))
    item_list = OdfList()
    item = ListItem()
    item.addElement(P(text="Validate credentials"))
    item_list.addElement(item)
    document.text.addElement(item_list)
    table = Table(name="Owners")
    row = TableRow()
    owner_cell = TableCell()
    owner_cell.addElement(P(text="Owner"))
    row.addElement(owner_cell)
    value_cell = TableCell()
    value_cell.addElement(P(text="IT Operations"))
    row.addElement(value_cell)
    table.addElement(row)
    document.text.addElement(table)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _compressed_pdf_payload(text: str) -> bytes:
    stream = zlib.compress(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode())
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        + f"<< /Length {len(stream)} /Filter /FlateDecode >>\n".encode("ascii")
        + b"stream\n"
        + stream
        + b"\nendstream\nendobj\n%%EOF"
    )


class IngestionFlowTests(unittest.TestCase):
    def test_markdown_ingestion_is_classified_before_mapping_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n- Reconnect client\n\n## Verification\n\n- Confirm tunnel\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )

            self.assertEqual(detail["filename"], "sample.md")
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(detail["mapping_result"], {})
            self.assertEqual(detail["normalized_content"]["title"], "VPN Recovery")
            self.assertEqual(detail["normalized_content"]["detected_format"], "Markdown")
            artifact_types = {artifact["artifact_type"] for artifact in detail["artifacts"]}
            self.assertTrue(
                {
                    "uploaded",
                    "parsed",
                    "normalized",
                    "classified",
                    "sections",
                    "stage_progress",
                }.issubset(artifact_types)
            )
            uploaded = next(
                artifact["content"]
                for artifact in detail["artifacts"]
                if artifact["artifact_type"] == "uploaded"
            )
            self.assertEqual(uploaded["detected_format"], "Markdown")

    def test_ingestion_detail_exposes_workflow_projection_and_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n- Reconnect client\n\n## Verification\n\n- Confirm tunnel\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            classified_actions = {
                action["action_id"]: action for action in detail["workflow_projection"]["actions"]
            }
            self.assertEqual(detail["workflow_projection"]["summary"], "Generate mapping review")
            self.assertEqual(
                classified_actions["review_ingestion_mapping"]["availability"], "allowed"
            )
            self.assertEqual(
                classified_actions["convert_ingestion_to_draft"]["availability"], "illegal"
            )

            map_to_blueprint(
                ingestion_id=result["ingestion_id"],
                blueprint_id="runbook",
                database_path=database_path,
            )
            mapped = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            mapped_actions = {
                action["action_id"]: action for action in mapped["workflow_projection"]["actions"]
            }
            self.assertEqual(mapped["workflow_projection"]["rows"][0]["value"], "mapped")
            self.assertEqual(mapped_actions["review_ingestion_mapping"]["availability"], "allowed")
            self.assertEqual(
                mapped_actions["convert_ingestion_to_draft"]["availability"], "allowed"
            )

    def test_mapping_transition_requires_real_mapping_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n", encoding="utf-8"
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )

            with self.assertRaisesRegex(ValueError, "real mapping result exists"):
                update_ingestion_mapping(
                    ingestion_id=result["ingestion_id"],
                    mapping_result={},
                    blueprint_id="runbook",
                    database_path=database_path,
                )

            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(detail["mapping_result"], {})

    def test_conversion_transition_requires_real_mapping_result(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "sample.md")
            source_path.write_text(
                "# VPN Recovery\n\n## Steps\n\n- Validate connectivity\n", encoding="utf-8"
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )

            with self.assertRaisesRegex(
                ValueError, "real mapping result before it can be reviewed and converted"
            ):
                mark_ingestion_converted(
                    ingestion_id=result["ingestion_id"],
                    object_id="kb-vpn-recovery-imported",
                    revision_id="00000000-0000-0000-0000-000000000000",
                    database_path=database_path,
                )

            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )
            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertIsNone(detail["converted_revision_id"])

    def test_ordered_extraction_preserves_source_order_and_heading_context(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "ordered.md")
            source_path.write_text(
                "# Access Recovery\n\n"
                "## Procedure\n\n"
                "Confirm identity.\n\n"
                "- Reset access\n\n"
                "## Verification\n\n"
                "Confirm login succeeds.\n\n"
                "## Procedure\n\n"
                "Record the follow-up note.\n",
                encoding="utf-8",
            )

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            sections = result["sections"]

            self.assertEqual(
                [(section["kind"], section["heading"], section["text"]) for section in sections],
                [
                    ("heading", "Access Recovery", "Access Recovery"),
                    ("heading", "Procedure", "Procedure"),
                    ("paragraph", "Procedure", "Confirm identity."),
                    ("list", "Procedure", "Reset access"),
                    ("heading", "Verification", "Verification"),
                    ("paragraph", "Verification", "Confirm login succeeds."),
                    ("heading", "Procedure", "Procedure"),
                    ("paragraph", "Procedure", "Record the follow-up note."),
                ],
            )

    def test_preformatted_blocks_are_retained_as_fragments(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = upload_source_root(temp_dir)

            result = ingest_file(
                file_path="commands.md",
                payload=b"# Commands\n\n```bash\npapyrus ingest sample.md\n```",
                database_path=database_path,
                source_root=source_root,
                declared_media_type="text/markdown",
            )

            preformatted = [
                section for section in result["sections"] if section["kind"] == "preformatted"
            ]
            self.assertEqual(len(preformatted), 1)
            self.assertIn("papyrus ingest sample.md", preformatted[0]["text"])

    def test_empty_extraction_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "empty.md")
            source_path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "did not yield any readable text"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    def test_low_signal_pdf_is_ingested_with_warnings_when_text_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "weak.pdf")
            source_path.write_bytes(_compressed_pdf_payload("Short PDF note"))

            result = ingest_file(
                file_path=source_path, database_path=database_path, source_root=source_root
            )
            detail = ingestion_detail(
                ingestion_id=result["ingestion_id"], database_path=database_path
            )

            self.assertEqual(detail["ingestion_state"], "classified")
            self.assertEqual(
                detail["normalized_content"]["extraction_quality"]["state"], "degraded"
            )
            self.assertTrue(detail["normalized_content"]["parser_warnings"])

    def test_import_accepts_supported_uploaded_formats(self) -> None:
        payloads = {
            "sample.txt": (b"Access Recovery\n\n- Confirm identity\n", "text/plain", "Plain text"),
            "sample.docx": (
                _docx_payload(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "DOCX",
            ),
            "sample.html": (
                b"<html><body><h1>HTML Import</h1><p>Review output.</p></body></html>",
                "text/html",
                "HTML",
            ),
            "sample.csv": (b"Owner,Team\nAlice,IT Operations\n", "text/csv", "CSV"),
        }
        if RTF_AVAILABLE:
            payloads["sample.rtf"] = (
                rb"{\rtf1\ansi Access Recovery\par - Confirm identity\par}",
                "application/rtf",
                "RTF",
            )
        if ODT_AVAILABLE:
            payloads["sample.odt"] = (
                _odt_payload(),
                "application/vnd.oasis.opendocument.text",
                "ODT",
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = upload_source_root(temp_dir)
            for filename, (payload, content_type, detected_format) in payloads.items():
                with self.subTest(filename=filename):
                    result = ingest_file(
                        file_path=filename,
                        payload=payload,
                        declared_media_type=content_type,
                        database_path=database_path,
                        source_root=source_root,
                    )
                    detail = ingestion_detail(
                        ingestion_id=result["ingestion_id"], database_path=database_path
                    )
                    self.assertEqual(
                        detail["normalized_content"]["detected_format"], detected_format
                    )

    def test_declared_media_type_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = upload_source_root(temp_dir)

            with self.assertRaisesRegex(ValueError, "does not match .docx"):
                ingest_file(
                    file_path="sample.docx",
                    payload=_docx_payload(),
                    declared_media_type="text/html",
                    database_path=database_path,
                    source_root=source_root,
                )

    def test_malformed_docx_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "broken.docx")
            source_path.write_bytes(b"not-a-docx")

            with self.assertRaisesRegex(ValueError, "malformed DOCX"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    @unittest.skipUnless(ODT_AVAILABLE, "odfpy not installed")
    def test_malformed_odt_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "broken.odt")
            source_path.write_bytes(b"not-an-odt")

            with self.assertRaisesRegex(ValueError, "malformed ODT"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    @unittest.skipIf(ODT_AVAILABLE, "odfpy is installed in this environment")
    def test_missing_odt_dependency_is_reported_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root = upload_source_root(temp_dir)

            with self.assertRaisesRegex(
                ValueError, "required parser dependencies are not installed: odfpy"
            ):
                ingest_file(
                    file_path="sample.odt",
                    payload=b"not-an-odt",
                    declared_media_type="application/vnd.oasis.opendocument.text",
                    database_path=database_path,
                    source_root=source_root,
                )

    def test_malformed_pdf_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "broken.pdf")
            source_path.write_bytes(b"not-a-pdf")

            with self.assertRaisesRegex(ValueError, "malformed PDF"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )

    def test_unsupported_file_type_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "runtime.db"
            source_root, source_path = governed_ingest_path(temp_dir, "notes.bin")
            source_path.write_bytes(b"unsupported")

            with self.assertRaisesRegex(ValueError, "Unsupported import file type"):
                ingest_file(
                    file_path=source_path, database_path=database_path, source_root=source_root
                )
