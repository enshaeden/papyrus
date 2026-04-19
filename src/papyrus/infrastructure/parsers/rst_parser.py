from __future__ import annotations

from docutils import nodes  # type: ignore[import-untyped]
from docutils.core import publish_doctree  # type: ignore[import-untyped]

from papyrus.infrastructure.parsers.text_parser import decode_text_bytes


def _table_rows(table_node: nodes.table) -> list[list[str]]:
    rows: list[list[str]] = []
    for row in table_node.findall(nodes.row):
        cells: list[str] = []
        for entry in row.findall(nodes.entry):
            cell_text = entry.astext().strip()
            cells.append(cell_text)
        if any(cells):
            rows.append(cells)
    return rows


def parse_rst_bytes(payload: bytes) -> dict[str, object]:
    text, warnings, degradation_notes = decode_text_bytes(payload, format_label="reStructuredText")
    try:
        doctree = publish_doctree(source=text)
    except Exception as exc:  # pragma: no cover - docutils exception types vary
        raise ValueError(f"malformed reStructuredText: {exc}") from exc

    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[dict[str, object]] = []
    tables: list[list[list[str]]] = []
    preformatted_blocks: list[str] = []
    elements: list[dict[str, object]] = []
    links = [
        {"label": reference.astext().strip(), "target": str(reference.get("refuri") or "").strip()}
        for reference in doctree.findall(nodes.reference)
        if str(reference.get("refuri") or "").strip() and reference.astext().strip()
    ]
    title = ""

    def visit(node: nodes.Node, *, level: int = 1) -> None:
        nonlocal title
        if isinstance(node, nodes.section):
            section_title = next(
                (child for child in node.children if isinstance(child, nodes.title)),
                None,
            )
            if isinstance(section_title, nodes.title):
                heading_text = section_title.astext().strip()
                if heading_text:
                    headings.append({"level": level, "text": heading_text})
                    elements.append({"kind": "heading", "level": level, "text": heading_text})
                    if not title and level == 1:
                        title = heading_text
            for child in node.children:
                if isinstance(child, nodes.title):
                    continue
                visit(child, level=level + 1)
            return
        if isinstance(node, nodes.title):
            heading_text = node.astext().strip()
            if heading_text and not title:
                headings.append({"level": level, "text": heading_text})
                elements.append({"kind": "heading", "level": level, "text": heading_text})
                title = heading_text
            return
        if isinstance(node, nodes.subtitle):
            heading_text = node.astext().strip()
            if heading_text:
                headings.append({"level": level + 1, "text": heading_text})
                elements.append({"kind": "heading", "level": level + 1, "text": heading_text})
            return
        if isinstance(node, nodes.paragraph):
            if isinstance(node.parent, nodes.list_item | nodes.entry | nodes.caption):
                return
            paragraph_text = node.astext().strip()
            if paragraph_text:
                paragraphs.append(paragraph_text)
                elements.append({"kind": "paragraph", "text": paragraph_text})
            return
        if isinstance(node, nodes.bullet_list | nodes.enumerated_list):
            items = [
                item.astext().strip()
                for item in node.findall(nodes.list_item)
                if item.astext().strip()
            ]
            if items:
                ordered = isinstance(node, nodes.enumerated_list)
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
        if isinstance(node, nodes.literal_block):
            block = node.astext().rstrip()
            if block.strip():
                preformatted_blocks.append(block)
                elements.append({"kind": "preformatted", "text": block})
            return
        if isinstance(node, nodes.table):
            rows = _table_rows(node)
            if rows:
                tables.append(rows)
                elements.append(
                    {
                        "kind": "table",
                        "rows": rows,
                        "text": "\n".join(" | ".join(cell for cell in row if cell) for row in rows),
                    }
                )
            return
        if isinstance(node, nodes.document):
            for child in node.children:
                visit(child, level=level)
            return
        if isinstance(node, nodes.topic | nodes.sidebar | nodes.compound | nodes.block_quote):
            for child in node.children:
                visit(child, level=level)
            return

    visit(doctree, level=1)
    raw_text_parts = [heading["text"] for heading in headings]
    raw_text_parts.extend(paragraphs)
    raw_text_parts.extend(item for block in lists for item in block["items"])
    raw_text_parts.extend(
        "\n".join(" | ".join(cell for cell in row if cell) for row in table) for table in tables
    )
    raw_text_parts.extend(preformatted_blocks)
    if not raw_text_parts:
        warnings.append("reStructuredText document did not yield any extractable text.")
        degradation_notes.append(
            "The document may be empty or structurally invalid even if it parsed."
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
            "score": 0.2 if not raw_text_parts else 0.95,
            "summary": (
                "reStructuredText extraction is degraded."
                if warnings or not raw_text_parts
                else "reStructuredText structure extracted cleanly."
            ),
        },
        "preserved_features": [
            "headings",
            "paragraphs",
            "lists" if lists else "",
            "tables" if tables else "",
            "code or preformatted blocks" if preformatted_blocks else "",
        ],
        "downgraded_features": ["directive-specific styling"],
        "dropped_features": ["non-text presentation details"],
    }
