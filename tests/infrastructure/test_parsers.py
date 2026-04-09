from __future__ import annotations

import io
import sys
import unittest
import zlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from papyrus.infrastructure.parsers.docx_parser import parse_docx_bytes
from papyrus.infrastructure.parsers.pdf_parser import parse_pdf_bytes


def _docx_payload_with_hyperlink() -> bytes:
    document_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>DOCX Import Title</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Review </w:t></w:r>
      <w:hyperlink r:id="rId1">
        <w:r><w:t>Example Link</w:t></w:r>
      </w:hyperlink>
    </w:p>
    <w:tbl>
      <w:tr>
        <w:tc><w:p><w:r><w:t>Owner</w:t></w:r></w:p></w:tc>
        <w:tc><w:p><w:r><w:t>IT Operations</w:t></w:r></w:p></w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>
"""
    relationships_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="https://example.com/reference" TargetMode="External"/>
</Relationships>
"""
    buffer = io.BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", relationships_xml)
    return buffer.getvalue()


def _compressed_pdf_payload(text: str) -> bytes:
    stream = zlib.compress(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("utf-8"))
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        + f"<< /Length {len(stream)} /Filter /FlateDecode >>\n".encode("ascii")
        + b"stream\n"
        + stream
        + b"\nendstream\nendobj\n%%EOF"
    )


class ParserTests(unittest.TestCase):
    def test_docx_parser_preserves_hyperlinks_and_table_structure(self) -> None:
        parsed = parse_docx_bytes(_docx_payload_with_hyperlink())

        self.assertEqual(parsed["title"], "DOCX Import Title")
        self.assertEqual(parsed["links"], [{"label": "Example Link", "target": "https://example.com/reference"}])
        self.assertEqual(parsed["tables"][0][0], ["Owner", "IT Operations"])
        self.assertEqual([element["kind"] for element in parsed["elements"]], ["heading", "paragraph", "table"])
        self.assertEqual(parsed["extraction_quality"]["state"], "clean")

    def test_pdf_parser_extracts_text_from_compressed_streams(self) -> None:
        parsed = parse_pdf_bytes(
            _compressed_pdf_payload("Hello PDF extraction test with enough text for confidence.")
        )

        self.assertIn("Hello PDF extraction test with enough text for confidence.", parsed["paragraphs"])
        self.assertEqual(parsed["elements"][0]["kind"], "paragraph")
        self.assertEqual(parsed["extraction_quality"]["state"], "clean")
        self.assertEqual(parsed["parser_warnings"], [])
