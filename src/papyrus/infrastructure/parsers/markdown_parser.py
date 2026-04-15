from __future__ import annotations

import re

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_PATTERN = re.compile(r"^\s*(?:[-*]|\d+\.)\s+(.*)$")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^\s*```")


def parse_markdown_bytes(payload: bytes) -> dict[str, object]:
    warnings: list[str] = []
    degradation_notes: list[str] = []
    if not payload:
        text = ""
        warnings.append("Markdown file is empty.")
        degradation_notes.append(
            "No headings, paragraphs, list items, or code blocks were available to classify or map."
        )
    else:
        try:
            text = payload.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = payload.decode("utf-8", errors="replace")
            warnings.append(
                "Markdown contained invalid UTF-8 bytes. Replacement characters were inserted during parsing."
            )
            degradation_notes.append(
                "Character decoding loss may reduce classification or mapping quality."
            )
    title = ""
    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[dict[str, object]] = []
    preformatted_blocks: list[str] = []
    elements: list[dict[str, object]] = []
    links: list[dict[str, str]] = []
    current_list: list[str] = []
    current_paragraph: list[str] = []
    current_preformatted: list[str] = []
    current_list_is_ordered = False
    in_fence = False

    def flush_paragraph() -> None:
        nonlocal current_paragraph
        if current_paragraph:
            paragraph_text = " ".join(current_paragraph).strip()
            paragraphs.append(paragraph_text)
            elements.append({"kind": "paragraph", "text": paragraph_text})
            current_paragraph = []

    def flush_list() -> None:
        nonlocal current_list, current_list_is_ordered
        if current_list:
            items = [item for item in current_list if item]
            if items:
                lists.append({"items": items, "ordered": current_list_is_ordered})
                elements.append(
                    {
                        "kind": "list",
                        "items": items,
                        "ordered": current_list_is_ordered,
                        "text": "\n".join(items),
                    }
                )
            current_list = []
            current_list_is_ordered = False

    def flush_preformatted() -> None:
        nonlocal current_preformatted
        if current_preformatted:
            block = "\n".join(current_preformatted).rstrip()
            if block.strip():
                preformatted_blocks.append(block)
                elements.append({"kind": "preformatted", "text": block})
            current_preformatted = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if FENCE_PATTERN.match(line):
            flush_list()
            flush_paragraph()
            if in_fence:
                flush_preformatted()
                in_fence = False
            else:
                flush_preformatted()
                in_fence = True
            continue
        if in_fence:
            current_preformatted.append(line)
            continue
        if not stripped:
            flush_preformatted()
            flush_list()
            flush_paragraph()
            continue
        if line.startswith(("    ", "\t")):
            flush_paragraph()
            flush_list()
            current_preformatted.append(line[4:] if line.startswith("    ") else line.lstrip("\t"))
            continue
        flush_preformatted()
        if heading_match := HEADING_PATTERN.match(line):
            flush_list()
            flush_paragraph()
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            headings.append({"level": level, "text": heading_text})
            elements.append({"kind": "heading", "level": level, "text": heading_text})
            if not title and level == 1:
                title = heading_text
            links.extend(
                {"label": label, "target": target}
                for label, target in LINK_PATTERN.findall(heading_text)
            )
            continue
        if list_match := LIST_PATTERN.match(line):
            flush_paragraph()
            current_list.append(list_match.group(1).strip())
            if len(current_list) == 1:
                current_list_is_ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            links.extend(
                {"label": label, "target": target}
                for label, target in LINK_PATTERN.findall(current_list[-1])
            )
            continue
        flush_list()
        current_paragraph.append(stripped)
        links.extend(
            {"label": label, "target": target} for label, target in LINK_PATTERN.findall(stripped)
        )
    flush_paragraph()
    flush_list()
    flush_preformatted()
    raw_text_parts = [heading["text"] for heading in headings]
    raw_text_parts.extend(paragraphs)
    raw_text_parts.extend(item for block in lists for item in block["items"])
    raw_text_parts.extend(preformatted_blocks)
    if not raw_text_parts:
        warnings.append("Markdown did not yield any extractable text.")
        degradation_notes.append(
            "The file can be stored, but downstream classification and mapping will have little or no source signal."
        )
    extraction_quality = {
        "state": "degraded" if warnings or not raw_text_parts else "clean",
        "score": 0.25 if not raw_text_parts else 0.75 if warnings else 0.98,
        "summary": (
            "Markdown extraction is degraded."
            if warnings or not raw_text_parts
            else "Markdown structure extracted cleanly."
        ),
    }

    return {
        "title": title or (headings[0]["text"] if headings else ""),
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": [],
        "preformatted_blocks": preformatted_blocks,
        "elements": elements,
        "links": links,
        "raw_text": "\n".join(raw_text_parts),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": extraction_quality,
        "preserved_features": [
            "headings" if headings else "",
            "paragraphs" if paragraphs else "",
            "lists" if lists else "",
            "links" if links else "",
            "code or preformatted blocks" if preformatted_blocks else "",
        ],
        "downgraded_features": ["inline styling"],
        "dropped_features": ["render-only layout details"],
    }
