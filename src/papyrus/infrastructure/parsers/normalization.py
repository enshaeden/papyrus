from __future__ import annotations

from typing import Any

from papyrus.infrastructure.parsers.models import NormalizedElement, NormalizedImportDocument


def table_text(rows: list[list[str]]) -> str:
    return "\n".join(
        " | ".join(cell for cell in row if cell) for row in rows if any(cell for cell in row)
    )


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _clean_text_list(items: object) -> list[str]:
    if not isinstance(items, list):
        return []
    cleaned: list[str] = []
    for item in items:
        text = _clean_text(item)
        if text:
            cleaned.append(text)
    return cleaned


def _normalized_lists(raw_lists: object) -> list[dict[str, object]]:
    if not isinstance(raw_lists, list):
        return []
    normalized: list[dict[str, object]] = []
    for entry in raw_lists:
        if isinstance(entry, dict):
            items = _clean_text_list(entry.get("items"))
            if items:
                normalized.append(
                    {
                        "items": items,
                        "ordered": bool(entry.get("ordered", False)),
                    }
                )
            continue
        if isinstance(entry, list):
            items = _clean_text_list(entry)
            if items:
                normalized.append({"items": items, "ordered": False})
    return normalized


def _normalized_tables(raw_tables: object) -> list[list[list[str]]]:
    if not isinstance(raw_tables, list):
        return []
    normalized: list[list[list[str]]] = []
    for raw_table in raw_tables:
        if not isinstance(raw_table, list):
            continue
        rows: list[list[str]] = []
        for raw_row in raw_table:
            if not isinstance(raw_row, list):
                continue
            row = [_clean_text(cell) for cell in raw_row]
            if any(row):
                rows.append(row)
        if rows:
            normalized.append(rows)
    return normalized


def _normalized_headings(raw_headings: object) -> list[dict[str, object]]:
    if not isinstance(raw_headings, list):
        return []
    headings: list[dict[str, object]] = []
    for raw_heading in raw_headings:
        if not isinstance(raw_heading, dict):
            continue
        text = _clean_text(raw_heading.get("text"))
        if not text:
            continue
        try:
            level = max(1, int(raw_heading.get("level") or 1))
        except (TypeError, ValueError):
            level = 1
        headings.append({"level": level, "text": text})
    return headings


def _normalized_preformatted(raw_preformatted: object) -> list[str]:
    return _clean_text_list(raw_preformatted)


def _sanitize_elements(parsed_content: dict[str, Any]) -> list[NormalizedElement]:
    raw_elements = parsed_content.get("elements")
    if not isinstance(raw_elements, list):
        return []
    sanitized: list[NormalizedElement] = []
    for element in raw_elements:
        if not isinstance(element, dict):
            continue
        kind = _clean_text(element.get("kind"))
        if kind == "heading":
            text = _clean_text(element.get("text"))
            if not text:
                continue
            try:
                level = max(1, int(element.get("level") or 1))
            except (TypeError, ValueError):
                level = 1
            sanitized.append(NormalizedElement(kind="heading", level=level, text=text))
            continue
        if kind == "paragraph":
            text = _clean_text(element.get("text"))
            if text:
                sanitized.append(NormalizedElement(kind="paragraph", text=text))
            continue
        if kind == "list":
            items = tuple(_clean_text_list(element.get("items")))
            if items:
                sanitized.append(
                    NormalizedElement(
                        kind="list",
                        text=_clean_text(element.get("text")) or "\n".join(items),
                        items=items,
                        ordered=bool(element.get("ordered", False)),
                    )
                )
            continue
        if kind == "table":
            raw_tables = _normalized_tables([element.get("rows")])
            if not raw_tables:
                continue
            rows = tuple(tuple(row) for row in raw_tables[0])
            sanitized.append(
                NormalizedElement(
                    kind="table",
                    text=_clean_text(element.get("text")) or table_text([list(row) for row in rows]),
                    rows=rows,
                )
            )
            continue
        if kind == "preformatted":
            text = str(element.get("text") or "").rstrip()
            if text.strip():
                sanitized.append(NormalizedElement(kind="preformatted", text=text))
    return sanitized


def _synthesized_elements(
    *,
    headings: list[dict[str, object]],
    paragraphs: list[str],
    lists: list[dict[str, object]],
    tables: list[list[list[str]]],
    preformatted_blocks: list[str],
) -> list[NormalizedElement]:
    synthesized: list[NormalizedElement] = []
    for heading in headings:
        synthesized.append(
            NormalizedElement(
                kind="heading",
                level=int(heading.get("level") or 1),
                text=str(heading.get("text") or ""),
            )
        )
    for paragraph in paragraphs:
        synthesized.append(NormalizedElement(kind="paragraph", text=paragraph))
    for list_block in lists:
        items = tuple(_clean_text_list(list_block.get("items")))
        if items:
            synthesized.append(
                NormalizedElement(
                    kind="list",
                    text="\n".join(items),
                    items=items,
                    ordered=bool(list_block.get("ordered", False)),
                )
            )
    for table in tables:
        rows = tuple(tuple(row) for row in table)
        if rows:
            synthesized.append(
                NormalizedElement(
                    kind="table",
                    text=table_text([list(row) for row in rows]),
                    rows=rows,
                )
            )
    for block in preformatted_blocks:
        synthesized.append(NormalizedElement(kind="preformatted", text=block))
    return synthesized


def normalize_parsed_content(
    *,
    parsed_content: dict[str, Any],
    detected_format: str,
    declared_media_type: str,
    media_type: str,
) -> NormalizedImportDocument:
    headings = _normalized_headings(parsed_content.get("headings"))
    paragraphs = _clean_text_list(parsed_content.get("paragraphs"))
    lists = _normalized_lists(parsed_content.get("lists"))
    tables = _normalized_tables(parsed_content.get("tables"))
    preformatted_blocks = _normalized_preformatted(
        parsed_content.get("preformatted_blocks") or parsed_content.get("preformatted")
    )
    links = tuple(
        {
            "label": _clean_text(item.get("label")),
            "target": _clean_text(item.get("target")),
        }
        for item in parsed_content.get("links", [])
        if isinstance(item, dict)
        and _clean_text(item.get("label"))
        and _clean_text(item.get("target"))
    )
    parser_warnings = tuple(_clean_text_list(parsed_content.get("parser_warnings")))
    degradation_notes = tuple(_clean_text_list(parsed_content.get("degradation_notes")))
    extraction_quality = (
        parsed_content.get("extraction_quality")
        if isinstance(parsed_content.get("extraction_quality"), dict)
        else {}
    )
    title = _clean_text(parsed_content.get("title"))
    if not title and headings:
        title = str(headings[0].get("text") or "")
    elements = _sanitize_elements(parsed_content)
    if not elements:
        elements = _synthesized_elements(
            headings=headings,
            paragraphs=paragraphs,
            lists=lists,
            tables=tables,
            preformatted_blocks=preformatted_blocks,
        )

    raw_text_parts = [title] if title else []
    raw_text_parts.extend(element.text for element in elements if element.text.strip())
    raw_text = _clean_text(parsed_content.get("raw_text")) or "\n\n".join(raw_text_parts).strip()

    preserved = tuple(_clean_text_list(parsed_content.get("preserved_features")))
    downgraded = tuple(_clean_text_list(parsed_content.get("downgraded_features")))
    dropped = tuple(_clean_text_list(parsed_content.get("dropped_features")))
    if not preserved:
        inferred_preserved: list[str] = []
        if headings:
            inferred_preserved.append("headings")
        if paragraphs:
            inferred_preserved.append("paragraphs")
        if lists:
            inferred_preserved.append("lists")
        if tables:
            inferred_preserved.append("tables")
        if preformatted_blocks:
            inferred_preserved.append("code or preformatted blocks")
        preserved = tuple(inferred_preserved)

    quality_state = _clean_text(extraction_quality.get("state")) or (
        "degraded" if parser_warnings else "clean"
    )
    quality_score = extraction_quality.get("score")
    try:
        normalized_score = float(quality_score) if quality_score is not None else None
    except (TypeError, ValueError):
        normalized_score = None
    quality_summary = _clean_text(extraction_quality.get("summary")) or (
        "Extraction quality is degraded."
        if quality_state == "degraded"
        else "Extraction quality is clean."
    )

    return NormalizedImportDocument(
        title=title,
        headings=tuple(headings),
        paragraphs=tuple(paragraphs),
        lists=tuple(
            {"items": tuple(item["items"]), "ordered": bool(item["ordered"])} for item in lists
        ),
        tables=tuple(tuple(tuple(row) for row in table) for table in tables),
        preformatted_blocks=tuple(preformatted_blocks),
        elements=tuple(elements),
        links=links,
        raw_text=raw_text,
        parser_warnings=parser_warnings,
        degradation_notes=degradation_notes,
        extraction_quality={
            "state": quality_state,
            "score": normalized_score
            if normalized_score is not None
            else (0.5 if parser_warnings else 1.0),
            "summary": quality_summary,
        },
        normalization_summary={
            "preserved": preserved,
            "downgraded": downgraded,
            "dropped": dropped,
        },
        detected_format=detected_format,
        declared_media_type=declared_media_type,
        media_type=media_type,
    )
