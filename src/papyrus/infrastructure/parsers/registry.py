from __future__ import annotations

import mimetypes
from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module, util
from pathlib import Path
from typing import cast

from papyrus.infrastructure.parsers.models import (
    EmptyImportExtractionError,
    ImportMimeMismatchError,
    ImportParseResult,
    ImportParserFailureError,
    UnsupportedImportFormatError,
)
from papyrus.infrastructure.parsers.normalization import normalize_parsed_content

Parser = Callable[[bytes], dict[str, object]]

GENERIC_MEDIA_TYPES = {"", "application/octet-stream"}


@dataclass(frozen=True)
class ParserDependency:
    module_name: str
    package_name: str


@dataclass(frozen=True)
class ImportFormatDefinition:
    extension: str
    parser_name: str
    label: str
    media_types: tuple[str, ...]
    parser_module: str
    parser_symbol: str
    dependencies: tuple[ParserDependency, ...] = ()

    @property
    def accept_token(self) -> str:
        return self.extension

    @property
    def primary_media_type(self) -> str:
        return self.media_types[0]

    def missing_dependencies(self) -> tuple[str, ...]:
        missing: list[str] = []
        for dependency in self.dependencies:
            try:
                spec = util.find_spec(dependency.module_name)
            except (ImportError, AttributeError, ValueError):
                spec = None
            if spec is None:
                missing.append(dependency.package_name)
        return tuple(missing)

    def is_available(self) -> bool:
        return not self.missing_dependencies()

    def load_parser(self) -> Parser:
        module = import_module(self.parser_module)
        return cast(Parser, getattr(module, self.parser_symbol))


ALL_FORMAT_REGISTRY: tuple[ImportFormatDefinition, ...] = (
    ImportFormatDefinition(
        extension=".md",
        parser_name="markdown",
        label="Markdown",
        media_types=("text/markdown", "text/x-markdown", "text/plain"),
        parser_module="papyrus.infrastructure.parsers.markdown_parser",
        parser_symbol="parse_markdown_bytes",
    ),
    ImportFormatDefinition(
        extension=".markdown",
        parser_name="markdown",
        label="Markdown",
        media_types=("text/markdown", "text/x-markdown", "text/plain"),
        parser_module="papyrus.infrastructure.parsers.markdown_parser",
        parser_symbol="parse_markdown_bytes",
    ),
    ImportFormatDefinition(
        extension=".txt",
        parser_name="plain_text",
        label="Plain text",
        media_types=("text/plain",),
        parser_module="papyrus.infrastructure.parsers.text_parser",
        parser_symbol="parse_text_bytes",
    ),
    ImportFormatDefinition(
        extension=".rst",
        parser_name="rst",
        label="reStructuredText",
        media_types=("text/x-rst", "text/prs.fallenstein.rst", "text/plain"),
        parser_module="papyrus.infrastructure.parsers.rst_parser",
        parser_symbol="parse_rst_bytes",
        dependencies=(ParserDependency("docutils", "docutils"),),
    ),
    ImportFormatDefinition(
        extension=".rtf",
        parser_name="rtf",
        label="RTF",
        media_types=("application/rtf", "text/rtf", "text/richtext", "text/plain"),
        parser_module="papyrus.infrastructure.parsers.rtf_parser",
        parser_symbol="parse_rtf_bytes",
        dependencies=(ParserDependency("striprtf", "striprtf"),),
    ),
    ImportFormatDefinition(
        extension=".docx",
        parser_name="docx",
        label="DOCX",
        media_types=("application/vnd.openxmlformats-officedocument.wordprocessingml.document",),
        parser_module="papyrus.infrastructure.parsers.docx_parser",
        parser_symbol="parse_docx_bytes",
        dependencies=(ParserDependency("lxml", "lxml"),),
    ),
    ImportFormatDefinition(
        extension=".odt",
        parser_name="odt",
        label="ODT",
        media_types=("application/vnd.oasis.opendocument.text",),
        parser_module="papyrus.infrastructure.parsers.odt_parser",
        parser_symbol="parse_odt_bytes",
        dependencies=(ParserDependency("odf", "odfpy"),),
    ),
    ImportFormatDefinition(
        extension=".html",
        parser_name="html",
        label="HTML",
        media_types=("text/html", "application/xhtml+xml"),
        parser_module="papyrus.infrastructure.parsers.html_parser",
        parser_symbol="parse_html_bytes",
        dependencies=(ParserDependency("lxml", "lxml"),),
    ),
    ImportFormatDefinition(
        extension=".htm",
        parser_name="html",
        label="HTML",
        media_types=("text/html", "application/xhtml+xml"),
        parser_module="papyrus.infrastructure.parsers.html_parser",
        parser_symbol="parse_html_bytes",
        dependencies=(ParserDependency("lxml", "lxml"),),
    ),
    ImportFormatDefinition(
        extension=".csv",
        parser_name="csv",
        label="CSV",
        media_types=("text/csv", "application/csv", "text/plain", "application/vnd.ms-excel"),
        parser_module="papyrus.infrastructure.parsers.csv_parser",
        parser_symbol="parse_csv_bytes",
    ),
    ImportFormatDefinition(
        extension=".pdf",
        parser_name="pdf",
        label="PDF",
        media_types=("application/pdf",),
        parser_module="papyrus.infrastructure.parsers.pdf_parser",
        parser_symbol="parse_pdf_bytes",
    ),
)

FORMAT_REGISTRY: tuple[ImportFormatDefinition, ...] = tuple(
    entry for entry in ALL_FORMAT_REGISTRY if entry.is_available()
)

ALL_FORMAT_BY_EXTENSION = {entry.extension: entry for entry in ALL_FORMAT_REGISTRY}
FORMAT_BY_EXTENSION = {entry.extension: entry for entry in FORMAT_REGISTRY}


def supported_import_accept_attribute() -> str:
    return ",".join(entry.accept_token for entry in FORMAT_REGISTRY)


def supported_import_labels() -> tuple[str, ...]:
    labels: list[str] = []
    for entry in FORMAT_REGISTRY:
        if entry.label not in labels:
            labels.append(entry.label)
    return tuple(labels)


def supported_import_extensions() -> tuple[str, ...]:
    return tuple(entry.extension for entry in FORMAT_REGISTRY)


def _supported_extension_text() -> str:
    supported = ", ".join(supported_import_extensions())
    return supported or "[none]"


def _unavailable_format_error(definition: ImportFormatDefinition) -> UnsupportedImportFormatError:
    missing = definition.missing_dependencies()
    if missing:
        missing_list = ", ".join(missing)
        return UnsupportedImportFormatError(
            f"Import file type {definition.extension} is unavailable in this environment because "
            f"required parser dependencies are not installed: {missing_list}. Run ./scripts/bootstrap.sh "
            "or install the missing packages."
        )
    return UnsupportedImportFormatError(
        f"Import file type {definition.extension} is unavailable in this environment."
    )


def resolve_import_format(filename: str | Path) -> ImportFormatDefinition:
    suffix = Path(filename).suffix.lower()
    definition = ALL_FORMAT_BY_EXTENSION.get(suffix)
    if definition is None:
        supported = _supported_extension_text()
        raise UnsupportedImportFormatError(
            f"Unsupported import file type: {suffix or '[no extension]'}. Supported types: {supported}."
        )
    if not definition.is_available():
        raise _unavailable_format_error(definition)
    return definition


def _normalize_declared_media_type(media_type: str | None) -> str:
    return str(media_type or "").split(";", 1)[0].strip().lower()


def _resolved_media_type(file_path: str | Path, definition: ImportFormatDefinition) -> str:
    guessed, _ = mimetypes.guess_type(str(file_path))
    normalized = _normalize_declared_media_type(guessed)
    return normalized or definition.primary_media_type


def _validate_declared_media_type(
    *,
    definition: ImportFormatDefinition,
    declared_media_type: str,
) -> None:
    normalized = _normalize_declared_media_type(declared_media_type)
    if normalized in GENERIC_MEDIA_TYPES:
        return
    if normalized in {media_type.lower() for media_type in definition.media_types}:
        return
    allowed = ", ".join(definition.media_types)
    raise ImportMimeMismatchError(
        f"Declared media type {normalized} does not match {definition.extension}. Expected one of: {allowed}."
    )


def parse_import_document(
    *,
    file_path: str | Path,
    payload: bytes,
    declared_media_type: str | None = None,
) -> ImportParseResult:
    definition = resolve_import_format(file_path)
    normalized_declared_media_type = _normalize_declared_media_type(declared_media_type)
    _validate_declared_media_type(
        definition=definition,
        declared_media_type=normalized_declared_media_type,
    )
    try:
        parser = definition.load_parser()
    except ModuleNotFoundError as exc:
        raise _unavailable_format_error(definition) from exc
    try:
        parsed_content = parser(payload)
    except ValueError as exc:
        raise ImportParserFailureError(str(exc)) from exc
    normalized_document = normalize_parsed_content(
        parsed_content=parsed_content,
        detected_format=definition.label,
        declared_media_type=normalized_declared_media_type,
        media_type=_resolved_media_type(file_path, definition),
    )
    if not normalized_document.raw_text.strip():
        raise EmptyImportExtractionError(
            f"{definition.label} import did not yield any readable text. No import draft was created."
        )
    return ImportParseResult(
        parser_name=definition.parser_name,
        format_label=definition.label,
        media_type=normalized_document.media_type,
        declared_media_type=normalized_document.declared_media_type,
        parsed_content=parsed_content,
        normalized_document=normalized_document,
    )
