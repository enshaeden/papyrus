from __future__ import annotations

import importlib.util
import io
import sys
import unittest
import zlib
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import papyrus.infrastructure.parsers as parser_exports
from papyrus.infrastructure.parsers.csv_parser import parse_csv_bytes
from papyrus.infrastructure.parsers.docx_parser import parse_docx_bytes
from papyrus.infrastructure.parsers.html_parser import parse_html_bytes
from papyrus.infrastructure.parsers.markdown_parser import parse_markdown_bytes
from papyrus.infrastructure.parsers.pdf_parser import parse_pdf_bytes
from papyrus.infrastructure.parsers.text_parser import parse_text_bytes


DOCUTILS_AVAILABLE = importlib.util.find_spec("docutils") is not None
RTF_AVAILABLE = importlib.util.find_spec("striprtf") is not None
ODF_AVAILABLE = importlib.util.find_spec("odf") is not None

if DOCUTILS_AVAILABLE:
    from papyrus.infrastructure.parsers.rst_parser import parse_rst_bytes

if RTF_AVAILABLE:
    from papyrus.infrastructure.parsers.rtf_parser import parse_rtf_bytes

if ODF_AVAILABLE:
    from papyrus.infrastructure.parsers.odt_parser import parse_odt_bytes


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
    stream = zlib.compress(f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode())
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n"
        + f"<< /Length {len(stream)} /Filter /FlateDecode >>\n".encode("ascii")
        + b"stream\n"
        + stream
        + b"\nendstream\nendobj\n%%EOF"
    )


def _odt_payload() -> bytes:
    from odf.opendocument import OpenDocumentText
    from odf.table import Table, TableCell, TableRow
    from odf.text import H, List as OdfList, ListItem, P

    document = OpenDocumentText()
    document.text.addElement(H(outlinelevel=1, text="ODT Import Title"))
    document.text.addElement(P(text="Review ODT content."))
    item_list = OdfList()
    item_one = ListItem()
    item_one.addElement(P(text="Validate credentials"))
    item_list.addElement(item_one)
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


class ParserTests(unittest.TestCase):
    def test_parser_package_import_does_not_require_optional_dependencies(self) -> None:
        self.assertTrue(callable(parser_exports.parse_import_document))

    def test_supported_extensions_reflect_installed_parser_dependencies(self) -> None:
        supported = set(parser_exports.supported_import_extensions())

        self.assertIn(".md", supported)
        self.assertIn(".txt", supported)
        self.assertIn(".csv", supported)
        self.assertIn(".pdf", supported)
        if DOCUTILS_AVAILABLE:
            self.assertIn(".rst", supported)
        else:
            self.assertNotIn(".rst", supported)
        if RTF_AVAILABLE:
            self.assertIn(".rtf", supported)
        else:
            self.assertNotIn(".rtf", supported)
        if ODF_AVAILABLE:
            self.assertIn(".odt", supported)
        else:
            self.assertNotIn(".odt", supported)

    def test_markdown_parser_preserves_code_blocks(self) -> None:
        parsed = parse_markdown_bytes(
            b"# Markdown Import\n\n## Steps\n\n- Review\n\n```bash\npapyrus ingest sample.md\n```\n"
        )

        self.assertEqual(parsed["title"], "Markdown Import")
        self.assertEqual(parsed["elements"][2]["kind"], "list")
        self.assertEqual(parsed["elements"][3]["kind"], "preformatted")
        self.assertIn("papyrus ingest sample.md", parsed["preformatted_blocks"][0])

    def test_plain_text_parser_recovers_lists_and_preformatted_blocks(self) -> None:
        parsed = parse_text_bytes(
            b"Access Recovery\n\n- Confirm identity\n- Reset access\n\n    papyrus validate\n"
        )

        self.assertEqual(parsed["title"], "Access Recovery")
        self.assertEqual(parsed["lists"][0]["items"], ["Confirm identity", "Reset access"])
        self.assertEqual(parsed["preformatted_blocks"], ["papyrus validate"])

    @unittest.skipUnless(DOCUTILS_AVAILABLE, "docutils not installed")
    def test_rst_parser_recovers_structure_and_literal_blocks(self) -> None:
        parsed = parse_rst_bytes(
            b"RST Import Title\n================\n\nSteps\n-----\n\n- Review mapping\n\n::\n\n  papyrus ingest sample.rst\n"
        )

        self.assertEqual(parsed["title"], "RST Import Title")
        self.assertEqual(parsed["headings"][1]["text"], "Steps")
        self.assertEqual(parsed["lists"][0]["items"], ["Review mapping"])
        self.assertIn("papyrus ingest sample.rst", parsed["preformatted_blocks"][0])

    @unittest.skipUnless(RTF_AVAILABLE, "striprtf not installed")
    def test_rtf_parser_extracts_readable_text(self) -> None:
        parsed = parse_rtf_bytes(
            rb"{\rtf1\ansi Access Recovery\par - Confirm identity\par - Reset access\par}"
        )

        self.assertEqual(parsed["title"], "Access Recovery")
        self.assertEqual(parsed["lists"][0]["items"], ["Confirm identity", "Reset access"])

    def test_docx_parser_preserves_hyperlinks_and_table_structure(self) -> None:
        parsed = parse_docx_bytes(_docx_payload_with_hyperlink())

        self.assertEqual(parsed["title"], "DOCX Import Title")
        self.assertEqual(
            parsed["links"], [{"label": "Example Link", "target": "https://example.com/reference"}]
        )
        self.assertEqual(parsed["tables"][0][0], ["Owner", "IT Operations"])
        self.assertEqual(
            [element["kind"] for element in parsed["elements"]], ["heading", "paragraph", "table"]
        )
        self.assertEqual(parsed["extraction_quality"]["state"], "clean")

    @unittest.skipUnless(ODF_AVAILABLE, "odfpy not installed")
    def test_odt_parser_recovers_headings_lists_and_tables(self) -> None:
        parsed = parse_odt_bytes(_odt_payload())

        self.assertEqual(parsed["title"], "ODT Import Title")
        self.assertEqual(parsed["headings"][0]["text"], "ODT Import Title")
        self.assertEqual(parsed["lists"][0]["items"], ["Validate credentials"])
        self.assertEqual(parsed["tables"][0][0], ["Owner", "IT Operations"])

    def test_html_parser_drops_chrome_and_preserves_semantic_content(self) -> None:
        parsed = parse_html_bytes(
            b"""
            <html>
              <head><title>HTML Import Title</title><style>.x { color: red; }</style></head>
              <body>
                <nav>Navigation</nav>
                <main>
                  <h1>HTML Import Title</h1>
                  <p>Review import output.</p>
                  <pre>papyrus ingest sample.html</pre>
                  <table><tr><th>Owner</th><td>IT Operations</td></tr></table>
                </main>
                <script>console.log('ignore');</script>
              </body>
            </html>
            """
        )

        self.assertEqual(parsed["title"], "HTML Import Title")
        self.assertEqual(parsed["paragraphs"], ["Review import output."])
        self.assertEqual(parsed["preformatted_blocks"], ["papyrus ingest sample.html"])
        self.assertEqual(parsed["tables"][0][0], ["Owner", "IT Operations"])
        self.assertNotIn("Navigation", parsed["raw_text"])

    def test_csv_parser_normalizes_rows_as_table_text(self) -> None:
        parsed = parse_csv_bytes(b"Owner,Team\nAlice,IT Operations\n")

        self.assertEqual(parsed["tables"][0][0], ["Owner", "Team"])
        self.assertIn("Alice | IT Operations", parsed["raw_text"])
        self.assertEqual(parsed["elements"][0]["kind"], "table")

    def test_pdf_parser_extracts_text_from_compressed_streams(self) -> None:
        parsed = parse_pdf_bytes(
            _compressed_pdf_payload("Hello PDF extraction test with enough text for confidence.")
        )

        self.assertIn(
            "Hello PDF extraction test with enough text for confidence.", parsed["paragraphs"]
        )
        self.assertEqual(parsed["elements"][0]["kind"], "paragraph")
        self.assertEqual(parsed["extraction_quality"]["state"], "clean")
        self.assertEqual(parsed["parser_warnings"], [])

    @unittest.skipUnless(ODF_AVAILABLE, "odfpy not installed")
    def test_odt_parser_rejects_corrupt_payload(self) -> None:
        with self.assertRaisesRegex(ValueError, "malformed ODT"):
            parse_odt_bytes(b"not-an-odt")


if __name__ == "__main__":
    unittest.main()
