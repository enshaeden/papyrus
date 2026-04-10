from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass
from typing import Any

from papyrus.domain.evidence import (
    default_citation_validity_status,
    summarize_evidence_posture,
)
from papyrus.interfaces.web.view_helpers import parse_csvish, parse_multiline


COMMON_FIELDS = (
    "title",
    "summary",
    "object_lifecycle_state",
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

BODY_SECTION_PATTERN = re.compile(r"^## (?P<title>.+?)\n\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


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


def _body_sections(body_markdown: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in BODY_SECTION_PATTERN.finditer(str(body_markdown or "").strip())
    }


def _list_field(section_content: dict[str, Any], section_id: str, field_name: str, fallback: str = "") -> str:
    section = section_content.get(section_id, {})
    if isinstance(section, dict) and isinstance(section.get(field_name), list):
        return "\n".join(str(item) for item in section.get(field_name, []) if str(item).strip())
    return fallback


def _text_field(section_content: dict[str, Any], section_id: str, field_name: str, fallback: str = "") -> str:
    section = section_content.get(section_id, {})
    if isinstance(section, dict):
        value = section.get(field_name)
        if value is not None:
            return str(value)
    return fallback


def build_revision_defaults(detail: dict[str, Any]) -> dict[str, str]:
    object_info = detail["object"]
    metadata = detail.get("metadata") or {}
    revision = detail.get("current_revision")
    section_content = revision.get("section_content", {}) if isinstance(revision, dict) else {}
    body_sections = _body_sections(str(revision.get("body_markdown") or "")) if isinstance(revision, dict) else {}
    values = {
        "title": _metadata_value(metadata, "title", object_info["title"]),
        "summary": _metadata_value(metadata, "summary", object_info["summary"]),
        "object_lifecycle_state": _metadata_value(
            metadata,
            "object_lifecycle_state",
            object_info["object_lifecycle_state"],
        ),
        "owner": _metadata_value(metadata, "owner", object_info["owner"]),
        "team": _metadata_value(metadata, "team", object_info["team"]),
        "review_cadence": _metadata_value(metadata, "review_cadence", object_info["review_cadence"]),
        "audience": _metadata_value(metadata, "audience", "service_desk"),
        "systems": _metadata_value(metadata, "systems"),
        "tags": _metadata_value(metadata, "tags"),
        "related_services": _metadata_value(metadata, "related_services"),
        "related_object_ids": _metadata_value(metadata, "related_object_ids"),
        "change_summary": "",
        "prerequisites": _list_field(section_content, "prerequisites", "prerequisites", _metadata_value(metadata, "prerequisites")),
        "steps": _list_field(section_content, "procedure", "steps", _metadata_value(metadata, "steps")),
        "verification": _list_field(section_content, "verification", "verification", _metadata_value(metadata, "verification")),
        "rollback": _list_field(section_content, "rollback", "rollback", _metadata_value(metadata, "rollback")),
        "use_when": _text_field(section_content, "purpose", "use_when", body_sections.get("Use When", "")),
        "boundaries_and_escalation": _text_field(
            section_content,
            "boundaries",
            "boundaries_and_escalation",
            body_sections.get("Boundaries And Escalation", ""),
        ),
        "related_knowledge_notes": _text_field(
            section_content,
            "boundaries",
            "related_knowledge_notes",
            body_sections.get("Related Knowledge Notes", ""),
        ),
        "symptoms": _list_field(section_content, "diagnosis", "symptoms", _metadata_value(metadata, "symptoms")),
        "scope": _text_field(section_content, "diagnosis", "scope", _metadata_value(metadata, "scope")),
        "cause": _text_field(section_content, "diagnosis", "cause", _metadata_value(metadata, "cause")),
        "diagnostic_checks": _list_field(
            section_content,
            "diagnostic_checks",
            "diagnostic_checks",
            _metadata_value(metadata, "diagnostic_checks"),
        ),
        "mitigations": _list_field(section_content, "mitigations", "mitigations", _metadata_value(metadata, "mitigations")),
        "permanent_fix_status": _metadata_value(metadata, "permanent_fix_status", "unknown"),
        "detection_notes": _text_field(section_content, "escalation", "detection_notes", body_sections.get("Detection Notes", "")),
        "escalation_threshold": _text_field(
            section_content,
            "escalation",
            "escalation_threshold",
            body_sections.get("Escalation Threshold", ""),
        ),
        "evidence_notes": _text_field(section_content, "escalation", "evidence_notes", body_sections.get("Evidence Notes", "")),
        "service_name": _text_field(section_content, "service_profile", "service_name", _metadata_value(metadata, "service_name", object_info["title"])),
        "service_criticality": _metadata_value(metadata, "service_criticality", "not_classified"),
        "dependencies": _list_field(section_content, "dependencies", "dependencies", _metadata_value(metadata, "dependencies")),
        "support_entrypoints": _list_field(
            section_content,
            "support_entrypoints",
            "support_entrypoints",
            _list_field(section_content, "operations", "support_entrypoints", _metadata_value(metadata, "support_entrypoints")),
        ),
        "common_failure_modes": _list_field(
            section_content,
            "failure_modes",
            "common_failure_modes",
            _metadata_value(metadata, "common_failure_modes"),
        ),
        "related_runbooks": _list_field(section_content, "operations", "related_runbooks", _metadata_value(metadata, "related_runbooks")),
        "related_known_errors": _list_field(
            section_content,
            "operations",
            "related_known_errors",
            _metadata_value(metadata, "related_known_errors"),
        ),
        "scope_notes": _text_field(section_content, "service_profile", "scope_notes", body_sections.get("Scope", "")),
        "operational_notes": _text_field(section_content, "operations", "operational_notes", body_sections.get("Operational Notes", "")),
        "policy_scope": _text_field(section_content, "policy_scope", "policy_scope", body_sections.get("Policy Scope", _metadata_value(metadata, "policy_scope"))),
        "controls": _list_field(section_content, "controls", "controls", _metadata_value(metadata, "controls")),
        "exceptions": _text_field(section_content, "exceptions", "exceptions", body_sections.get("Exceptions", _metadata_value(metadata, "exceptions"))),
        "architecture": _text_field(section_content, "architecture", "architecture", body_sections.get("Architecture", _metadata_value(metadata, "architecture"))),
        "citation_1_source_title": "",
        "citation_1_source_type": "document",
        "citation_1_source_ref": "",
        "citation_1_note": "",
        "citation_1_lookup": "",
        "citation_2_source_title": "",
        "citation_2_source_type": "document",
        "citation_2_source_ref": "",
        "citation_2_note": "",
        "citation_2_lookup": "",
        "citation_3_source_title": "",
        "citation_3_source_type": "document",
        "citation_3_source_ref": "",
        "citation_3_note": "",
        "citation_3_lookup": "",
    }
    citations = detail.get("citations", [])
    for index, citation in enumerate(citations[:3], start=1):
        values[f"citation_{index}_source_title"] = str(citation["source_title"])
        values[f"citation_{index}_source_type"] = str(citation["source_type"])
        values[f"citation_{index}_source_ref"] = str(citation["source_ref"])
        values[f"citation_{index}_note"] = str(citation["note"] or "")
        values[f"citation_{index}_lookup"] = str(citation["source_title"])
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
                "validity_status": default_citation_validity_status(source_ref),
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
    if object_type == "service_record":
        return (
            "## Scope\n\n"
            + values["scope_notes"].strip()
            + "\n\n## Operational Notes\n\n"
            + values["operational_notes"].strip()
            + "\n\n## Evidence Notes\n\n"
            + values["evidence_notes"].strip()
        ).strip()
    if object_type == "policy":
        return (
            "## Policy Scope\n\n"
            + values["policy_scope"].strip()
            + "\n\n## Exceptions\n\n"
            + values["exceptions"].strip()
        ).strip()
    if object_type == "system_design":
        return (
            "## Architecture\n\n"
            + values["architecture"].strip()
            + "\n\n## Operational Notes\n\n"
            + values["operational_notes"].strip()
        ).strip()
    raise ValueError(f"unsupported object type for revision form serialization: {object_type}")


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
    if values.get("object_lifecycle_state", "") not in taxonomies["statuses"]["allowed_values"]:
        add_error("object_lifecycle_state", "Choose a valid lifecycle state.")

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
    elif object_type == "service_record":
        for field in ("service_name", "dependencies", "support_entrypoints", "common_failure_modes", "scope_notes", "operational_notes"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
        if values.get("service_criticality", "") not in taxonomies["service_criticality"]["allowed_values"]:
            add_error("service_criticality", "Choose a valid service criticality.")
    elif object_type == "policy":
        for field in ("policy_scope", "controls"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
    elif object_type == "system_design":
        for field in ("architecture", "dependencies", "interfaces", "common_failure_modes", "operational_notes"):
            if not values.get(field, "").strip():
                add_error(field, "This field is required.")
    else:
        add_error("_form", "Unsupported object type for revision editing.")

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
        "object_lifecycle_state": values["object_lifecycle_state"].strip(),
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
    elif object_type == "service_record":
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
    elif object_type == "policy":
        payload.update(
            {
                "policy_scope": values["policy_scope"].strip(),
                "controls": parse_multiline(values["controls"]),
                "exceptions": values["exceptions"].strip(),
            }
        )
    elif object_type == "system_design":
        payload.update(
            {
                "architecture": values["architecture"].strip(),
                "dependencies": parse_multiline(values["dependencies"]),
                "interfaces": parse_multiline(values["interfaces"]),
                "common_failure_modes": parse_multiline(values["common_failure_modes"]),
                "support_entrypoints": parse_multiline(values["support_entrypoints"]),
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
    citations = list(payload.get("citations") or [])
    evidence_posture = summarize_evidence_posture(citations)
    if not citations:
        findings.append("Missing supporting citations.")
    weak_count = int(evidence_posture["weak_external_evidence_count"])
    if weak_count:
        findings.append(
            f"Evidence posture: {weak_count} external/manual citation(s) still need evidence follow-up. This draft records the title, reference, and note, but stronger verification details are added later."
        )
    if object_type in {"runbook", "known_error"} and not payload.get("related_services"):
        findings.append("Related service links are missing.")
    if object_type == "service_record" and not payload.get("dependencies"):
        findings.append("Dependencies have not been documented.")
    if object_type == "policy" and not payload.get("controls"):
        findings.append("Policy controls have not been documented.")
    if object_type == "system_design":
        if not payload.get("dependencies"):
            findings.append("Dependencies have not been documented.")
        if not payload.get("interfaces"):
            findings.append("Interfaces have not been documented.")
    if not payload.get("related_object_ids"):
        findings.append("No related knowledge objects were linked for impact tracing.")
    return findings
