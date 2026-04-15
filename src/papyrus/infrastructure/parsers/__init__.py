from importlib import import_module

from papyrus.infrastructure.parsers.models import (
    EmptyImportExtractionError,
    ImportFormatError,
    ImportMimeMismatchError,
    ImportParseResult,
    ImportParserFailureError,
    NormalizedElement,
    NormalizedImportDocument,
    UnsupportedImportFormatError,
)
from papyrus.infrastructure.parsers.normalization import normalize_parsed_content, table_text
from papyrus.infrastructure.parsers.registry import (
    FORMAT_REGISTRY,
    parse_import_document,
    resolve_import_format,
    supported_import_accept_attribute,
    supported_import_extensions,
    supported_import_labels,
)

_LAZY_EXPORTS = {
    "parse_csv_bytes": ("papyrus.infrastructure.parsers.csv_parser", "parse_csv_bytes"),
    "parse_docx_bytes": ("papyrus.infrastructure.parsers.docx_parser", "parse_docx_bytes"),
    "parse_html_bytes": ("papyrus.infrastructure.parsers.html_parser", "parse_html_bytes"),
    "parse_markdown_bytes": (
        "papyrus.infrastructure.parsers.markdown_parser",
        "parse_markdown_bytes",
    ),
    "parse_odt_bytes": ("papyrus.infrastructure.parsers.odt_parser", "parse_odt_bytes"),
    "parse_pdf_bytes": ("papyrus.infrastructure.parsers.pdf_parser", "parse_pdf_bytes"),
    "parse_rst_bytes": ("papyrus.infrastructure.parsers.rst_parser", "parse_rst_bytes"),
    "parse_rtf_bytes": ("papyrus.infrastructure.parsers.rtf_parser", "parse_rtf_bytes"),
    "parse_text_bytes": ("papyrus.infrastructure.parsers.text_parser", "parse_text_bytes"),
}


def __getattr__(name: str):
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attribute_name = target
    module = import_module(module_name)
    return getattr(module, attribute_name)


__all__ = [
    "FORMAT_REGISTRY",
    "EmptyImportExtractionError",
    "ImportFormatError",
    "ImportMimeMismatchError",
    "ImportParseResult",
    "ImportParserFailureError",
    "NormalizedElement",
    "NormalizedImportDocument",
    "UnsupportedImportFormatError",
    "normalize_parsed_content",
    "parse_csv_bytes",
    "parse_docx_bytes",
    "parse_html_bytes",
    "parse_import_document",
    "parse_markdown_bytes",
    "parse_odt_bytes",
    "parse_pdf_bytes",
    "parse_rst_bytes",
    "parse_rtf_bytes",
    "parse_text_bytes",
    "resolve_import_format",
    "supported_import_accept_attribute",
    "supported_import_extensions",
    "supported_import_labels",
    "table_text",
]
