from __future__ import annotations

from io import BytesIO

from odf.namespaces import TABLENS, TEXTNS
from odf.opendocument import load
from odf.teletype import extractText
from odf.text import A


def _qname(node) -> tuple[str, str] | None:
    qname = getattr(node, "qname", None)
    if isinstance(qname, tuple) and len(qname) == 2:
        return str(qname[0]), str(qname[1])
    return None


def _outline_level(node) -> int:
    try:
        value = node.getAttribute("outlinelevel")
    except Exception:  # pragma: no cover - odfpy attribute access can vary
        value = None
    try:
        return max(1, int(value or 1))
    except (TypeError, ValueError):
        return 1


def parse_odt_bytes(payload: bytes) -> dict[str, object]:
    try:
        document = load(BytesIO(payload))
    except Exception as exc:  # pragma: no cover - odfpy exception types vary
        raise ValueError(f"malformed ODT: {exc}") from exc

    text_root = getattr(document, "text", None)
    if text_root is None or not getattr(text_root, "childNodes", None):
        raise ValueError("malformed ODT: missing document body")

    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[dict[str, object]] = []
    tables: list[list[list[str]]] = []
    elements: list[dict[str, object]] = []
    title = ""

    def visit(nodes) -> None:
        nonlocal title
        for node in nodes:
            qname = _qname(node)
            if qname is None:
                continue
            namespace, localname = qname
            if namespace == TEXTNS and localname == "h":
                heading_text = extractText(node).strip()
                if not heading_text:
                    continue
                level = _outline_level(node)
                headings.append({"level": level, "text": heading_text})
                elements.append({"kind": "heading", "level": level, "text": heading_text})
                if not title and level == 1:
                    title = heading_text
                continue
            if namespace == TEXTNS and localname == "p":
                paragraph_text = extractText(node).strip()
                if paragraph_text:
                    paragraphs.append(paragraph_text)
                    elements.append({"kind": "paragraph", "text": paragraph_text})
                continue
            if namespace == TEXTNS and localname == "list":
                items: list[str] = []
                for child in getattr(node, "childNodes", []):
                    child_qname = _qname(child)
                    if child_qname != (TEXTNS, "list-item"):
                        continue
                    item_text = extractText(child).strip()
                    if item_text:
                        items.append(item_text)
                if items:
                    lists.append({"items": items, "ordered": False})
                    elements.append({"kind": "list", "items": items, "ordered": False, "text": "\n".join(items)})
                continue
            if namespace == TABLENS and localname == "table":
                rows: list[list[str]] = []
                for row in getattr(node, "childNodes", []):
                    if _qname(row) != (TABLENS, "table-row"):
                        continue
                    cells: list[str] = []
                    for cell in getattr(row, "childNodes", []):
                        if _qname(cell) not in {(TABLENS, "table-cell"), (TABLENS, "covered-table-cell")}:
                            continue
                        cells.append(extractText(cell).strip())
                    if any(cells):
                        rows.append(cells)
                if rows:
                    tables.append(rows)
                    elements.append(
                        {
                            "kind": "table",
                            "rows": rows,
                            "text": "\n".join(" | ".join(cell for cell in row if cell) for row in rows),
                        }
                    )
                continue
            visit(getattr(node, "childNodes", []))

    visit(text_root.childNodes)
    links = []
    for anchor in text_root.getElementsByType(A):
        label = extractText(anchor).strip()
        try:
            target = str(anchor.getAttribute("href") or "").strip()
        except Exception:  # pragma: no cover - odfpy attribute access can vary
            target = ""
        if label and target:
            links.append({"label": label, "target": target})

    raw_text_parts = [heading["text"] for heading in headings]
    raw_text_parts.extend(paragraphs)
    raw_text_parts.extend(item for block in lists for item in block["items"])
    raw_text_parts.extend(
        "\n".join(" | ".join(cell for cell in row if cell) for row in table) for table in tables
    )
    warnings: list[str] = []
    degradation_notes: list[str] = []
    if not raw_text_parts:
        warnings.append("ODT document did not yield any extractable text.")
        degradation_notes.append(
            "The document may be empty or structurally malformed even if the package opened."
        )

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": tables,
        "preformatted_blocks": [],
        "elements": elements,
        "links": links,
        "raw_text": "\n\n".join(raw_text_parts).strip(),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": {
            "state": "degraded" if warnings or not raw_text_parts else "clean",
            "score": 0.2 if not raw_text_parts else 0.9,
            "summary": (
                "ODT extraction is degraded."
                if warnings or not raw_text_parts
                else "ODT structure extracted cleanly."
            ),
        },
        "preserved_features": [
            "headings" if headings else "",
            "paragraphs" if paragraphs else "",
            "lists" if lists else "",
            "tables" if tables else "",
            "links" if links else "",
        ],
        "downgraded_features": ["document styling"],
        "dropped_features": ["decorative formatting", "embedded media"],
    }
