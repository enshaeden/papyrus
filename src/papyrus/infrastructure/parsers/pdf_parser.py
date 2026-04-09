from __future__ import annotations

import re


TEXT_TOKEN_PATTERN = re.compile(rb"\(([^()]*)\)\s*Tj")


def _decode_pdf_string(payload: bytes) -> str:
    text = payload.replace(rb"\(", b"(").replace(rb"\)", b")").replace(rb"\n", b"\n")
    try:
        return text.decode("utf-8")
    except UnicodeDecodeError:
        return text.decode("latin-1", errors="ignore")


def parse_pdf_bytes(payload: bytes) -> dict[str, object]:
    fragments = [_decode_pdf_string(match) for match in TEXT_TOKEN_PATTERN.findall(payload)]
    paragraphs = [fragment.strip() for fragment in fragments if fragment.strip()]
    title = paragraphs[0] if paragraphs else ""
    return {
        "title": title,
        "headings": [{"level": 1, "text": title}] if title else [],
        "paragraphs": paragraphs,
        "lists": [],
        "tables": [],
        "links": [],
        "raw_text": "\n".join(paragraphs),
    }
