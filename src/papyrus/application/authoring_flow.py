from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.revision_runtime import RevisionRuntimeServices
from papyrus.application.runtime_projection import persist_revision_artifacts
from papyrus.domain.actor import require_actor_id
from papyrus.domain.blueprints import Blueprint, BlueprintSection, SectionType
from papyrus.domain.lifecycle import (
    DraftProgressState,
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
)
from papyrus.domain.evidence import (
    default_citation_validity_status,
    summarize_evidence_posture,
)
from papyrus.domain.value_objects import RevisionReviewStatus, TrustState
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    get_knowledge_object,
    get_knowledge_revision,
    insert_knowledge_revision,
    latest_revision_for_object,
    next_revision_number,
    update_knowledge_revision_content,
    upsert_knowledge_object,
)
from papyrus.infrastructure.search.indexer import fts5_available


SECTION_PATTERN = re.compile(r"^## (?P<title>.+?)\n\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)

FIELD_PROVENANCE_KEY = "_field_provenance"
CONVERSION_GAPS_KEY = "_conversion_gaps"

@dataclass(frozen=True)
class DraftRevisionArtifacts:
    payload: dict[str, Any]
    body_markdown: str
    completion: dict[str, Any]
    parsed: Any
    normalized_payload_json: str


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _content_hash(normalized_payload_json: str, body_markdown: str) -> str:
    return hashlib.sha256(f"{normalized_payload_json}\n{body_markdown}".encode("utf-8")).hexdigest()


def _policy_authority(authority: PolicyAuthority | None) -> PolicyAuthority:
    return authority or PolicyAuthority.from_repository_policy()


def _body_sections(body_markdown: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in SECTION_PATTERN.finditer(str(body_markdown or "").strip())
    }


def _list_value(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    return []


def _citation_list(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for entry in value:
        if not isinstance(entry, dict):
            continue
        source_title = str(entry.get("source_title") or "").strip()
        source_ref = str(entry.get("source_ref") or "").strip()
        if not any([source_title, source_ref, entry.get("note")]):
            continue
        items.append(
            {
                "source_title": source_title,
                "source_type": str(entry.get("source_type") or "document").strip() or "document",
                "source_ref": source_ref,
                "note": str(entry.get("note") or "").strip() or None,
                "claim_anchor": None,
                "excerpt": None,
                "captured_at": entry.get("captured_at"),
                "validity_status": str(entry.get("validity_status") or default_citation_validity_status(source_ref)),
                "integrity_hash": entry.get("integrity_hash"),
                "evidence_snapshot_path": entry.get("evidence_snapshot_path"),
                "evidence_expiry_at": entry.get("evidence_expiry_at"),
                "evidence_last_validated_at": entry.get("evidence_last_validated_at"),
            }
        )
    return items


def _revision_metadata_value(metadata: dict[str, Any], field_name: str) -> Any:
    aliases = {
        "object_id": ("id",),
        "related_services": ("services",),
        "related_object_ids": ("related_articles",),
    }
    if field_name in metadata:
        return metadata[field_name]
    for alias in aliases.get(field_name, ()):
        if alias in metadata:
            return metadata[alias]
    return ""


def _section_field_values(section_values: dict[str, Any], section: BlueprintSection) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field in section.fields:
        name = str(field["name"])
        kind = str(field.get("kind") or "text")
        value = section_values.get(name, [] if kind in {"list", "references"} else "")
        if kind == "list":
            result[name] = _list_value(value)
        elif kind == "references":
            result[name] = _citation_list(value)
        else:
            result[name] = str(value or "").strip()
    return result


def _field_provenance(section_values: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = section_values.get(FIELD_PROVENANCE_KEY)
    if not isinstance(raw, dict):
        return {}
    return {
        str(field_name): dict(value)
        for field_name, value in raw.items()
        if isinstance(value, dict)
    }


def _conversion_gaps(section_values: dict[str, Any]) -> list[dict[str, Any]]:
    raw = section_values.get(CONVERSION_GAPS_KEY)
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, dict)]


def _build_section_content_from_revision(
    *,
    blueprint: Blueprint,
    metadata: dict[str, Any],
    body_markdown: str,
) -> dict[str, dict[str, Any]]:
    content: dict[str, dict[str, Any]] = {}
    body_sections = _body_sections(body_markdown)

    for section in blueprint.sections:
        section_values: dict[str, Any] = {}
        long_text_fields = [field for field in section.fields if str(field.get("kind")) == "long_text"]
        long_text_by_heading = {
            heading: long_text_fields[index]["name"]
            for index, heading in enumerate(section.body_headings)
            if index < len(long_text_fields)
        }
        for field in section.fields:
            name = str(field["name"])
            kind = str(field.get("kind") or "text")
            source_value = _revision_metadata_value(metadata, name)
            if kind == "references":
                section_values[name] = source_value if isinstance(source_value, list) else metadata.get(name, [])
            elif kind == "list":
                section_values[name] = source_value if isinstance(source_value, list) else metadata.get(name, [])
            elif kind == "select":
                section_values[name] = str(source_value or "")
            elif kind == "long_text":
                matched_heading = next((heading for heading, field_name in long_text_by_heading.items() if field_name == name), None)
                if matched_heading:
                    section_values[name] = body_sections.get(matched_heading, str(source_value or ""))
                else:
                    section_values[name] = str(source_value or "")
            else:
                section_values[name] = str(source_value or "")
        content[section.section_id] = section_values
    return content


def derive_section_content(*, blueprint_id: str, metadata: dict[str, Any], body_markdown: str) -> dict[str, dict[str, Any]]:
    blueprint = get_blueprint(blueprint_id)
    return _build_section_content_from_revision(
        blueprint=blueprint,
        metadata=metadata,
        body_markdown=body_markdown,
    )


def _build_initial_section_content(
    *,
    blueprint: Blueprint,
    object_row: sqlite3.Row,
    revision_row: sqlite3.Row | None,
) -> dict[str, dict[str, Any]]:
    if revision_row is not None:
        raw_section_content = str(revision_row["section_content_json"] or "").strip()
        if raw_section_content and raw_section_content != "{}":
            parsed = json.loads(raw_section_content)
            if isinstance(parsed, dict):
                return {str(key): dict(value) for key, value in parsed.items() if isinstance(value, dict)}
        metadata = json.loads(revision_row["normalized_payload_json"])
        return _build_section_content_from_revision(
            blueprint=blueprint,
            metadata=metadata,
            body_markdown=str(revision_row["body_markdown"]),
        )

    stewardship = {
        "summary": str(object_row["summary"]),
        "owner": str(object_row["owner"]),
        "team": str(object_row["team"]),
        "object_lifecycle_state": str(object_row["object_lifecycle_state"]),
        "review_cadence": str(object_row["review_cadence"]),
        "audience": "service_desk",
        "systems": json.loads(str(object_row["systems_json"])),
        "tags": json.loads(str(object_row["tags_json"])),
        "related_services": [],
        "related_object_ids": [],
        "change_summary": "",
    }
    identity = {
        "object_id": str(object_row["object_id"]),
        "title": str(object_row["title"]),
        "canonical_path": str(object_row["canonical_path"]),
    }
    content: dict[str, dict[str, Any]] = {}
    for section in blueprint.sections:
        if section.section_id == "identity":
            content[section.section_id] = identity
            continue
        if section.section_id == "stewardship":
            content[section.section_id] = stewardship
            continue
        initial_values: dict[str, Any] = {}
        for field in section.fields:
            kind = str(field.get("kind") or "text")
            initial_values[str(field["name"])] = [] if kind in {"list", "references"} else ""
        content[section.section_id] = initial_values
    return content


def _references_for_payload(citations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"title": citation["source_title"], "path": citation["source_ref"], "note": citation.get("note")}
        for citation in citations
        if citation.get("source_title") or citation.get("source_ref")
    ]


def _change_log_entry(actor: str, summary: str) -> dict[str, str]:
    today = dt.date.today().isoformat()
    return {"date": today, "summary": summary or "Structured draft update.", "author": actor}


def _body_from_section_content(blueprint: Blueprint, section_content: dict[str, dict[str, Any]]) -> str:
    parts: list[str] = []
    for section in blueprint.sections:
        values = _section_field_values(section_content.get(section.section_id, {}), section)
        long_text_fields = [field for field in section.fields if str(field.get("kind")) == "long_text"]
        for index, heading in enumerate(section.body_headings):
            if index >= len(long_text_fields):
                continue
            field_name = str(long_text_fields[index]["name"])
            body_text = str(values.get(field_name) or "").strip()
            if not body_text:
                continue
            parts.append(f"## {heading}\n\n{body_text}")
    return "\n\n".join(parts).strip()


def _base_payload(
    *,
    blueprint: Blueprint,
    object_row: sqlite3.Row,
    section_content: dict[str, dict[str, Any]],
    actor: str,
    existing_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    today = dt.date.today().isoformat()
    metadata = existing_metadata or {}
    identity = _section_field_values(section_content.get("identity", {}), blueprint.section("identity"))
    stewardship = _section_field_values(section_content.get("stewardship", {}), blueprint.section("stewardship"))
    citations = _citation_list(section_content.get("evidence", {}).get("citations", []))
    related_object_ids = _list_value(stewardship.get("related_object_ids", []))
    payload: dict[str, Any] = {
        "id": identity.get("object_id") or str(object_row["object_id"]),
        "title": identity.get("title") or str(object_row["title"]),
        "canonical_path": identity.get("canonical_path") or str(object_row["canonical_path"]),
        "summary": stewardship.get("summary") or str(object_row["summary"]),
        "knowledge_object_type": blueprint.blueprint_id,
        "legacy_article_type": metadata.get("legacy_article_type"),
        "object_lifecycle_state": (
            stewardship.get("object_lifecycle_state") or str(object_row["object_lifecycle_state"])
        ),
        "owner": stewardship.get("owner") or str(object_row["owner"]),
        "source_type": str(metadata.get("source_type") or object_row["source_type"] or "native"),
        "source_system": str(metadata.get("source_system") or object_row["source_system"] or "repository"),
        "source_title": identity.get("title") or str(metadata.get("source_title") or object_row["title"]),
        "team": stewardship.get("team") or str(object_row["team"]),
        "systems": _list_value(stewardship.get("systems", [])),
        "tags": _list_value(stewardship.get("tags", [])),
        "created": str(metadata.get("created") or object_row["created_date"] or today),
        "updated": today,
        "last_reviewed": today,
        "review_cadence": stewardship.get("review_cadence") or str(object_row["review_cadence"]),
        "audience": stewardship.get("audience") or str(metadata.get("audience") or "service_desk"),
        "citations": citations,
        "related_object_ids": related_object_ids,
        "superseded_by": metadata.get("superseded_by"),
        "replaced_by": metadata.get("replaced_by"),
        "retirement_reason": metadata.get("retirement_reason"),
        "services": _list_value(stewardship.get("related_services", [])),
        "related_articles": related_object_ids,
        "references": _references_for_payload(citations),
        "change_log": [
            *(metadata.get("change_log") if isinstance(metadata.get("change_log"), list) else []),
            _change_log_entry(actor, str(stewardship.get("change_summary") or "")),
        ],
    }
    return payload


def _payload_from_sections(
    *,
    blueprint: Blueprint,
    object_row: sqlite3.Row,
    section_content: dict[str, dict[str, Any]],
    actor: str,
    existing_metadata: dict[str, Any] | None,
) -> tuple[dict[str, Any], str]:
    payload = _base_payload(
        blueprint=blueprint,
        object_row=object_row,
        section_content=section_content,
        actor=actor,
        existing_metadata=existing_metadata,
    )
    if blueprint.blueprint_id == "runbook":
        purpose = section_content.get("purpose", {})
        boundaries = section_content.get("boundaries", {})
        payload.update(
            {
                "related_services": _list_value(section_content.get("stewardship", {}).get("related_services", [])),
                "prerequisites": _list_value(section_content.get("prerequisites", {}).get("prerequisites", [])),
                "steps": _list_value(section_content.get("procedure", {}).get("steps", [])),
                "verification": _list_value(section_content.get("verification", {}).get("verification", [])),
                "rollback": _list_value(section_content.get("rollback", {}).get("rollback", [])),
            }
        )
        body = _body_from_section_content(blueprint, section_content)
        if not str(purpose.get("use_when") or "").strip():
            body = body
        return payload, body
    if blueprint.blueprint_id == "known_error":
        diagnosis = section_content.get("diagnosis", {})
        mitigations = section_content.get("mitigations", {})
        payload.update(
            {
                "related_services": _list_value(section_content.get("stewardship", {}).get("related_services", [])),
                "symptoms": _list_value(diagnosis.get("symptoms", [])),
                "scope": str(diagnosis.get("scope") or "").strip(),
                "cause": str(diagnosis.get("cause") or "").strip(),
                "diagnostic_checks": _list_value(section_content.get("diagnostic_checks", {}).get("diagnostic_checks", [])),
                "mitigations": _list_value(mitigations.get("mitigations", [])),
                "permanent_fix_status": str(mitigations.get("permanent_fix_status") or "unknown").strip(),
            }
        )
        return payload, _body_from_section_content(blueprint, section_content)
    if blueprint.blueprint_id == "service_record":
        profile = section_content.get("service_profile", {})
        operations = section_content.get("operations", {})
        payload.update(
            {
                "service_name": str(profile.get("service_name") or payload["title"]).strip(),
                "service_criticality": str(profile.get("service_criticality") or "not_classified").strip(),
                "dependencies": _list_value(section_content.get("dependencies", {}).get("dependencies", [])),
                "support_entrypoints": _list_value(
                    section_content.get("support_entrypoints", {}).get("support_entrypoints", [])
                ),
                "common_failure_modes": _list_value(section_content.get("failure_modes", {}).get("common_failure_modes", [])),
                "related_runbooks": _list_value(operations.get("related_runbooks", [])),
                "related_known_errors": _list_value(operations.get("related_known_errors", [])),
            }
        )
        return payload, _body_from_section_content(blueprint, section_content)
    if blueprint.blueprint_id == "policy":
        payload.update(
            {
                "policy_scope": str(section_content.get("policy_scope", {}).get("policy_scope", "")).strip(),
                "controls": _list_value(section_content.get("controls", {}).get("controls", [])),
                "exceptions": str(section_content.get("exceptions", {}).get("exceptions", "")).strip(),
            }
        )
        return payload, _body_from_section_content(blueprint, section_content)
    if blueprint.blueprint_id == "system_design":
        operations = section_content.get("operations", {})
        payload.update(
            {
                "architecture": str(section_content.get("architecture", {}).get("architecture", "")).strip(),
                "dependencies": _list_value(section_content.get("dependencies", {}).get("dependencies", [])),
                "interfaces": _list_value(section_content.get("interfaces", {}).get("interfaces", [])),
                "common_failure_modes": _list_value(section_content.get("failure_modes", {}).get("common_failure_modes", [])),
                "support_entrypoints": _list_value(operations.get("support_entrypoints", [])),
            }
        )
        return payload, _body_from_section_content(blueprint, section_content)
    raise ValueError(f"unsupported blueprint payload builder: {blueprint.blueprint_id}")


def _validate_field(
    *,
    field: dict[str, Any],
    value: Any,
    taxonomies: dict[str, dict[str, Any]],
    authority: PolicyAuthority | None = None,
) -> list[str]:
    current_authority = _policy_authority(authority)
    errors: list[str] = []
    name = str(field["name"])
    kind = str(field.get("kind") or "text")
    required = bool(field.get("required", True))
    taxonomy = str(field.get("taxonomy") or "").strip()
    if kind == "references":
        citations = _citation_list(value)
        if required and not citations:
            errors.append("At least one citation is required.")
        for index, citation in enumerate(citations, start=1):
            if not citation["source_title"]:
                errors.append(f"Citation {index} needs a source title.")
            if not citation["source_ref"]:
                errors.append(f"Citation {index} needs a source reference.")
        return errors
    if kind == "list":
        items = _list_value(value)
        if required and not items:
            errors.append("This list cannot be empty.")
        if taxonomy and items:
            allowed = set(taxonomies[taxonomy]["allowed_values"])
            for item in items:
                if item not in allowed:
                    errors.append(f"'{item}' is not an approved {taxonomy} value.")
        return errors
    text = str(value or "").strip()
    if required and not text:
        errors.append("This field is required.")
    if name == "object_id" and text and not re.fullmatch(r"^kb-[a-z0-9]+(?:-[a-z0-9]+)*$", text):
        errors.append("Object ID must match kb-slug format.")
    if name == "canonical_path" and text:
        try:
            current_authority.validate_canonical_repo_relative_path(text)
        except ValueError as exc:
            errors.append(str(exc))
    if taxonomy and text:
        allowed = set(taxonomies[taxonomy]["allowed_values"])
        if text not in allowed:
            errors.append(f"'{text}' is not an approved {taxonomy} value.")
    return errors


def compute_completion_state(
    *,
    blueprint: Blueprint,
    section_content: dict[str, dict[str, Any]],
    taxonomies: dict[str, dict[str, Any]],
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    section_completion_map: dict[str, dict[str, Any]] = {}
    completed_required = 0
    required_section_ids = set(blueprint.required_sections)
    total_required = len(required_section_ids)
    blockers: list[str] = []
    warnings: list[str] = []
    next_section_id: str | None = None
    evidence_posture = summarize_evidence_posture([])

    for section_id in blueprint.ordering:
        section = blueprint.section(section_id)
        required_section = section_id in required_section_ids
        raw_values = section_content.get(section_id, {})
        values = _section_field_values(raw_values, section)
        provenance_map = _field_provenance(raw_values if isinstance(raw_values, dict) else {})
        conversion_gaps = _conversion_gaps(raw_values if isinstance(raw_values, dict) else {})
        errors: list[str] = []
        field_statuses: dict[str, dict[str, Any]] = {}
        completed_fields = 0
        populated_fields = 0
        required_field_count = 0
        for field in section.fields:
            field_name = str(field["name"])
            kind = str(field.get("kind") or "text")
            required = bool(field.get("required", True))
            if required:
                required_field_count += 1
            value = values.get(field_name)
            field_errors = _validate_field(
                field=field,
                value=value,
                taxonomies=taxonomies,
                authority=current_authority,
            )
            errors.extend(field_errors)
            value_present = (
                bool(_list_value(value))
                if kind == "list"
                else bool(_citation_list(value))
                if kind == "references"
                else bool(str(value or "").strip())
            )
            if value_present:
                populated_fields += 1
            field_complete = not field_errors and (value_present or not required)
            if field_complete:
                completed_fields += 1
            provenance = provenance_map.get(field_name)
            if provenance and str(provenance.get("status") or "") in {"manual_required", "unresolved", "low_confidence"}:
                warnings.append(
                    f"{section.display_name}: {str(field.get('label') or field_name)} remains {str(provenance.get('status'))} after import."
                )
            field_statuses[field_name] = {
                "display_name": str(field.get("label") or field_name),
                "required": required,
                "completed": field_complete,
                "value_present": value_present,
                "errors": field_errors,
                "provenance": provenance,
            }
        if section.section_type == SectionType.REFERENCES:
            citations = _citation_list(values.get("citations", []))
            evidence_posture = summarize_evidence_posture(citations)
            weak_count = int(evidence_posture["weak_external_evidence_count"])
            if weak_count:
                warnings.append(
                    f"{section.display_name}: {weak_count} external/manual citation(s) remain weak because the write surface has not recorded capture time and integrity hash."
                )
        complete = not errors and all(
            (
                bool(_list_value(values.get(str(field["name"]))))
                if str(field.get("kind")) == "list"
                else bool(_citation_list(values.get(str(field["name"]))))
                if str(field.get("kind")) == "references"
                else bool(str(values.get(str(field["name"])) or "").strip())
            )
            or not bool(field.get("required", True))
            for field in section.fields
        )
        if required_section and complete:
            completed_required += 1
        if required_section and errors:
            blockers.extend(f"{section.display_name}: {message}" for message in errors)
        if next_section_id is None and required_section and not complete:
            next_section_id = section.section_id
        section_completion_map[section.section_id] = {
            "display_name": section.display_name,
            "required": required_section,
            "completed": complete,
            "errors": errors,
            "field_count": len(section.fields),
            "required_field_count": required_field_count,
            "completed_field_count": completed_fields,
            "populated_field_count": populated_fields,
            "fields": field_statuses,
            "conversion_gaps": conversion_gaps,
            "evidence_posture": evidence_posture if section.section_type == SectionType.REFERENCES else None,
        }

    completion_percentage = int((completed_required / total_required) * 100) if total_required else 100
    draft_state = DraftProgressState.READY_FOR_REVIEW.value
    if blockers:
        draft_state = DraftProgressState.BLOCKED.value
    elif completion_percentage < 100:
        draft_state = DraftProgressState.IN_PROGRESS.value

    if next_section_id is None:
        next_section_id = blueprint.ordering[-1] if blueprint.ordering else None

    return {
        "completion_percentage": completion_percentage,
        "completed_required_sections": completed_required,
        "required_section_count": total_required,
        "draft_progress_state": draft_state,
        "next_section_id": next_section_id,
        "blockers": blockers,
        "warnings": warnings,
        "section_completion_map": section_completion_map,
        "evidence_posture": evidence_posture,
    }


def _connection(database_path: Path) -> sqlite3.Connection:
    connection = open_runtime_database(database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    apply_runtime_schema(connection, has_fts5=fts5_available(connection))
    connection.execute(
        "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
        (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
    )
    return connection


def build_draft_revision_artifacts(
    *,
    blueprint: Blueprint,
    object_row: sqlite3.Row | dict[str, Any],
    section_content: dict[str, dict[str, Any]],
    actor: str,
    existing_metadata: dict[str, Any] | None,
    runtime: RevisionRuntimeServices,
    taxonomies: dict[str, dict[str, Any]] | None = None,
    authority: PolicyAuthority | None = None,
) -> DraftRevisionArtifacts:
    payload, body_markdown = _payload_from_sections(
        blueprint=blueprint,
        object_row=object_row,
        section_content=section_content,
        actor=actor,
        existing_metadata=existing_metadata,
    )
    completion = compute_completion_state(
        blueprint=blueprint,
        section_content=section_content,
        taxonomies=taxonomies or runtime.taxonomies(),
        authority=authority,
    )
    parsed = runtime.parse_revision(payload, body_markdown)
    return DraftRevisionArtifacts(
        payload=payload,
        body_markdown=body_markdown,
        completion=completion,
        parsed=parsed,
        normalized_payload_json=json_dump(parsed.metadata),
    )


def _sync_object_from_parsed_revision(
    connection: sqlite3.Connection,
    *,
    object_row: sqlite3.Row,
    revision_id: str,
    parsed: Any,
    authority: PolicyAuthority | None = None,
) -> None:
    current_authority = _policy_authority(authority)
    current_object_lifecycle = str(object_row["object_lifecycle_state"])
    next_object_lifecycle = str(parsed.metadata["object_lifecycle_state"])
    current_authority.require_object_lifecycle_transition(current_object_lifecycle, next_object_lifecycle)
    source_sync_state = (
        SourceSyncState.APPLIED.value
        if str(parsed.metadata.get("source_type") or object_row["source_type"] or "native") != "native"
        else SourceSyncState.NOT_REQUIRED.value
    )
    upsert_knowledge_object(
        connection,
        object_id=str(object_row["object_id"]),
        object_type=str(parsed.object_type),
        legacy_type=object_row["legacy_type"],
        title=str(parsed.metadata["title"]),
        summary=str(parsed.metadata["summary"]),
        object_lifecycle_state=next_object_lifecycle,
        owner=str(parsed.metadata["owner"]),
        team=str(parsed.metadata["team"]),
        canonical_path=str(parsed.metadata["canonical_path"]),
        source_type=str(parsed.metadata["source_type"]),
        source_system=str(parsed.metadata["source_system"]),
        source_title=str(parsed.metadata["source_title"]),
        created_date=str(parsed.metadata["created"]),
        updated_date=str(parsed.metadata["updated"]),
        last_reviewed=str(parsed.metadata["last_reviewed"]),
        review_cadence=str(parsed.metadata["review_cadence"]),
        trust_state=TrustState.SUSPECT.value,
        source_sync_state=source_sync_state,
        current_revision_id=revision_id,
        tags_json=json_dump(parsed.metadata.get("tags", [])),
        systems_json=json_dump(parsed.metadata.get("systems", [])),
    )
    persist_revision_artifacts(
        connection,
        parsed=parsed,
        revision_id=revision_id,
        relationship_provenance="workflow_projection",
    )


def create_draft_from_blueprint(
    *,
    object_id: str,
    blueprint_id: str,
    actor: str,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    return ensure_draft_revision(
        object_id=object_id,
        blueprint_id=blueprint_id,
        actor=actor,
        database_path=database_path,
        source_root=source_root,
        authority=authority,
    )


def _draft_result_from_row(
    *,
    revision_row: sqlite3.Row,
    blueprint: Blueprint,
    taxonomies: dict[str, dict[str, Any]],
    authority: PolicyAuthority,
) -> dict[str, Any]:
    section_content = json.loads(str(revision_row["section_content_json"] or "{}"))
    return {
        "revision_id": str(revision_row["revision_id"]),
        "revision_number": int(revision_row["revision_number"]),
        "blueprint": blueprint,
        "section_content": section_content,
        "completion": compute_completion_state(
            blueprint=blueprint,
            section_content=section_content,
            taxonomies=taxonomies,
            authority=authority,
        ),
        "is_first_revision": int(revision_row["revision_number"]) == 1,
    }


def _compatible_current_draft_revision(
    connection: sqlite3.Connection,
    *,
    object_row: sqlite3.Row,
    blueprint: Blueprint,
) -> sqlite3.Row | None:
    current_revision_id = str(object_row["current_revision_id"] or "").strip()
    if not current_revision_id:
        return None
    current_revision_row = get_knowledge_revision(connection, current_revision_id)
    if current_revision_row is None:
        return None
    revision_review_state = str(current_revision_row["revision_review_state"] or "").strip()
    revision_blueprint_id = str(current_revision_row["blueprint_id"] or blueprint.blueprint_id)
    if revision_blueprint_id != blueprint.blueprint_id:
        return None
    if revision_review_state not in {RevisionReviewStatus.DRAFT.value, RevisionReviewStatus.REJECTED.value}:
        return None
    return current_revision_row


def ensure_draft_revision(
    *,
    object_id: str,
    blueprint_id: str,
    actor: str,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    blueprint = get_blueprint(blueprint_id)
    runtime = RevisionRuntimeServices(source_root=Path(source_root))
    taxonomies = runtime.taxonomies()
    connection = _connection(Path(database_path))
    now = _now_utc()
    try:
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        current_revision_row = _compatible_current_draft_revision(
            connection,
            object_row=object_row,
            blueprint=blueprint,
        )
        if current_revision_row is not None:
            return _draft_result_from_row(
                revision_row=current_revision_row,
                blueprint=blueprint,
                taxonomies=taxonomies,
                authority=current_authority,
            )

        latest_revision = latest_revision_for_object(connection, object_id)
        section_content = _build_initial_section_content(
            blueprint=blueprint,
            object_row=object_row,
            revision_row=latest_revision,
        )
        existing_metadata = (
            json.loads(str(latest_revision["normalized_payload_json"]))
            if latest_revision is not None and latest_revision["normalized_payload_json"]
            else None
        )
        artifacts = build_draft_revision_artifacts(
            blueprint=blueprint,
            object_row=object_row,
            section_content=section_content,
            actor=actor,
            existing_metadata=existing_metadata,
            runtime=runtime,
            taxonomies=taxonomies,
            authority=current_authority,
        )
        revision_id = f"{object_id}-rev-{uuid.uuid4().hex[:12]}"
        revision_number = next_revision_number(connection, object_id)
        insert_knowledge_revision(
            connection,
            revision_id=revision_id,
            object_id=object_id,
            revision_number=revision_number,
            revision_review_state=RevisionReviewState.DRAFT.value,
            blueprint_id=blueprint.blueprint_id,
            draft_progress_state=artifacts.completion["draft_progress_state"],
            source_path=str(artifacts.parsed.metadata["canonical_path"]),
            content_hash=_content_hash(artifacts.normalized_payload_json, artifacts.body_markdown),
            body_markdown=artifacts.body_markdown,
            normalized_payload_json=artifacts.normalized_payload_json,
            section_content_json=json_dump(section_content),
            section_completion_json=json_dump(artifacts.completion["section_completion_map"]),
            legacy_metadata_json=json_dump(existing_metadata or {}),
            imported_at=now.isoformat(),
            change_summary=str(section_content.get("stewardship", {}).get("change_summary") or "") or None,
        )
        _sync_object_from_parsed_revision(
            connection,
            object_row=object_row,
            revision_id=revision_id,
            parsed=artifacts.parsed,
            authority=current_authority,
        )
        runtime.refresh_object_projection(connection, object_id=object_id)
        insert_audit_event(
            connection,
            event_id=_event_id("draft-created"),
            event_type="revision_created",
            occurred_at=now.isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=revision_id,
            details_json=json_dump(
                {
                    "revision_number": revision_number,
                    "blueprint_id": blueprint.blueprint_id,
                    "draft_progress_state": artifacts.completion["draft_progress_state"],
                }
            ),
        )
        connection.commit()
        return {
            "revision_id": revision_id,
            "revision_number": revision_number,
            "blueprint": blueprint,
            "section_content": section_content,
            "completion": artifacts.completion,
            "is_first_revision": revision_number == 1,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def load_draft_context(
    *,
    object_id: str,
    revision_id: str | None = None,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    connection = _connection(Path(database_path))
    try:
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        blueprint = get_blueprint(str(object_row["object_type"]))
        revision_row: sqlite3.Row | None
        if revision_id is None:
            revision_row = _compatible_current_draft_revision(
                connection,
                object_row=object_row,
                blueprint=blueprint,
            )
            if revision_row is None:
                raise ValueError("Guided drafting needs an existing draft revision. Start a draft before loading this page.")
        else:
            revision_row = get_knowledge_revision(connection, revision_id)
            if revision_row is None or str(revision_row["object_id"]) != object_id:
                raise ValueError(f"revision not found for {object_id}: {revision_id}")
            revision_blueprint_id = str(revision_row["blueprint_id"] or blueprint.blueprint_id)
            if revision_blueprint_id != blueprint.blueprint_id:
                raise ValueError(f"revision {revision_id} does not match blueprint {blueprint.blueprint_id}")
            revision_review_state = str(revision_row["revision_review_state"] or "").strip()
            if revision_review_state not in {RevisionReviewStatus.DRAFT.value, RevisionReviewStatus.REJECTED.value}:
                raise ValueError(
                    f"guided drafting can only load draft or rejected revisions; revision {revision_id} is {revision_review_state or 'unknown'}"
                )

        section_content = _build_initial_section_content(
            blueprint=blueprint,
            object_row=object_row,
            revision_row=revision_row,
        )
        runtime = RevisionRuntimeServices(source_root=Path(source_root))
        completion = compute_completion_state(
            blueprint=blueprint,
            section_content=section_content,
            taxonomies=runtime.taxonomies(),
            authority=current_authority,
        )
        return {
            "revision_id": str(revision_row["revision_id"]),
            "revision_number": int(revision_row["revision_number"]),
            "blueprint": blueprint,
            "section_content": section_content,
            "completion": completion,
            "is_first_revision": int(revision_row["revision_number"]) == 1,
        }
    finally:
        connection.close()


def update_section(
    *,
    object_id: str,
    revision_id: str,
    section_id: str,
    values: dict[str, Any],
    section_metadata: dict[str, Any] | None = None,
    actor: str,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    runtime = RevisionRuntimeServices(source_root=Path(source_root))
    taxonomies = runtime.taxonomies()
    connection = _connection(Path(database_path))
    now = _now_utc()
    try:
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        revision_row = get_knowledge_revision(connection, revision_id)
        if revision_row is None or str(revision_row["object_id"]) != object_id:
            raise ValueError(f"revision not found for {object_id}: {revision_id}")
        blueprint = get_blueprint(str(revision_row["blueprint_id"] or object_row["object_type"]))
        section_content = _build_initial_section_content(
            blueprint=blueprint,
            object_row=object_row,
            revision_row=revision_row,
        )
        section = blueprint.section(section_id)
        existing_section = section_content.get(section_id, {}) if isinstance(section_content.get(section_id, {}), dict) else {}
        next_section_values = _section_field_values(values, section)
        for key, value in existing_section.items():
            if str(key).startswith("_") and str(key) not in next_section_values:
                next_section_values[str(key)] = value
        if section_metadata:
            for key, value in section_metadata.items():
                next_section_values[str(key)] = value
        section_content[section_id] = next_section_values
        existing_metadata = json.loads(str(revision_row["normalized_payload_json"]))
        artifacts = build_draft_revision_artifacts(
            blueprint=blueprint,
            object_row=object_row,
            section_content=section_content,
            actor=actor,
            existing_metadata=existing_metadata,
            runtime=runtime,
            taxonomies=taxonomies,
            authority=current_authority,
        )
        update_knowledge_revision_content(
            connection,
            revision_id=revision_id,
            content_hash=_content_hash(artifacts.normalized_payload_json, artifacts.body_markdown),
            body_markdown=artifacts.body_markdown,
            normalized_payload_json=artifacts.normalized_payload_json,
            blueprint_id=blueprint.blueprint_id,
            draft_progress_state=artifacts.completion["draft_progress_state"],
            section_content_json=json_dump(section_content),
            section_completion_json=json_dump(artifacts.completion["section_completion_map"]),
            change_summary=str(section_content.get("stewardship", {}).get("change_summary") or "") or None,
        )
        _sync_object_from_parsed_revision(
            connection,
            object_row=object_row,
            revision_id=revision_id,
            parsed=artifacts.parsed,
            authority=current_authority,
        )
        runtime.refresh_object_projection(connection, object_id=object_id)
        insert_audit_event(
            connection,
            event_id=_event_id("draft-section-updated"),
            event_type="draft_section_updated",
            occurred_at=now.isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=revision_id,
            details_json=json_dump(
                {
                    "section_id": section_id,
                    "draft_progress_state": artifacts.completion["draft_progress_state"],
                }
            ),
        )
        connection.commit()
        return {
            "revision_id": revision_id,
            "section_content": section_content,
            "completion": artifacts.completion,
            "metadata": artifacts.parsed.metadata,
            "body_markdown": artifacts.body_markdown,
        }
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def validate_draft_progress(
    *,
    object_id: str,
    revision_id: str,
    database_path: Path = DB_PATH,
    source_root: Path,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    current_authority = _policy_authority(authority)
    connection = _connection(Path(database_path))
    try:
        object_row = get_knowledge_object(connection, object_id)
        revision_row = get_knowledge_revision(connection, revision_id)
        if object_row is None or revision_row is None:
            raise ValueError("draft revision not found")
        blueprint = get_blueprint(str(revision_row["blueprint_id"] or object_row["object_type"]))
        section_content = _build_initial_section_content(
            blueprint=blueprint,
            object_row=object_row,
            revision_row=revision_row,
        )
        runtime = RevisionRuntimeServices(source_root=Path(source_root))
        return {
            "blueprint": blueprint,
            "section_content": section_content,
            "completion": compute_completion_state(
                blueprint=blueprint,
                section_content=section_content,
                taxonomies=runtime.taxonomies(),
                authority=current_authority,
            ),
        }
    finally:
        connection.close()
