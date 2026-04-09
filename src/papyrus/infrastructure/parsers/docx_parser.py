from __future__ import annotations

from io import BytesIO
from zipfile import ZipFile

from lxml import etree


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def parse_docx_bytes(payload: bytes) -> dict[str, object]:
    with ZipFile(BytesIO(payload)) as archive:
        document_xml = archive.read("word/document.xml")
    root = etree.fromstring(document_xml)

    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[list[str]] = []
    tables: list[list[list[str]]] = []
    current_list: list[str] = []
    title = ""

    for paragraph in root.xpath(".//w:body/w:p", namespaces=WORD_NS):
        style_nodes = paragraph.xpath("./w:pPr/w:pStyle/@w:val", namespaces=WORD_NS)
        style = style_nodes[0] if style_nodes else ""
        text = "".join(node.text or "" for node in paragraph.xpath(".//w:t", namespaces=WORD_NS)).strip()
        if not text:
            continue
        if style.lower().startswith("heading"):
            if current_list:
                lists.append(current_list)
                current_list = []
            level_suffix = style[len("Heading") :]
            try:
                level = int(level_suffix)
            except ValueError:
                level = 1
            headings.append({"level": level, "text": text})
            if not title and level == 1:
                title = text
            continue
        if paragraph.xpath("./w:pPr/w:numPr", namespaces=WORD_NS):
            current_list.append(text)
            continue
        if current_list:
            lists.append(current_list)
            current_list = []
        paragraphs.append(text)

    if current_list:
        lists.append(current_list)

    for table in root.xpath(".//w:tbl", namespaces=WORD_NS):
        rows: list[list[str]] = []
        for row in table.xpath("./w:tr", namespaces=WORD_NS):
            cells = [
                "".join(node.text or "" for node in cell.xpath(".//w:t", namespaces=WORD_NS)).strip()
                for cell in row.xpath("./w:tc", namespaces=WORD_NS)
            ]
            rows.append(cells)
        if rows:
            tables.append(rows)

    return {
        "title": title or (paragraphs[0] if paragraphs else ""),
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "links": [],
        "raw_text": "\n".join(paragraphs),
    }
