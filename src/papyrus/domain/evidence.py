from __future__ import annotations

from typing import Any


LOCAL_GOVERNED_REFERENCE_PREFIXES = (
    "knowledge/",
    "archive/knowledge/",
    "docs/",
    "decisions/",
)


def citation_is_local_governed_reference(source_ref: str) -> bool:
    normalized = str(source_ref or "").strip()
    return normalized.startswith(LOCAL_GOVERNED_REFERENCE_PREFIXES)


def citation_requires_capture_metadata(source_ref: str) -> bool:
    normalized = str(source_ref or "").strip()
    if normalized.startswith("migration/"):
        return True
    return not citation_is_local_governed_reference(normalized)


def default_citation_validity_status(source_ref: str) -> str:
    return "verified" if citation_is_local_governed_reference(source_ref) else "unverified"


def summarize_evidence_posture(citations: list[dict[str, Any]]) -> dict[str, Any]:
    total_citations = 0
    internal_reference_count = 0
    weak_external_evidence_count = 0
    captured_external_evidence_count = 0

    for citation in citations:
        if not isinstance(citation, dict):
            continue
        total_citations += 1
        source_ref = str(citation.get("source_ref") or "").strip()
        if citation_requires_capture_metadata(source_ref):
            if citation.get("captured_at") and citation.get("integrity_hash"):
                captured_external_evidence_count += 1
            else:
                weak_external_evidence_count += 1
            continue
        if citation_is_local_governed_reference(source_ref):
            internal_reference_count += 1

    if total_citations == 0:
        posture = "no_evidence"
    elif weak_external_evidence_count and (internal_reference_count or captured_external_evidence_count):
        posture = "mixed_support"
    elif weak_external_evidence_count:
        posture = "weak_external_only"
    elif captured_external_evidence_count and internal_reference_count:
        posture = "mixed_support"
    elif captured_external_evidence_count:
        posture = "captured_external_only"
    else:
        posture = "internal_reference_only"

    summary_parts: list[str] = []
    if internal_reference_count:
        summary_parts.append(
            f"{internal_reference_count} governed Papyrus reference"
            f"{'' if internal_reference_count == 1 else 's'}"
        )
    if captured_external_evidence_count:
        summary_parts.append(
            f"{captured_external_evidence_count} external/manual evidence item"
            f"{'' if captured_external_evidence_count == 1 else 's'} with capture metadata"
        )
    if weak_external_evidence_count:
        summary_parts.append(
            f"{weak_external_evidence_count} weak external/manual citation"
            f"{'' if weak_external_evidence_count == 1 else 's'}"
        )

    if summary_parts:
        summary = "; ".join(summary_parts)
    else:
        summary = "No evidence references recorded yet."

    return {
        "posture": posture,
        "total_citations": total_citations,
        "internal_reference_count": internal_reference_count,
        "weak_external_evidence_count": weak_external_evidence_count,
        "captured_external_evidence_count": captured_external_evidence_count,
        "summary": summary,
    }
