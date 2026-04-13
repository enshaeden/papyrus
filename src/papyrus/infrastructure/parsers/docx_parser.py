from __future__ import annotations

from io import BytesIO
from zipfile import BadZipFile, ZipFile

from lxml import etree

WORD_NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
WORD_REL_NS = {"rel": "http://schemas.openxmlformats.org/package/2006/relationships"}
WORD_REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
WORD_ANCHOR = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}anchor"
HYPERLINK_REL_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"


def _normalize_text(value: str) -> str:
    return " ".join(value.split())


def _extract_text(element: etree._Element) -> str:
    return _normalize_text(
        "".join(node for node in element.xpath(".//w:t/text()", namespaces=WORD_NS))
    )


def _table_text(rows: list[list[str]]) -> str:
    return "\n".join(
        " | ".join(cell for cell in row if cell) for row in rows if any(cell for cell in row)
    )


def _relationship_targets(archive: ZipFile) -> dict[str, str]:
    try:
        relationships_xml = archive.read("word/_rels/document.xml.rels")
    except KeyError:
        return {}
    root = etree.fromstring(relationships_xml)
    targets: dict[str, str] = {}
    for relationship in root.xpath("./rel:Relationship", namespaces=WORD_REL_NS):
        if str(relationship.get("Type") or "") != HYPERLINK_REL_TYPE:
            continue
        relationship_id = str(relationship.get("Id") or "").strip()
        target = str(relationship.get("Target") or "").strip()
        if relationship_id and target:
            targets[relationship_id] = target
    return targets


def _paragraph_links(
    paragraph: etree._Element, relationship_targets: dict[str, str]
) -> tuple[list[dict[str, str]], int]:
    links: list[dict[str, str]] = []
    unresolved = 0
    for hyperlink in paragraph.xpath("./w:hyperlink", namespaces=WORD_NS):
        label = _extract_text(hyperlink)
        relationship_id = str(hyperlink.get(WORD_REL_ID) or "").strip()
        anchor = str(hyperlink.get(WORD_ANCHOR) or "").strip()
        target = relationship_targets.get(relationship_id)
        if not target and anchor:
            target = f"#{anchor}"
        if label and target:
            links.append({"label": label, "target": target})
        elif label:
            unresolved += 1
    return links, unresolved


def parse_docx_bytes(payload: bytes) -> dict[str, object]:
    try:
        with ZipFile(BytesIO(payload)) as archive:
            try:
                document_xml = archive.read("word/document.xml")
            except KeyError as exc:
                raise ValueError("malformed DOCX: missing word/document.xml") from exc
            relationship_targets = _relationship_targets(archive)
    except BadZipFile as exc:
        raise ValueError("malformed DOCX: not a valid zip archive") from exc
    try:
        root = etree.fromstring(document_xml)
    except etree.XMLSyntaxError as exc:
        raise ValueError("malformed DOCX: word/document.xml is not valid XML") from exc

    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[list[str]] = []
    tables: list[list[list[str]]] = []
    elements: list[dict[str, object]] = []
    links: list[dict[str, str]] = []
    current_list: list[str] = []
    title = ""
    warnings: list[str] = []
    degradation_notes: list[str] = []
    unresolved_links = 0
    raw_text_parts: list[str] = []

    body = root.find(".//w:body", namespaces=WORD_NS)
    if body is None:
        raise ValueError("malformed DOCX: missing document body")

    def flush_list() -> None:
        nonlocal current_list
        if current_list:
            items = [item for item in current_list if item]
            if items:
                lists.append(items)
                raw_text_parts.extend(items)
                elements.append({"kind": "list", "items": items, "text": "\n".join(items)})
            current_list = []

    for block in body.xpath("./w:p | ./w:tbl", namespaces=WORD_NS):
        if etree.QName(block).localname == "tbl":
            flush_list()
            rows: list[list[str]] = []
            for row in block.xpath("./w:tr", namespaces=WORD_NS):
                cells: list[str] = []
                for cell in row.xpath("./w:tc", namespaces=WORD_NS):
                    cell_text = _extract_text(cell)
                    cells.append(cell_text)
                    if cell_text:
                        raw_text_parts.append(cell_text)
                rows.append(cells)
            if rows:
                tables.append(rows)
                elements.append({"kind": "table", "rows": rows, "text": _table_text(rows)})
            continue
        paragraph = block
        style_nodes = paragraph.xpath("./w:pPr/w:pStyle/@w:val", namespaces=WORD_NS)
        style = style_nodes[0] if style_nodes else ""
        paragraph_links, unresolved = _paragraph_links(paragraph, relationship_targets)
        links.extend(paragraph_links)
        unresolved_links += unresolved
        text = _extract_text(paragraph)
        if not text:
            continue
        if style.lower().startswith("heading"):
            flush_list()
            level_suffix = style[len("Heading") :]
            try:
                level = int(level_suffix)
            except ValueError:
                level = 1
            headings.append({"level": level, "text": text})
            elements.append({"kind": "heading", "level": level, "text": text})
            raw_text_parts.append(text)
            if not title and level == 1:
                title = text
            continue
        if paragraph.xpath("./w:pPr/w:numPr", namespaces=WORD_NS):
            current_list.append(text)
            continue
        flush_list()
        paragraphs.append(text)
        elements.append({"kind": "paragraph", "text": text})
        raw_text_parts.append(text)

    flush_list()
    if unresolved_links:
        warnings.append("One or more DOCX hyperlinks could not be resolved to a target.")
        degradation_notes.append(
            "Relationship loss may hide source references that were present in the original document."
        )
    if not raw_text_parts:
        warnings.append("DOCX document did not yield any extractable text.")
        degradation_notes.append(
            "The document may be empty, image-based, or structurally malformed even if the container opened."
        )
    extraction_quality = {
        "state": "degraded" if warnings or not raw_text_parts else "clean",
        "score": 0.2 if not raw_text_parts else 0.72 if warnings else 0.96,
        "summary": (
            "DOCX extraction is degraded."
            if warnings or not raw_text_parts
            else "DOCX structure extracted cleanly."
        ),
    }

    return {
        "title": title or (paragraphs[0] if paragraphs else ""),
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "elements": elements,
        "links": links,
        "raw_text": "\n".join(raw_text_parts),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": extraction_quality,
    }
