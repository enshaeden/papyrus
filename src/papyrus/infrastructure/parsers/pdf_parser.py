from __future__ import annotations

import re
import zlib

STREAM_PATTERN = re.compile(
    rb"<<(?P<dictionary>.*?)>>\s*stream\r?\n(?P<data>.*?)\r?\nendstream", re.DOTALL
)
TEXT_SHOW_PATTERN = re.compile(rb"(?P<operand>\((?:\\.|[^\\()])*\)|<[\da-fA-F\s]*>)\s*(?:Tj|'|\")")
TEXT_ARRAY_PATTERN = re.compile(rb"\[(?P<items>.*?)\]\s*TJ", re.DOTALL)
STRING_TOKEN_PATTERN = re.compile(rb"\((?:\\.|[^\\()])*\)|<[\da-fA-F\s]*>")


def _decode_pdf_text(payload: bytes) -> str:
    if not payload:
        return ""
    utf16_be_bom = b"\xfe\xff"
    if payload.startswith(utf16_be_bom):
        try:
            return payload[len(utf16_be_bom) :].decode("utf-16-be")
        except UnicodeDecodeError:
            pass
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return payload.decode("latin-1", errors="ignore")


def _decode_pdf_literal(payload: bytes) -> str:
    decoded = bytearray()
    index = 0
    while index < len(payload):
        byte = payload[index]
        if byte != 0x5C:
            decoded.append(byte)
            index += 1
            continue
        index += 1
        if index >= len(payload):
            break
        escaped = payload[index]
        mapping = {
            ord("n"): b"\n",
            ord("r"): b"\r",
            ord("t"): b"\t",
            ord("b"): b"\b",
            ord("f"): b"\f",
            ord("("): b"(",
            ord(")"): b")",
            ord("\\"): b"\\",
        }
        if escaped in mapping:
            decoded.extend(mapping[escaped])
            index += 1
            continue
        if escaped in b"\r\n":
            if (
                escaped == ord("\r")
                and index + 1 < len(payload)
                and payload[index + 1] == ord("\n")
            ):
                index += 2
            else:
                index += 1
            continue
        if 48 <= escaped <= 55:
            octal = bytes([escaped])
            index += 1
            for _ in range(2):
                if index < len(payload) and 48 <= payload[index] <= 55:
                    octal += bytes([payload[index]])
                    index += 1
                else:
                    break
            decoded.append(int(octal, 8))
            continue
        decoded.append(escaped)
        index += 1
    return _decode_pdf_text(bytes(decoded))


def _decode_pdf_hex(payload: bytes) -> str:
    cleaned = re.sub(rb"\s+", b"", payload)
    if not cleaned:
        return ""
    if len(cleaned) % 2 == 1:
        cleaned += b"0"
    try:
        return _decode_pdf_text(bytes.fromhex(cleaned.decode("ascii")))
    except ValueError:
        return ""


def _decode_pdf_token(token: bytes) -> str:
    if token.startswith(b"(") and token.endswith(b")"):
        return _decode_pdf_literal(token[1:-1]).strip()
    if token.startswith(b"<") and token.endswith(b">"):
        return _decode_pdf_hex(token[1:-1]).strip()
    return ""


def _extract_fragments(source: bytes) -> list[str]:
    fragments: list[tuple[int, str]] = []
    for match in TEXT_SHOW_PATTERN.finditer(source):
        text = _decode_pdf_token(match.group("operand"))
        if text:
            fragments.append((match.start(), text))
    for match in TEXT_ARRAY_PATTERN.finditer(source):
        parts = [
            _decode_pdf_token(token) for token in STRING_TOKEN_PATTERN.findall(match.group("items"))
        ]
        text = "".join(part for part in parts if part).strip()
        if text:
            fragments.append((match.start(), text))
    fragments.sort(key=lambda item: item[0])
    return [fragment for _, fragment in fragments]


def _text_sources(payload: bytes) -> tuple[list[bytes], list[str]]:
    sources: list[bytes] = []
    warnings: list[str] = []
    for match in STREAM_PATTERN.finditer(payload):
        source = match.group("data")
        dictionary = match.group("dictionary")
        if b"/FlateDecode" in dictionary:
            try:
                source = zlib.decompress(source)
            except zlib.error:
                warnings.append(
                    "One or more compressed PDF streams could not be decompressed. Extraction may be incomplete."
                )
                continue
        sources.append(source)
    if not sources:
        sources.append(payload)
    return sources, warnings


def parse_pdf_bytes(payload: bytes) -> dict[str, object]:
    if not payload.startswith(b"%PDF"):
        raise ValueError("malformed PDF: missing %PDF header")
    warnings: list[str] = []
    degradation_notes: list[str] = []
    sources, source_warnings = _text_sources(payload)
    warnings.extend(source_warnings)
    fragments: list[str] = []
    for source in sources:
        extracted = _extract_fragments(source)
        if extracted:
            fragments.extend(extracted)
    paragraphs = [fragment.strip() for fragment in fragments if fragment.strip()]
    if not paragraphs:
        warnings.append(
            "No extractable PDF text found. Papyrus currently supports text-based PDFs with simple text operators only."
        )
        degradation_notes.append(
            "Scanned, image-only, encrypted, or heavily font-encoded PDFs require external OCR or preprocessing."
        )
    elif len("\n".join(paragraphs)) < 40:
        warnings.append("Extracted PDF text is low-signal and may be incomplete.")
        degradation_notes.append(
            "Complex layout, unsupported encodings, or fragmented content streams may have reduced extraction quality."
        )
    title = paragraphs[0] if paragraphs else ""
    extraction_quality = {
        "state": "degraded" if warnings or not paragraphs else "clean",
        "score": 0.15
        if not paragraphs
        else 0.45
        if len("\n".join(paragraphs)) < 40
        else 0.7
        if warnings
        else 0.85,
        "summary": (
            "PDF extraction is degraded."
            if warnings or not paragraphs
            else "PDF text extraction succeeded."
        ),
    }
    return {
        "title": title,
        "headings": [{"level": 1, "text": title}] if title else [],
        "paragraphs": paragraphs,
        "lists": [],
        "tables": [],
        "preformatted_blocks": [],
        "elements": [{"kind": "paragraph", "text": paragraph} for paragraph in paragraphs],
        "links": [],
        "raw_text": "\n".join(paragraphs),
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": extraction_quality,
        "preserved_features": ["paragraphs" if paragraphs else ""],
        "downgraded_features": ["layout", "heading structure", "tables", "list semantics"],
        "dropped_features": ["images", "annotations", "page chrome"],
    }
