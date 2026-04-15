from __future__ import annotations

from striprtf.striprtf import rtf_to_text

from papyrus.infrastructure.parsers.text_parser import parse_plain_text_content


def parse_rtf_bytes(payload: bytes) -> dict[str, object]:
    if not payload:
        extracted = ""
    else:
        try:
            extracted = rtf_to_text(payload.decode("latin-1"))
        except Exception as exc:  # pragma: no cover - striprtf exception types vary
            raise ValueError(f"malformed RTF: {exc}") from exc
    parsed = parse_plain_text_content(
        extracted,
        format_label="RTF",
        recover_title=True,
        default_dropped_features=["rich styling", "fonts", "embedded objects"],
    )
    parsed["downgraded_features"] = ["RTF styling reduced to readable text structure"]
    return parsed
