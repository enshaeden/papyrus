from __future__ import annotations

from lxml import etree, html

BLOCK_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "ul", "ol", "table"}
DROP_TAGS = {"script", "style", "nav", "header", "footer", "form", "noscript", "aside"}


def _inline_text(element: html.HtmlElement) -> str:
    return " ".join(part.strip() for part in element.itertext() if part.strip())


def _preformatted_text(element: html.HtmlElement) -> str:
    text = element.text_content().replace("\r\n", "\n").rstrip()
    return "\n".join(line.rstrip() for line in text.splitlines()).strip("\n")


def _table_rows(table: html.HtmlElement) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table.xpath("./thead/tr | ./tbody/tr | ./tr | .//tfoot/tr"):
        cells = [_inline_text(cell) for cell in row.xpath("./th | ./td")]
        if any(cells):
            rows.append(cells)
    return rows


def parse_html_bytes(payload: bytes) -> dict[str, object]:
    try:
        document = html.document_fromstring(payload)
    except (etree.ParserError, ValueError) as exc:
        raise ValueError(f"malformed HTML: {exc}") from exc

    for element in document.xpath(
        ".//*[self::script or self::style or self::nav or self::header or self::footer or self::form or self::noscript or self::aside]"
    ):
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)

    body = document.find("body")
    root = body if body is not None else document

    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[dict[str, object]] = []
    tables: list[list[list[str]]] = []
    preformatted_blocks: list[str] = []
    elements: list[dict[str, object]] = []
    links = [
        {"label": _inline_text(anchor), "target": str(anchor.get("href") or "").strip()}
        for anchor in root.xpath(".//a[@href]")
        if _inline_text(anchor) and str(anchor.get("href") or "").strip()
    ]
    page_title = (
        _inline_text(document.find(".//title")) if document.find(".//title") is not None else ""
    )

    def visit(node: html.HtmlElement) -> None:
        tag = node.tag.lower() if isinstance(node.tag, str) else ""
        if tag in DROP_TAGS:
            return
        if tag in BLOCK_TAGS:
            if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
                heading_text = _inline_text(node)
                if heading_text:
                    headings.append({"level": int(tag[1]), "text": heading_text})
                    elements.append({"kind": "heading", "level": int(tag[1]), "text": heading_text})
                return
            if tag == "p":
                paragraph_text = _inline_text(node)
                if paragraph_text:
                    paragraphs.append(paragraph_text)
                    elements.append({"kind": "paragraph", "text": paragraph_text})
                return
            if tag == "pre":
                block = _preformatted_text(node)
                if block.strip():
                    preformatted_blocks.append(block)
                    elements.append({"kind": "preformatted", "text": block})
                return
            if tag in {"ul", "ol"}:
                items = [_inline_text(item) for item in node.xpath("./li") if _inline_text(item)]
                if items:
                    ordered = tag == "ol"
                    lists.append({"items": items, "ordered": ordered})
                    elements.append(
                        {
                            "kind": "list",
                            "items": items,
                            "ordered": ordered,
                            "text": "\n".join(items),
                        }
                    )
                return
            if tag == "table":
                rows = _table_rows(node)
                if rows:
                    tables.append(rows)
                    elements.append(
                        {
                            "kind": "table",
                            "rows": rows,
                            "text": "\n".join(
                                " | ".join(cell for cell in row if cell) for row in rows
                            ),
                        }
                    )
                return
        for child in node:
            if isinstance(child, html.HtmlElement):
                visit(child)

    visit(root)
    title = (
        next(
            (
                str(heading.get("text") or "")
                for heading in headings
                if int(heading.get("level") or 1) == 1
            ),
            "",
        )
        or page_title
    )
    raw_text_parts = [title] if title else []
    raw_text_parts.extend(paragraphs)
    raw_text_parts.extend(item for block in lists for item in block["items"])
    raw_text_parts.extend(
        "\n".join(" | ".join(cell for cell in row if cell) for row in table) for table in tables
    )
    raw_text_parts.extend(preformatted_blocks)

    warnings: list[str] = []
    degradation_notes: list[str] = []
    if not raw_text_parts:
        warnings.append("HTML document did not yield any extractable text.")
        degradation_notes.append(
            "The document may be empty or dominated by scripts, navigation chrome, or unsupported layout."
        )

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "preformatted_blocks": preformatted_blocks,
        "elements": elements,
        "links": links,
        "raw_text": "\n\n".join(raw_text_parts).strip(),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": {
            "state": "degraded" if warnings or not raw_text_parts else "clean",
            "score": 0.2 if not raw_text_parts else 0.9,
            "summary": (
                "HTML extraction is degraded."
                if warnings or not raw_text_parts
                else "HTML semantic structure extracted cleanly."
            ),
        },
        "preserved_features": [
            "title" if title else "",
            "headings" if headings else "",
            "paragraphs" if paragraphs else "",
            "lists" if lists else "",
            "tables" if tables else "",
            "code or preformatted blocks" if preformatted_blocks else "",
            "links" if links else "",
        ],
        "downgraded_features": ["inline styling", "layout-driven visual structure"],
        "dropped_features": ["scripts", "styles", "navigation chrome", "forms"],
    }
