from __future__ import annotations

from dataclasses import dataclass, field


class ImportFormatError(ValueError):
    """Base class for import normalization failures."""


class UnsupportedImportFormatError(ImportFormatError):
    """Raised when a file extension is not supported by the import registry."""


class ImportMimeMismatchError(ImportFormatError):
    """Raised when an explicit media type contradicts a supported file extension."""


class ImportParserFailureError(ImportFormatError):
    """Raised when a format parser cannot read the supplied payload."""


class EmptyImportExtractionError(ImportFormatError):
    """Raised when normalization did not recover any readable text."""


@dataclass(frozen=True)
class NormalizedElement:
    kind: str
    text: str
    level: int | None = None
    items: tuple[str, ...] = ()
    rows: tuple[tuple[str, ...], ...] = ()
    ordered: bool | None = None

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "kind": self.kind,
            "text": self.text,
        }
        if self.level is not None:
            payload["level"] = self.level
        if self.items:
            payload["items"] = list(self.items)
        if self.rows:
            payload["rows"] = [list(row) for row in self.rows]
        if self.ordered is not None:
            payload["ordered"] = self.ordered
        return payload


@dataclass(frozen=True)
class NormalizedImportDocument:
    title: str
    headings: tuple[dict[str, object], ...]
    paragraphs: tuple[str, ...]
    lists: tuple[dict[str, object], ...]
    tables: tuple[tuple[tuple[str, ...], ...], ...]
    preformatted_blocks: tuple[str, ...]
    elements: tuple[NormalizedElement, ...]
    links: tuple[dict[str, str], ...]
    raw_text: str
    parser_warnings: tuple[str, ...]
    degradation_notes: tuple[str, ...]
    extraction_quality: dict[str, object]
    normalization_summary: dict[str, tuple[str, ...]] = field(default_factory=dict)
    detected_format: str = ""
    declared_media_type: str = ""
    media_type: str = ""

    def to_payload(self) -> dict[str, object]:
        return {
            "title": self.title,
            "headings": [dict(item) for item in self.headings],
            "paragraphs": list(self.paragraphs),
            "lists": [
                {
                    "items": list(item.get("items", ())),
                    "ordered": bool(item.get("ordered", False)),
                }
                for item in self.lists
            ],
            "tables": [[list(row) for row in table] for table in self.tables],
            "preformatted_blocks": list(self.preformatted_blocks),
            "elements": [element.to_payload() for element in self.elements],
            "links": [dict(item) for item in self.links],
            "raw_text": self.raw_text,
            "parser_warnings": list(self.parser_warnings),
            "degradation_notes": list(self.degradation_notes),
            "extraction_quality": dict(self.extraction_quality),
            "normalization_summary": {
                key: list(values) for key, values in self.normalization_summary.items()
            },
            "detected_format": self.detected_format,
            "declared_media_type": self.declared_media_type,
            "media_type": self.media_type,
        }


@dataclass(frozen=True)
class ImportParseResult:
    parser_name: str
    format_label: str
    media_type: str
    declared_media_type: str
    parsed_content: dict[str, object]
    normalized_document: NormalizedImportDocument
