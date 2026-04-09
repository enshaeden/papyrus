from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.application.authoring_flow import create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.ingestion_flow import ingestion_detail, mark_ingestion_converted, update_ingestion_mapping
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.domain.actor import require_actor_id
from papyrus.infrastructure.paths import DB_PATH, ROOT


SECTION_KEYWORDS = {
    "purpose": ("purpose", "overview", "summary", "use when"),
    "prerequisites": ("prerequisite", "before", "access"),
    "procedure": ("step", "procedure", "workflow"),
    "verification": ("verify", "validation", "confirm"),
    "rollback": ("rollback", "undo", "recovery"),
    "boundaries": ("boundary", "escalation"),
    "diagnosis": ("symptom", "cause", "scope"),
    "diagnostic_checks": ("diagnostic", "check"),
    "mitigations": ("mitigation", "workaround"),
    "escalation": ("escalation", "detection"),
    "service_profile": ("service", "scope", "criticality"),
    "dependencies": ("dependency", "depends"),
    "support_entrypoints": ("support", "entrypoint", "contact"),
    "failure_modes": ("failure", "issue", "degradation"),
    "operations": ("operation", "notes"),
    "policy_scope": ("policy", "scope"),
    "controls": ("control", "requirement", "must", "shall"),
    "exceptions": ("exception", "waiver"),
    "architecture": ("architecture", "design", "component"),
    "interfaces": ("interface", "integration", "api"),
    "evidence": ("source", "reference", "evidence", "citation"),
    "relationships": ("related", "dependency", "reference"),
}


def _confidence_score(section_title: str, content: str, keywords: tuple[str, ...]) -> float:
    haystack = f"{section_title} {content}".lower()
    matches = sum(1 for keyword in keywords if keyword in haystack)
    if matches <= 0:
        return 0.0
    return min(0.95, 0.25 + (matches * 0.2))


def map_to_blueprint(
    *,
    ingestion_id: str,
    blueprint_id: str | None = None,
    database_path: Path = DB_PATH,
) -> dict[str, Any]:
    detail = ingestion_detail(ingestion_id=ingestion_id, database_path=database_path)
    resolved_blueprint_id = blueprint_id or detail.get("blueprint_id") or detail["classification"]["blueprint_id"]
    blueprint = get_blueprint(str(resolved_blueprint_id))
    sections = []
    for artifact in detail["artifacts"]:
        if artifact["artifact_type"] == "sections":
            sections = list(artifact["content"].get("sections", []))
            break
    mapped_sections: dict[str, dict[str, Any]] = {}
    unmapped: list[dict[str, Any]] = []
    low_confidence: list[dict[str, Any]] = []

    for section_id in blueprint.ordering:
        keywords = SECTION_KEYWORDS.get(section_id, ())
        best_match: dict[str, Any] | None = None
        best_score = 0.0
        for item in sections:
            heading = str(item.get("heading") or "")
            content = item.get("content")
            normalized_content = "\n".join(content) if isinstance(content, list) else str(content or "")
            score = _confidence_score(heading, normalized_content, keywords)
            if score > best_score:
                best_score = score
                best_match = item
        mapped_sections[section_id] = {
            "match": best_match,
            "confidence": round(best_score, 2),
            "required": section_id in blueprint.required_sections,
        }
        if best_match is None:
            continue
        if best_score < 0.55:
            low_confidence.append(
                {
                    "section_id": section_id,
                    "display_name": blueprint.section(section_id).display_name,
                    "confidence": round(best_score, 2),
                    "source_heading": str(best_match.get("heading") or ""),
                }
            )

    for item in sections:
        if not any(mapping["match"] == item for mapping in mapped_sections.values()):
            unmapped.append(item)

    result = {
        "blueprint_id": blueprint.blueprint_id,
        "sections": mapped_sections,
        "missing_sections": identify_missing_sections(mapped_sections, blueprint.required_sections),
        "low_confidence": detect_low_confidence_mappings(mapped_sections),
        "unmapped_content": unmapped,
    }
    update_ingestion_mapping(
        ingestion_id=ingestion_id,
        mapping_result=result,
        status="mapped",
        blueprint_id=blueprint.blueprint_id,
        database_path=database_path,
    )
    return result


def identify_missing_sections(
    mapping_result: dict[str, Any],
    required_sections: tuple[str, ...] | list[str],
) -> list[str]:
    missing: list[str] = []
    for section_id in required_sections:
        entry = mapping_result.get(section_id)
        if entry is None or entry.get("match") is None:
            missing.append(section_id)
    return missing


def detect_low_confidence_mappings(mapping_result: dict[str, Any]) -> list[dict[str, Any]]:
    flagged: list[dict[str, Any]] = []
    for section_id, entry in mapping_result.items():
        confidence = float(entry.get("confidence") or 0.0)
        if entry.get("match") is not None and confidence < 0.55:
            flagged.append({"section_id": section_id, "confidence": round(confidence, 2)})
    return flagged


def _mapped_text(entry: dict[str, Any] | None) -> str:
    if not entry or entry.get("match") is None:
        return ""
    content = entry["match"].get("content")
    if isinstance(content, list):
        return "\n".join(str(item) for item in content if str(item).strip())
    return str(content or "").strip()


def convert_to_draft(
    *,
    ingestion_id: str,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    team: str,
    review_cadence: str,
    status: str,
    audience: str,
    actor: str,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
) -> dict[str, Any]:
    actor = require_actor_id(actor)
    detail = ingestion_detail(ingestion_id=ingestion_id, database_path=database_path)
    mapping_result = detail.get("mapping_result") or map_to_blueprint(
        ingestion_id=ingestion_id,
        blueprint_id=detail["classification"]["blueprint_id"],
        database_path=database_path,
    )
    blueprint = get_blueprint(str(mapping_result["blueprint_id"]))
    workflow = GovernanceWorkflow(Path(database_path), source_root=Path(source_root))

    try:
        workflow.create_object(
            object_id=object_id,
            object_type=blueprint.blueprint_id,
            title=title,
            summary=str(detail["normalized_content"].get("title") or title),
            owner=owner,
            team=team,
            canonical_path=canonical_path,
            actor=actor,
            status=status,
            review_cadence=review_cadence,
        )
    except ValueError:
        pass

    created = create_draft_from_blueprint(
        object_id=object_id,
        blueprint_id=blueprint.blueprint_id,
        actor=actor,
        database_path=Path(database_path),
        source_root=Path(source_root),
    )
    revision_id = str(created["revision_id"])
    update_section(
        object_id=object_id,
        revision_id=revision_id,
        section_id="identity",
        values={
            "object_id": object_id,
            "title": title,
            "canonical_path": canonical_path,
        },
        actor=actor,
        database_path=Path(database_path),
        source_root=Path(source_root),
    )
    update_section(
        object_id=object_id,
        revision_id=revision_id,
        section_id="stewardship",
        values={
            "summary": str(detail["normalized_content"].get("title") or title),
            "owner": owner,
            "team": team,
            "status": status,
            "review_cadence": review_cadence,
            "audience": audience,
            "systems": [],
            "tags": [],
            "related_services": [],
            "related_object_ids": [],
            "change_summary": f"Imported from {detail['filename']}.",
        },
        actor=actor,
        database_path=Path(database_path),
        source_root=Path(source_root),
    )
    for section_id in blueprint.ordering:
        if section_id in {"identity", "stewardship", "evidence", "relationships"}:
            continue
        mapping_entry = mapping_result["sections"].get(section_id)
        mapped_text = _mapped_text(mapping_entry)
        if not mapped_text:
            continue
        section = blueprint.section(section_id)
        values: dict[str, Any] = {}
        for field in section.fields:
            kind = str(field.get("kind") or "text")
            name = str(field["name"])
            if kind == "list":
                values[name] = mapped_text.splitlines()
            else:
                values[name] = mapped_text
        update_section(
            object_id=object_id,
            revision_id=revision_id,
            section_id=section_id,
            values=values,
            actor=actor,
            database_path=Path(database_path),
            source_root=Path(source_root),
        )
    converted = validate_draft_progress(object_id=object_id, revision_id=revision_id, database_path=Path(database_path))
    mark_ingestion_converted(
        ingestion_id=ingestion_id,
        object_id=object_id,
        revision_id=revision_id,
        database_path=Path(database_path),
    )
    return {
        "object_id": object_id,
        "revision_id": revision_id,
        "completion": converted["completion"],
        "blueprint": blueprint,
    }
