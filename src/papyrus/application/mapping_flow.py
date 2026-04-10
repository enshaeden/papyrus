from __future__ import annotations

from pathlib import Path
from typing import Any

from papyrus.application.authoring_flow import (
    CONVERSION_GAPS_KEY,
    FIELD_PROVENANCE_KEY,
    create_draft_from_blueprint,
    update_section,
    validate_draft_progress,
)
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.application.ingestion_flow import ingestion_detail, mark_ingestion_converted, update_ingestion_mapping
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.review_flow import GovernanceWorkflow
from papyrus.domain.actor import require_actor_id
from papyrus.domain.ingestion import has_mapping_result
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
FRAGMENT_KIND_WEIGHT = {
    "paragraph": 1.0,
    "list": 0.95,
    "table": 0.85,
    "heading": 0.6,
}
MAPPABLE_FRAGMENT_KINDS = {"paragraph", "list", "table"}
CONFLICT_CONFIDENCE_THRESHOLD = 0.55
FIELD_IMPORT_CONFIDENCE_THRESHOLD = 0.7
FIELD_IMPORT_RULES: dict[str, dict[str, dict[str, dict[str, Any]]]] = {
    "runbook": {
        "purpose": {
            "use_when": {"keywords": ("use when", "purpose", "overview", "summary"), "mode": "text"},
        },
        "prerequisites": {
            "prerequisites": {
                "keywords": ("prerequisite", "before", "access"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "procedure": {
            "steps": {"keywords": ("procedure", "step", "workflow"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "verification": {
            "verification": {
                "keywords": ("verification", "verify", "validation", "confirm"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "rollback": {
            "rollback": {"keywords": ("rollback", "undo", "recovery"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "boundaries": {
            "boundaries_and_escalation": {"keywords": ("boundary", "boundaries", "escalation", "scope"), "mode": "text"},
            "related_knowledge_notes": {"keywords": ("related knowledge", "knowledge notes", "follow-on"), "mode": "text"},
        },
    },
    "known_error": {
        "diagnosis": {
            "symptoms": {"keywords": ("symptom", "symptoms", "failure", "error"), "mode": "list", "allow_paragraph_to_list": True},
            "scope": {"keywords": ("scope", "affected", "impact", "boundary"), "mode": "text"},
            "cause": {"keywords": ("cause", "root cause", "because"), "mode": "text"},
        },
        "diagnostic_checks": {
            "diagnostic_checks": {
                "keywords": ("diagnostic", "check", "validate", "verify", "test"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "mitigations": {
            "mitigations": {
                "keywords": ("mitigation", "mitigations", "workaround", "recovery"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
            "permanent_fix_status": {"mode": "manual_only"},
        },
        "escalation": {
            "detection_notes": {"keywords": ("detection", "alert", "monitor"), "mode": "text"},
            "escalation_threshold": {"keywords": ("escalation", "threshold", "escalate", "page"), "mode": "text"},
            "evidence_notes": {"keywords": ("evidence note", "evidence", "log", "reference"), "mode": "text"},
        },
    },
    "service_record": {
        "service_profile": {
            "service_name": {"mode": "manual_only"},
            "service_criticality": {"mode": "manual_only"},
            "scope_notes": {"keywords": ("scope", "service profile", "overview"), "mode": "text"},
        },
        "dependencies": {
            "dependencies": {"keywords": ("dependency", "dependencies", "depends"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "support_entrypoints": {
            "support_entrypoints": {
                "keywords": ("support entrypoint", "entrypoint", "contact", "support"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "failure_modes": {
            "common_failure_modes": {
                "keywords": ("failure mode", "failure", "degradation", "issue"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "operations": {
            "operational_notes": {"keywords": ("operational notes", "operations", "caveat"), "mode": "text"},
            "evidence_notes": {"keywords": ("evidence note", "evidence"), "mode": "text"},
            "related_runbooks": {"mode": "manual_only"},
            "related_known_errors": {"mode": "manual_only"},
        },
    },
    "policy": {
        "policy_scope": {
            "policy_scope": {"keywords": ("policy scope", "scope", "purpose"), "mode": "text"},
        },
        "controls": {
            "controls": {"keywords": ("control", "controls", "requirement", "must", "shall"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "exceptions": {
            "exceptions": {"keywords": ("exception", "exceptions", "waiver"), "mode": "text"},
        },
    },
    "system_design": {
        "architecture": {
            "architecture": {"keywords": ("architecture", "design", "component"), "mode": "text"},
        },
        "dependencies": {
            "dependencies": {"keywords": ("dependency", "dependencies", "depends"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "interfaces": {
            "interfaces": {"keywords": ("interface", "interfaces", "integration", "api"), "mode": "list", "allow_paragraph_to_list": True},
        },
        "failure_modes": {
            "common_failure_modes": {
                "keywords": ("failure mode", "failure", "degradation", "issue"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
        "operations": {
            "operational_notes": {"keywords": ("operational notes", "operations", "support posture"), "mode": "text"},
            "support_entrypoints": {
                "keywords": ("support entrypoint", "support entrypoints", "contact"),
                "mode": "list",
                "allow_paragraph_to_list": True,
            },
        },
    },
}


def _fragment_text(fragment: dict[str, Any]) -> str:
    text = str(fragment.get("text") or "").strip()
    if text:
        return text
    content = fragment.get("content")
    if isinstance(content, list):
        if content and isinstance(content[0], list):
            rows = [row for row in content if isinstance(row, list)]
            return "\n".join(" | ".join(str(cell).strip() for cell in row if str(cell).strip()) for row in rows)
        return "\n".join(str(item).strip() for item in content if str(item).strip())
    return str(content or "").strip()


def _normalized_fragment(fragment: dict[str, Any], index: int) -> dict[str, Any]:
    kind = str(fragment.get("kind") or "paragraph").strip() or "paragraph"
    heading = str(fragment.get("heading") or "").strip()
    heading_path = fragment.get("heading_path")
    if isinstance(heading_path, list):
        normalized_heading_path = [
            {
                "level": max(1, int(item.get("level") or 1)) if isinstance(item, dict) else 1,
                "text": str(item.get("text") or "").strip() if isinstance(item, dict) else "",
            }
            for item in heading_path
            if isinstance(item, dict) and str(item.get("text") or "").strip()
        ]
    else:
        normalized_heading_path = [{"level": 1, "text": heading}] if heading else []
    try:
        order = max(1, int(fragment.get("order") or (index + 1)))
    except (TypeError, ValueError):
        order = index + 1
    source = fragment.get("source") if isinstance(fragment.get("source"), dict) else {}
    text = _fragment_text(fragment)
    return {
        "fragment_id": str(fragment.get("fragment_id") or f"fragment-{order:04d}"),
        "order": order,
        "kind": kind,
        "heading": heading or (normalized_heading_path[-1]["text"] if normalized_heading_path else ""),
        "heading_path": normalized_heading_path,
        "content": fragment.get("content"),
        "text": text,
        "source": {
            "element_index": int(source.get("element_index") or index),
            "kind": str(source.get("kind") or kind),
            "legacy": bool(source.get("legacy")) or "fragment_id" not in fragment,
        },
    }


def _rank_fragment(
    *,
    section_id: str,
    fragment: dict[str, Any],
    keywords: tuple[str, ...],
) -> tuple[float, list[str]]:
    if not keywords:
        return 0.0, []
    active_heading = str(fragment.get("heading") or "").lower()
    body_text = _fragment_text(fragment).lower()
    matched_keywords = sorted(
        {
            keyword
            for keyword in keywords
            if keyword in active_heading or keyword in body_text
        }
    )
    if not matched_keywords:
        return 0.0, []
    score = 0.0
    for keyword in matched_keywords:
        if keyword in active_heading:
            score += 0.45
        if keyword in body_text:
            score += 0.25
    score *= FRAGMENT_KIND_WEIGHT.get(str(fragment.get("kind") or "paragraph"), 0.8)
    if section_id in {"evidence", "relationships"} and "reference" in matched_keywords:
        score += 0.1
    return min(0.95, round(score, 2)), matched_keywords


def _fragment_provenance(fragment: dict[str, Any] | None) -> dict[str, Any] | None:
    if fragment is None:
        return None
    source = fragment.get("source") if isinstance(fragment.get("source"), dict) else {}
    return {
        "source_fragment_id": str(fragment.get("fragment_id") or ""),
        "fragment_order": int(fragment.get("order") or 0),
        "source_kind": str(fragment.get("kind") or ""),
        "source_heading": str(fragment.get("heading") or ""),
        "heading_path": fragment.get("heading_path") if isinstance(fragment.get("heading_path"), list) else [],
        "source_element_index": int(source.get("element_index") or 0),
        "source_text": _fragment_text(fragment),
    }


def _section_keywords(section_id: str) -> tuple[str, ...]:
    raw_keywords = list(SECTION_KEYWORDS.get(section_id, ()))
    raw_keywords.extend(part for part in section_id.split("_") if part)
    raw_keywords.append(section_id.replace("_", " "))
    return tuple(dict.fromkeys(keyword for keyword in raw_keywords if keyword))


def _mapping_candidates(
    *,
    blueprint,
    fragments: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    candidates_by_section: dict[str, list[dict[str, Any]]] = {}
    for section_id in blueprint.ordering:
        keywords = _section_keywords(section_id)
        ranked: list[dict[str, Any]] = []
        for fragment in fragments:
            if str(fragment.get("kind") or "") not in MAPPABLE_FRAGMENT_KINDS:
                continue
            confidence, matched_keywords = _rank_fragment(section_id=section_id, fragment=fragment, keywords=keywords)
            if confidence <= 0.0:
                continue
            ranked.append(
                {
                    "section_id": section_id,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                    "fragment": fragment,
                }
            )
        ranked.sort(
            key=lambda item: (
                -float(item["confidence"]),
                int(item["fragment"]["order"]),
                str(item["fragment"]["fragment_id"]),
            )
        )
        candidates_by_section[section_id] = ranked
    return candidates_by_section


def _assigned_candidates(
    *,
    blueprint,
    candidates_by_section: dict[str, list[dict[str, Any]]],
) -> tuple[dict[str, dict[str, Any] | None], dict[str, str]]:
    section_priority = {section_id: index for index, section_id in enumerate(blueprint.ordering)}
    assigned: dict[str, dict[str, Any] | None] = {section_id: None for section_id in blueprint.ordering}
    fragment_usage: dict[str, str] = {}
    all_candidates = [
        candidate
        for section_candidates in candidates_by_section.values()
        for candidate in section_candidates
    ]
    all_candidates.sort(
        key=lambda item: (
            -float(item["confidence"]),
            int(item["fragment"]["order"]),
            section_priority[str(item["section_id"])],
            str(item["section_id"]),
        )
    )
    for candidate in all_candidates:
        section_id = str(candidate["section_id"])
        fragment_id = str(candidate["fragment"]["fragment_id"])
        if assigned[section_id] is not None or fragment_id in fragment_usage:
            continue
        assigned[section_id] = candidate
        fragment_usage[fragment_id] = section_id
    return assigned, fragment_usage


def _mapping_conflicts(
    *,
    candidates_by_section: dict[str, list[dict[str, Any]]],
    fragment_usage: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    candidates_by_fragment: dict[str, list[dict[str, Any]]] = {}
    for section_candidates in candidates_by_section.values():
        for candidate in section_candidates:
            if float(candidate["confidence"]) < CONFLICT_CONFIDENCE_THRESHOLD:
                continue
            fragment_id = str(candidate["fragment"]["fragment_id"])
            candidates_by_fragment.setdefault(fragment_id, []).append(candidate)
    conflicts: list[dict[str, Any]] = []
    conflicts_by_section: dict[str, list[dict[str, Any]]] = {}
    for fragment_id, contenders in candidates_by_fragment.items():
        if len(contenders) <= 1 or fragment_id not in fragment_usage:
            continue
        contenders.sort(key=lambda item: (-float(item["confidence"]), str(item["section_id"])))
        assigned_section_id = fragment_usage[fragment_id]
        fragment = contenders[0]["fragment"]
        conflict_entry = {
            "source_fragment_id": fragment_id,
            "fragment_order": int(fragment.get("order") or 0),
            "source_heading": str(fragment.get("heading") or ""),
            "source_text": _fragment_text(fragment),
            "assigned_section_id": assigned_section_id,
            "competing_sections": [],
        }
        for contender in contenders:
            section_id = str(contender["section_id"])
            competitor = {
                "section_id": section_id,
                "confidence": round(float(contender["confidence"]), 2),
                "matched_keywords": list(contender.get("matched_keywords", [])),
                "outcome": "selected" if section_id == assigned_section_id else "blocked_duplicate_source_reuse",
            }
            conflict_entry["competing_sections"].append(competitor)
            conflicts_by_section.setdefault(section_id, []).append(
                {
                    "source_fragment_id": fragment_id,
                    "fragment_order": int(fragment.get("order") or 0),
                    "source_heading": str(fragment.get("heading") or ""),
                    "source_text": _fragment_text(fragment),
                    "assigned_section_id": assigned_section_id,
                    "confidence": round(float(contender["confidence"]), 2),
                    "matched_keywords": list(contender.get("matched_keywords", [])),
                    "outcome": competitor["outcome"],
                }
            )
        conflicts.append(conflict_entry)
    conflicts.sort(key=lambda item: (int(item["fragment_order"]), str(item["source_fragment_id"])))
    return conflicts, conflicts_by_section


def _low_confidence_mappings(mapping_result: dict[str, Any]) -> list[dict[str, Any]]:
    flagged: list[dict[str, Any]] = []
    for section_id, entry in mapping_result.items():
        confidence = float(entry.get("confidence") or 0.0)
        provenance = entry.get("provenance") if isinstance(entry.get("provenance"), dict) else {}
        if entry.get("match") is not None and confidence < CONFLICT_CONFIDENCE_THRESHOLD:
            flagged.append(
                {
                    "section_id": section_id,
                    "confidence": round(confidence, 2),
                    "source_fragment_id": str(provenance.get("source_fragment_id") or ""),
                    "source_heading": str(provenance.get("source_heading") or ""),
                }
            )
    return flagged


def map_to_blueprint(
    *,
    ingestion_id: str,
    blueprint_id: str | None = None,
    database_path: Path = DB_PATH,
) -> dict[str, Any]:
    detail = ingestion_detail(ingestion_id=ingestion_id, database_path=database_path)
    resolved_blueprint_id = blueprint_id or detail.get("blueprint_id") or detail["classification"]["blueprint_id"]
    blueprint = get_blueprint(str(resolved_blueprint_id))
    fragments: list[dict[str, Any]] = []
    for artifact in detail["artifacts"]:
        if artifact["artifact_type"] == "sections":
            raw_sections = artifact["content"].get("sections", [])
            if isinstance(raw_sections, list):
                fragments = [_normalized_fragment(fragment, index) for index, fragment in enumerate(raw_sections) if isinstance(fragment, dict)]
            break
    candidates_by_section = _mapping_candidates(blueprint=blueprint, fragments=fragments)
    assigned, fragment_usage = _assigned_candidates(blueprint=blueprint, candidates_by_section=candidates_by_section)
    conflicts, conflicts_by_section = _mapping_conflicts(
        candidates_by_section=candidates_by_section,
        fragment_usage=fragment_usage,
    )
    mapped_sections: dict[str, dict[str, Any]] = {}
    for section_id in blueprint.ordering:
        assignment = assigned.get(section_id)
        best_match = assignment["fragment"] if assignment is not None else None
        best_score = float(assignment["confidence"]) if assignment is not None else 0.0
        section_conflicts = conflicts_by_section.get(section_id, [])
        conflict_state = "conflicted" if section_conflicts else "clear" if best_match is not None else "unmapped"
        mapped_sections[section_id] = {
            "match": best_match,
            "confidence": round(best_score, 2),
            "required": section_id in blueprint.required_sections,
            "matched_keywords": list(assignment.get("matched_keywords", [])) if assignment is not None else [],
            "provenance": _fragment_provenance(best_match),
            "conflict_state": conflict_state,
            "conflicts": section_conflicts,
        }

    unmapped = [fragment for fragment in fragments if str(fragment["fragment_id"]) not in fragment_usage]

    result = {
        "blueprint_id": blueprint.blueprint_id,
        "sections": mapped_sections,
        "missing_sections": identify_missing_sections(mapped_sections, blueprint.required_sections),
        "low_confidence": detect_low_confidence_mappings(mapped_sections),
        "conflicts": conflicts,
        "unmapped_content": unmapped,
    }
    update_ingestion_mapping(
        ingestion_id=ingestion_id,
        mapping_result=result,
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
    return _low_confidence_mappings(mapping_result)


def _mapped_text(entry: dict[str, Any] | None) -> str:
    if not entry or entry.get("match") is None:
        return ""
    return _fragment_text(entry["match"])


def _empty_field_value(field: dict[str, Any]) -> Any:
    kind = str(field.get("kind") or "text")
    return [] if kind in {"list", "references"} else ""


def _section_field_rules(blueprint_id: str, section_id: str) -> dict[str, dict[str, Any]]:
    return FIELD_IMPORT_RULES.get(blueprint_id, {}).get(section_id, {})


def _field_keywords(section_id: str, field_name: str, rule: dict[str, Any]) -> tuple[str, ...]:
    raw_keywords = list(rule.get("keywords", ()))
    if not raw_keywords:
        raw_keywords.extend(part for part in section_id.split("_") if part)
        raw_keywords.extend(part for part in field_name.split("_") if part)
        raw_keywords.append(section_id.replace("_", " "))
        raw_keywords.append(field_name.replace("_", " "))
    return tuple(dict.fromkeys(keyword for keyword in raw_keywords if keyword))


def _field_value_from_fragment(field: dict[str, Any], fragment: dict[str, Any], rule: dict[str, Any]) -> Any | None:
    kind = str(field.get("kind") or "text")
    fragment_kind = str(fragment.get("kind") or "")
    text = _fragment_text(fragment)
    if kind == "references" or str(rule.get("mode") or "") == "manual_only":
        return None
    if fragment_kind == "heading":
        return None
    if kind == "list":
        if fragment_kind == "list":
            content = fragment.get("content")
            if isinstance(content, list):
                return [str(item).strip() for item in content if str(item).strip()]
        if rule.get("allow_paragraph_to_list") and fragment_kind in {"paragraph", "table"} and text:
            return [line.strip() for line in text.splitlines() if line.strip()] or [text]
        return None
    if kind == "select":
        return None
    if fragment_kind in {"paragraph", "heading", "table"} and text:
        return text
    if fragment_kind == "list" and rule.get("allow_list_to_text"):
        return text
    return None


def _field_candidate_score(
    *,
    field: dict[str, Any],
    fragment: dict[str, Any],
    keywords: tuple[str, ...],
    rule: dict[str, Any],
    section_match_fragment_id: str | None,
) -> tuple[float, list[str]]:
    active_heading = str(fragment.get("heading") or "").lower()
    body_text = _fragment_text(fragment).lower()
    matched_keywords = sorted({keyword for keyword in keywords if keyword in active_heading or keyword in body_text})
    if not matched_keywords:
        return 0.0, []
    score = 0.0
    for keyword in matched_keywords:
        if keyword in active_heading:
            score += 0.65
        if keyword in body_text:
            score += 0.35
    if str(field.get("kind") or "text") == "list" and str(fragment.get("kind") or "") == "list":
        score += 0.2
    if str(field.get("kind") or "text") in {"text", "long_text"} and str(fragment.get("kind") or "") in {"paragraph", "table"}:
        score += 0.1
    if section_match_fragment_id and str(fragment.get("fragment_id") or "") == section_match_fragment_id:
        score += 0.05
    return min(0.99, round(score, 2)), matched_keywords


def _blank_field_provenance(
    *,
    field: dict[str, Any],
    status: str,
    note: str,
    candidate: dict[str, Any] | None = None,
) -> dict[str, Any]:
    provenance = {
        "status": status,
        "note": note,
    }
    if candidate is not None:
        provenance.update(
            {
                "candidate_fragment_id": str(candidate["fragment"].get("fragment_id") or ""),
                "candidate_heading": str(candidate["fragment"].get("heading") or ""),
                "candidate_confidence": round(float(candidate.get("confidence") or 0.0), 2),
            }
        )
    return provenance


def _mapped_field_provenance(
    *,
    mapping_entry: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    fragment = candidate["fragment"]
    return {
        "status": "mapped",
        "source_fragment_id": str(fragment.get("fragment_id") or ""),
        "source_fragment_order": int(fragment.get("order") or 0),
        "source_heading": str(fragment.get("heading") or ""),
        "source_text_preview": _fragment_text(fragment)[:240],
        "mapping_confidence": round(float(candidate.get("confidence") or 0.0), 2),
        "mapping_conflict_state": str(mapping_entry.get("conflict_state") or "clear"),
        "note": "Imported from the mapped ingestion fragment.",
    }


def _manual_input_provenance(note: str) -> dict[str, Any]:
    return {"status": "manual_input", "note": note}


def _section_fragment_pool(
    *,
    mapping_result: dict[str, Any],
    section_id: str,
) -> list[dict[str, Any]]:
    fragments: list[dict[str, Any]] = []
    seen: set[str] = set()
    section_entry = mapping_result.get("sections", {}).get(section_id, {}) if isinstance(mapping_result.get("sections"), dict) else {}
    match = section_entry.get("match") if isinstance(section_entry, dict) else None
    if isinstance(match, dict):
        fragment_id = str(match.get("fragment_id") or "")
        if fragment_id:
            seen.add(fragment_id)
        fragments.append(match)
    for item in mapping_result.get("unmapped_content", []):
        if not isinstance(item, dict):
            continue
        fragment_id = str(item.get("fragment_id") or "")
        if fragment_id in seen:
            continue
        seen.add(fragment_id)
        fragments.append(item)
    return fragments


def _field_import_plan(
    *,
    blueprint_id: str,
    section,
    mapping_entry: dict[str, Any],
    mapping_result: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    values: dict[str, Any] = {}
    field_provenance: dict[str, dict[str, Any]] = {}
    conversion_gaps: list[dict[str, Any]] = []
    used_fragments: set[str] = set()
    section_match_fragment_id = (
        str(mapping_entry.get("match", {}).get("fragment_id") or "")
        if isinstance(mapping_entry.get("match"), dict)
        else None
    )
    fragment_pool = _section_fragment_pool(mapping_result=mapping_result, section_id=section.section_id)
    section_rules = _section_field_rules(blueprint_id, section.section_id)

    for field in section.fields:
        field_name = str(field["name"])
        rule = section_rules.get(field_name, {})
        values[field_name] = _empty_field_value(field)
        if str(rule.get("mode") or "") == "manual_only":
            status = "manual_required" if bool(field.get("required", True)) else "unresolved"
            note = "Papyrus does not infer this field safely from imported source text."
            field_provenance[field_name] = _blank_field_provenance(field=field, status=status, note=note)
            conversion_gaps.append({"field": field_name, "status": status, "reason": note})
            continue
        keywords = _field_keywords(section.section_id, field_name, rule)
        candidates: list[dict[str, Any]] = []
        for fragment in fragment_pool:
            fragment_id = str(fragment.get("fragment_id") or "")
            if fragment_id in used_fragments and not bool(rule.get("allow_reuse")):
                continue
            candidate_value = _field_value_from_fragment(field, fragment, rule)
            if candidate_value is None:
                continue
            confidence, matched_keywords = _field_candidate_score(
                field=field,
                fragment=fragment,
                keywords=keywords,
                rule=rule,
                section_match_fragment_id=section_match_fragment_id,
            )
            if confidence <= 0.0:
                continue
            candidates.append(
                {
                    "fragment": fragment,
                    "value": candidate_value,
                    "confidence": confidence,
                    "matched_keywords": matched_keywords,
                }
            )
        candidates.sort(
            key=lambda item: (
                -float(item["confidence"]),
                int(item["fragment"].get("order") or 0),
                str(item["fragment"].get("fragment_id") or ""),
            )
        )
        best_candidate = candidates[0] if candidates else None
        if best_candidate is not None and float(best_candidate["confidence"]) >= float(rule.get("min_confidence") or FIELD_IMPORT_CONFIDENCE_THRESHOLD):
            values[field_name] = best_candidate["value"]
            field_provenance[field_name] = _mapped_field_provenance(mapping_entry=mapping_entry, candidate=best_candidate)
            if not bool(rule.get("allow_reuse")):
                used_fragments.add(str(best_candidate["fragment"].get("fragment_id") or ""))
            continue
        if best_candidate is not None:
            note = "Best import candidate was below the confidence threshold, so the field was left blank."
            field_provenance[field_name] = _blank_field_provenance(
                field=field,
                status="low_confidence",
                note=note,
                candidate=best_candidate,
            )
            conversion_gaps.append(
                {
                    "field": field_name,
                    "status": "low_confidence",
                    "reason": note,
                    "candidate_fragment_id": str(best_candidate["fragment"].get("fragment_id") or ""),
                }
            )
            continue
        status = "manual_required" if bool(field.get("required", True)) else "unresolved"
        note = "No confident source fragment matched this field during import conversion."
        field_provenance[field_name] = _blank_field_provenance(field=field, status=status, note=note)
        conversion_gaps.append({"field": field_name, "status": status, "reason": note})

    return values, {FIELD_PROVENANCE_KEY: field_provenance, CONVERSION_GAPS_KEY: conversion_gaps}


def convert_to_draft(
    *,
    ingestion_id: str,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    team: str,
    review_cadence: str,
    object_lifecycle_state: str,
    audience: str,
    actor: str,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> dict[str, Any]:
    actor = require_actor_id(actor)
    detail = ingestion_detail(ingestion_id=ingestion_id, database_path=database_path)
    if detail.get("converted_revision_id"):
        raise ValueError(f"ingestion {ingestion_id} has already been reviewed and converted")
    existing_mapping = detail.get("mapping_result") if has_mapping_result(detail.get("mapping_result")) else None
    mapping_result = existing_mapping or map_to_blueprint(
        ingestion_id=ingestion_id,
        blueprint_id=detail["classification"]["blueprint_id"],
        database_path=database_path,
    )
    blueprint = get_blueprint(str(mapping_result["blueprint_id"]))
    workflow = GovernanceWorkflow(
        Path(database_path),
        source_root=Path(source_root),
        authority=authority,
    )

    try:
        workflow.create_object(
            object_id=object_id,
            object_type=blueprint.blueprint_id,
            title=title,
            summary="",
            owner=owner,
            team=team,
            canonical_path=canonical_path,
            actor=actor,
            object_lifecycle_state=object_lifecycle_state,
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
        section_metadata={
            FIELD_PROVENANCE_KEY: {
                "object_id": _manual_input_provenance("Provided during import conversion."),
                "title": _manual_input_provenance("Provided during import conversion."),
                "canonical_path": _manual_input_provenance("Provided during import conversion."),
            },
            CONVERSION_GAPS_KEY: [],
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
            "summary": "",
            "owner": owner,
            "team": team,
            "object_lifecycle_state": object_lifecycle_state,
            "review_cadence": review_cadence,
            "audience": audience,
            "systems": [],
            "tags": [],
            "related_services": [],
            "related_object_ids": [],
            "change_summary": f"Imported from {detail['filename']}.",
        },
        section_metadata={
            FIELD_PROVENANCE_KEY: {
                "summary": {
                    "status": "manual_required",
                    "note": "Import conversion did not infer a reliable stewardship summary.",
                },
                "owner": _manual_input_provenance("Provided during import conversion."),
                "team": _manual_input_provenance("Provided during import conversion."),
                "object_lifecycle_state": _manual_input_provenance("Provided during import conversion."),
                "review_cadence": _manual_input_provenance("Provided during import conversion."),
                "audience": _manual_input_provenance("Provided during import conversion."),
                "systems": {"status": "unresolved", "note": "No structured system mapping was inferred from the import."},
                "tags": {"status": "unresolved", "note": "No structured tag mapping was inferred from the import."},
                "related_services": {"status": "unresolved", "note": "No related services were inferred from the import."},
                "related_object_ids": {"status": "unresolved", "note": "No related object IDs were inferred from the import."},
                "change_summary": _manual_input_provenance("Recorded by the import conversion workflow."),
            },
            CONVERSION_GAPS_KEY: [
                {
                    "field": "summary",
                    "status": "manual_required",
                    "reason": "Import conversion did not infer a reliable stewardship summary.",
                }
            ],
        },
        actor=actor,
        database_path=Path(database_path),
        source_root=Path(source_root),
    )
    for section_id in blueprint.ordering:
        if section_id in {"identity", "stewardship"}:
            continue
        mapping_entry = mapping_result["sections"].get(section_id)
        section = blueprint.section(section_id)
        values, section_metadata = _field_import_plan(
            blueprint_id=blueprint.blueprint_id,
            section=section,
            mapping_entry=mapping_entry if isinstance(mapping_entry, dict) else {},
            mapping_result=mapping_result,
        )
        update_section(
            object_id=object_id,
            revision_id=revision_id,
            section_id=section_id,
            values=values,
            section_metadata=section_metadata,
            actor=actor,
            database_path=Path(database_path),
            source_root=Path(source_root),
        )
    converted = validate_draft_progress(
        object_id=object_id,
        revision_id=revision_id,
        database_path=Path(database_path),
        source_root=Path(source_root),
    )
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
