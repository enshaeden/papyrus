from __future__ import annotations

import re

LIST_PATTERN = re.compile(r"^\s*(?:[-*+•]|\d+[.)])\s+(.*)$")
FENCE_PATTERN = re.compile(r"^\s*```")
TITLE_CANDIDATE_PATTERN = re.compile(r"^[A-Z0-9][^\n]{0,79}$")


def decode_text_bytes(payload: bytes, *, format_label: str) -> tuple[str, list[str], list[str]]:
    warnings: list[str] = []
    degradation_notes: list[str] = []
    if not payload:
        return "", warnings, degradation_notes
    try:
        return payload.decode("utf-8-sig"), warnings, degradation_notes
    except UnicodeDecodeError:
        text = payload.decode("utf-8", errors="replace")
        warnings.append(
            f"{format_label} contained invalid UTF-8 bytes. Replacement characters were inserted during parsing."
        )
        degradation_notes.append(
            "Character decoding loss may reduce classification or mapping quality."
        )
        return text, warnings, degradation_notes


def _strong_title_candidate(first_block: str) -> str:
    candidate = first_block.strip()
    if not candidate or "\n" in candidate:
        return ""
    if not TITLE_CANDIDATE_PATTERN.match(candidate):
        return ""
    if candidate.endswith((".", "?", "!", ";")):
        return ""
    return candidate


def parse_plain_text_content(
    text: str,
    *,
    format_label: str,
    recover_title: bool,
    default_dropped_features: list[str] | None = None,
) -> dict[str, object]:
    headings: list[dict[str, object]] = []
    paragraphs: list[str] = []
    lists: list[dict[str, object]] = []
    preformatted_blocks: list[str] = []
    elements: list[dict[str, object]] = []
    warnings: list[str] = []
    degradation_notes: list[str] = []
    current_paragraph: list[str] = []
    current_list: list[str] = []
    current_list_is_ordered = False
    current_preformatted: list[str] = []
    in_fence = False

    def flush_paragraph() -> None:
        nonlocal current_paragraph
        if current_paragraph:
            paragraph_text = " ".join(line.strip() for line in current_paragraph).strip()
            if paragraph_text:
                paragraphs.append(paragraph_text)
                elements.append({"kind": "paragraph", "text": paragraph_text})
            current_paragraph = []

    def flush_list() -> None:
        nonlocal current_list, current_list_is_ordered
        if current_list:
            items = [item.strip() for item in current_list if item.strip()]
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
        line = raw_line.rstrip("\r")
        stripped = line.strip()
        if FENCE_PATTERN.match(line):
            flush_paragraph()
            flush_list()
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
        if list_match := LIST_PATTERN.match(line):
            flush_paragraph()
            list_item = list_match.group(1).strip()
            current_list.append(list_item)
            current_list_is_ordered = bool(re.match(r"^\s*\d+[.)]\s+", line))
            continue
        flush_list()
        current_paragraph.append(stripped)

    flush_preformatted()
    flush_list()
    flush_paragraph()

    title = ""
    if recover_title:
        first_block = next(
            (
                element.get("text", "")
                for element in elements
                if str(element.get("kind") or "") in {"paragraph", "preformatted"}
            ),
            "",
        )
        title = _strong_title_candidate(str(first_block))
        if title:
            headings.append({"level": 1, "text": title})
            elements.insert(0, {"kind": "heading", "level": 1, "text": title})

    raw_text_parts = [heading["text"] for heading in headings]
    raw_text_parts.extend(paragraphs)
    raw_text_parts.extend(item for block in lists for item in block["items"])
    raw_text_parts.extend(preformatted_blocks)
    if not raw_text_parts:
        warnings.append(f"{format_label} did not yield any extractable text.")
        degradation_notes.append(
            "The file can be stored, but downstream classification and mapping would have little or no source signal."
        )

    preserved = ["paragraphs"]
    if headings:
        preserved.append("recovered title")
    if lists:
        preserved.append("lists")
    if preformatted_blocks:
        preserved.append("code or preformatted blocks")

    return {
        "title": title,
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
        "tables": [],
        "preformatted_blocks": preformatted_blocks,
        "elements": elements,
        "links": [],
        "raw_text": "\n\n".join(raw_text_parts).strip(),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": {
            "state": "degraded" if warnings or not raw_text_parts else "clean",
            "score": 0.25 if not raw_text_parts else 0.88,
            "summary": (
                f"{format_label} extraction is degraded."
                if warnings or not raw_text_parts
                else f"{format_label} structure extracted cleanly."
            ),
        },
        "preserved_features": preserved,
        "downgraded_features": ["section hierarchy inferred only where obvious"]
        if recover_title
        else [],
        "dropped_features": default_dropped_features or ["rich styling"],
    }


def parse_text_bytes(payload: bytes) -> dict[str, object]:
    text, warnings, degradation_notes = decode_text_bytes(payload, format_label="Plain text")
    parsed = parse_plain_text_content(
        text,
        format_label="Plain text",
        recover_title=True,
        default_dropped_features=["rich styling", "embedded media"],
    )
    parsed["parser_warnings"] = warnings + list(parsed.get("parser_warnings", []))
    parsed["degradation_notes"] = degradation_notes + list(parsed.get("degradation_notes", []))
    if not parsed.get("raw_text"):
        parsed["extraction_quality"] = {
            "state": "degraded",
            "score": 0.2,
            "summary": "Plain text extraction is degraded.",
        }
    return parsed
