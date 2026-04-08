from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

from papyrus.interfaces.web.view_helpers import parse_csvish, parse_multiline


COMMON_FIELDS = (
    "title",
    "summary",
    "status",
    "owner",
    "team",
    "review_cadence",
    "audience",
    "systems",
    "tags",
    "related_services",
    "related_object_ids",
    "change_summary",
)


@dataclass(frozen=True)
class RevisionFormResult:
    values: dict[str, str]
    errors: dict[str, list[str]]
    cleaned_data: dict[str, Any]

    @property
    def is_valid(self) -> bool:
        return not self.errors


def _metadata_value(metadata: dict[str, Any], key: str, fallback: str = "") -> str:
    value = metadata.get(key, fallback)
    if isinstance(value, list):
        return "\n".join(str(item) for item in value if str(item).strip())
    if value is None:
        return fallback
    return str(value)


def build_revision_defaults(detail: dict[str, Any]) -> dict[str, str]:
    object_info = detail["object"]
    metadata = detail.get("metadata") or {}
    revision = detail.get("current_revision")
    values = {
        "title": _metadata_value(metadata, "title", object_info["title"]),
        "summary": _metadata_value(metadata, "summary", object_info["summary"]),
        "status": _metadata_value(metadata, "status", object_info["status"]),
        "owner": _metadata_value(metadata, "owner", object_info["owner"]),
        "team": _metadata_value(metadata, "team", object_info["team"]),
        "review_cadence": _metadata_value(metadata, "review_cadence", object_info["review_cadence"]),
        "audience": _metadata_value(metadata, "audience", "service_desk"),
        "systems": _metadata_value(metadata, "systems"),
        "tags": _metadata_value(metadata, "tags"),
        "related_services": _metadata_value(metadata, "related_services"),
        "related_object_ids": _metadata_value(metadata, "related_object_ids"),
        "change_summary": "",
        "prerequisites": _metadata_value(metadata, "prerequisites"),
        "steps": _metadata_value(metadata, "steps"),
        "verification": _metadata_value(metadata, "verification"),
        "rollback": _metadata_value(metadata, "rollback"),
        "use_when": "",
        "boundaries_and_escalation": "",
        "related_knowledge_notes": "",
        "symptoms": _metadata_value(metadata, "symptoms"),
        "scope": _metadata_value(metadata, "scope"),
        "cause": _metadata_value(metadata, "cause"),
        "diagnostic_checks": _metadata_value(metadata, "diagnostic_checks"),
        "mitigations": _metadata_value(metadata, "mitigations"),
        "permanent_fix_status": _metadata_value(metadata, "permanent_fix_status", "unknown"),
        "detection_notes": "",
        "escalation_threshold": "",
        "evidence_notes": "",
        "service_name": _metadata_value(metadata, "service_name", object_info["title"]),
        "service_criticality": _metadata_value(metadata, "service_criticality", "not_classified"),
        "dependencies": _metadata_value(metadata, "dependencies"),
        "support_entrypoints": _metadata_value(metadata, "support_entrypoints"),
        "common_failure_modes": _metadata_value(metadata, "common_failure_modes"),
        "related_runbooks": _metadata_value(metadata, "related_runbooks"),
        "related_known_errors": _metadata_value(metadata, "related_known_errors"),
        "scope_notes": "",
        "operational_notes": "",
        "citation_1_source_title": "",
        "citation_1_source_type": "document",
        "citation_1_source_ref": "",
        "citation_1_note": "",
        "citation_2_source_title": "",
        "citation_2_source_type": "document",
        "citation_2_source_ref": "",
        "citation_2_note": "",
        "citation_3_source_title": "",
        "citation_3_source_type": "document",
        "citation_3_source_ref": "",
        "citation_3_note": "",
    }
    citations = detail.get("citations", [])
    for index, citation in enumerate(citations[:3], start=1):
        values[f"citation_{index}_source_title"] = str(citation["source_title"])
        values[f"citation_{index}_source_type"] = str(citation["source_type"])
        values[f"citation_{index}_source_ref"] = str(citation["source_ref"])
        values[f"citation_{index}_note"] = str(citation["note"] or "")
    if revision and revision["body_markdown"]:
        values["use_when"] = revision["body_markdown"]
    return values


def _citation_entries(values: dict[str, str]) -> list[dict[str, Any]]:
    citations: list[dict[str, Any]] = []
    for index in range(1, 4):
        source_title = values.get(f"citation_{index}_source_title", "").strip()
        source_type = values.get(f"citation_{index}_source_type", "document").strip() or "document"
        source_ref = values.get(f"citation_{index}_source_ref", "").strip()
        note = values.get(f"citation_{index}_note", "").strip()
        if not any([source_title, source_ref, note]):
            continue
        citations.append(
            {
                "source_title": source_title,
                "source_type": source_type,
                "source_ref": source_ref,
                "note": note or None,
                "claim_anchor": None,
                "excerpt": None,
                "captured_at": None,
                "validity_status": None,
                "integrity_hash": None,
            }
        )
    return citations


def _serialize_body(object_type: str, values: dict[str, str]) -> str:
    if object_type == "runbook":
        return (
            "## Use When\n\n"
            + values["use_when"].strip()
            + "\n\n## Boundaries And Escalation\n\n"
            + values["boundaries_and_escalation"].strip()
            + "\n\n## Related Knowledge Notes\n\n"
            + values["related_knowledge_notes"].strip()
        ).strip()
    if object_type == "known_error":
        return (
            "## Detection Notes\n\n"
            + values["detection_notes"].strip()
            + "\n\n## Escalation Threshold\n\n"
            + values["escalation_threshold"].strip()
            + "\n\n## Evidence Notes\n\n"
            + values["evidence_notes"].strip()
        ).strip()
    return (
        "## Scope\n\n"
        + values["scope_notes"].strip()
        + "\n\n## Operational Notes\n\n"
        + values["operational_notes"].strip()
        + "\n\n## Evidence Notes\n\n"
        + values["evidence_notes"].strip()
    ).strip()


def validate_revision_form(
    *,
    values: dict[str, str],
    object_detail: dict[str, Any],
    taxonomies: dict[str, dict[str, Any]],
    actor: str,
) -> RevisionFormResult:
    errors: dict[str, list[str]] = {}

    def add_error(field: str, message: str) -> None:
        errors.setdefault(field, []).append(message)

    object_type = object_detail["object"]["object_type"]
    for field in COMMON_FIELDS:
        if not values.get(field, "").strip():
            add_error(field, "This field is required.")

    if values.get("team", "") not in taxonomies["teams"]["allowed_values"]:
        add_error("team", "Choose a valid team.")
    if values.get("review_cadence", "") not in taxonomies["review_cadences"]["allowed_values"]:
        add_error("review_cadence", "Choose a valid review cadence.")
    if values.get("audience", "") not in taxonomies["audiences"]["allowed_values"]:
        add_error("audience", "Choose a valid audience.")
    if values.get("status", "") not in taxonomies["statuses"]["allowed_values"]:
        add_error("status", "Choose a valid status.")

    citations = _citation_entries(values)
    if not citations:
        add_error("citations", "At least one citation is required.")
    for index, citation in enumerate(citations, start=1):
        if not citation["source_title"]:
            add_error("citations", f"Citation {index} needs a source title.")
        if not citation["source_ref"]:
            add_error("citations", f"Citation {index} needs a source reference.")

    if object_type == "runbook":
        for field in ("prerequisites", "steps", "verification", "rollback", "use_when", "boundaries_and_escalation"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
    elif object_type == "known_error":
        for field in ("symptoms", "scope", "cause", "diagnostic_checks", "mitigations", "detection_notes", "escalation_threshold"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
        if values.get("permanent_fix_status", "") not in taxonomies["permanent_fix_status"]["allowed_values"]:
            add_error("permanent_fix_status", "Choose a valid permanent fix status.")
    else:
        for field in ("service_name", "dependencies", "support_entrypoints", "common_failure_modes", "scope_notes", "operational_notes"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
        if values.get("service_criticality", "") not in taxonomies["service_criticality"]["allowed_values"]:
            add_error("service_criticality", "Choose a valid service criticality.")

    metadata = object_detail.get("metadata") or {}
    today = dt.date.today().isoformat()
    related_services = parse_multiline(values.get("related_services", ""))
    related_object_ids = parse_multiline(values.get("related_object_ids", ""))
    payload: dict[str, Any] = {
        "id": object_detail["object"]["object_id"],
        "title": values["title"].strip(),
        "canonical_path": object_detail["object"]["canonical_path"],
        "summary": values["summary"].strip(),
        "knowledge_object_type": object_type,
        "legacy_article_type": metadata.get("legacy_article_type"),
        "status": values["status"].strip(),
        "owner": values["owner"].strip(),
        "source_type": str(metadata.get("source_type") or "native"),
        "source_system": str(metadata.get("source_system") or "repository"),
        "source_title": values["title"].strip(),
        "team": values["team"].strip(),
        "systems": parse_multiline(values["systems"]),
        "tags": parse_multiline(values["tags"]),
        "created": str(metadata.get("created") or object_detail["object"]["created_date"]),
        "updated": today,
        "last_reviewed": today,
        "review_cadence": values["review_cadence"].strip(),
        "audience": values["audience"].strip(),
        "citations": citations,
        "related_object_ids": related_object_ids,
        "superseded_by": metadata.get("superseded_by"),
        "replaced_by": metadata.get("replaced_by"),
        "retirement_reason": metadata.get("retirement_reason"),
        "services": related_services,
        "related_articles": related_object_ids,
        "references": [
            {"title": citation["source_title"], "path": citation["source_ref"], "note": citation.get("note")}
            for citation in citations
        ],
        "change_log": [
            *(metadata.get("change_log") if isinstance(metadata.get("change_log"), list) else []),
            {"date": today, "summary": values["change_summary"].strip() or "Structured revision update.", "author": actor.strip()},
        ],
    }

    if object_type == "runbook":
        payload.update(
            {
                "related_services": related_services,
                "prerequisites": parse_multiline(values["prerequisites"]),
                "steps": parse_multiline(values["steps"]),
                "verification": parse_multiline(values["verification"]),
                "rollback": parse_multiline(values["rollback"]),
            }
        )
    elif object_type == "known_error":
        payload.update(
            {
                "related_services": related_services,
                "symptoms": parse_multiline(values["symptoms"]),
                "scope": values["scope"].strip(),
                "cause": values["cause"].strip(),
                "diagnostic_checks": parse_multiline(values["diagnostic_checks"]),
                "mitigations": parse_multiline(values["mitigations"]),
                "permanent_fix_status": values["permanent_fix_status"].strip(),
            }
        )
    else:
        payload.update(
            {
                "service_name": values["service_name"].strip(),
                "service_criticality": values["service_criticality"].strip(),
                "dependencies": parse_multiline(values["dependencies"]),
                "support_entrypoints": parse_multiline(values["support_entrypoints"]),
                "common_failure_modes": parse_multiline(values["common_failure_modes"]),
                "related_runbooks": parse_multiline(values["related_runbooks"]),
                "related_known_errors": parse_multiline(values["related_known_errors"]),
            }
        )

    cleaned_data = {
        "normalized_payload": payload,
        "body_markdown": _serialize_body(object_type, values),
        "change_summary": values["change_summary"].strip() or None,
        "validation_findings": build_submission_findings(object_type=object_type, payload=payload),
    }
    return RevisionFormResult(values=values, errors=errors, cleaned_data=cleaned_data)


def build_submission_findings(*, object_type: str, payload: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    if not payload.get("citations"):
        findings.append("Missing supporting citations.")
    else:
        weak_count = sum(
            1
            for citation in payload["citations"]
            if not citation.get("captured_at") or not citation.get("integrity_hash")
        )
        if weak_count:
            findings.append(f"{weak_count} citation(s) are still in weak-evidence posture.")
    if object_type in {"runbook", "known_error"} and not payload.get("related_services"):
        findings.append("Related service links are missing.")
    if object_type == "service_record" and not payload.get("dependencies"):
        findings.append("Dependencies have not been documented.")
    if not payload.get("related_object_ids"):
        findings.append("No related knowledge objects were linked for impact tracing.")
    return findings
