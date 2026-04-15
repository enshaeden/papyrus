from __future__ import annotations

import csv
from io import StringIO

from papyrus.infrastructure.parsers.text_parser import decode_text_bytes


def parse_csv_bytes(payload: bytes) -> dict[str, object]:
    text, warnings, degradation_notes = decode_text_bytes(payload, format_label="CSV")
    try:
        rows = [
            [str(cell).strip() for cell in row]
            for row in csv.reader(StringIO(text))
            if any(str(cell).strip() for cell in row)
        ]
    except csv.Error as exc:
        raise ValueError(f"malformed CSV: {exc}") from exc

    elements: list[dict[str, object]] = []
    raw_text = ""
    if rows:
        raw_text = "\n".join(" | ".join(cell for cell in row if cell) for row in rows)
        elements.append({"kind": "table", "rows": rows, "text": raw_text})
    else:
        warnings.append("CSV document did not yield any readable rows.")
        degradation_notes.append(
            "The file may be empty or contain delimiters without readable cell content."
        )

    title = rows[0][0] if len(rows) == 1 and len(rows[0]) == 1 else ""
    return {
        "title": title,
        "headings": [{"level": 1, "text": title}] if title else [],
        "paragraphs": [],
        "lists": [],
        "tables": [rows] if rows else [],
        "preformatted_blocks": [],
        "elements": elements,
        "links": [],
        "raw_text": raw_text,
        "parser_warnings": warnings,
        "degradation_notes": degradation_notes,
        "extraction_quality": {
            "state": "degraded" if warnings or not rows else "clean",
            "score": 0.2 if not rows else 0.86,
            "summary": (
                "CSV extraction is degraded."
                if warnings or not rows
                else "CSV rows normalized as readable table text."
            ),
        },
        "preserved_features": ["simple table rows"] if rows else [],
        "downgraded_features": ["cell typing", "column formatting", "spreadsheet semantics"],
        "dropped_features": ["formulas", "multiple-sheet workbook behavior"],
    }
