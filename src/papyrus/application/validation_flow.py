from __future__ import annotations

import datetime as dt
import re
from typing import Any, Iterable

from papyrus.application.export_flow import ExportRuntimeUnavailableError, filter_approved_export_documents
from papyrus.application.impact_flow import find_possible_duplicate_documents
from papyrus.application.authoring_flow import compute_completion_state, derive_section_content
from papyrus.application.blueprint_registry import get_blueprint
from papyrus.domain.actor import require_actor_id
from papyrus.domain.entities import KnowledgeDocument, ValidationIssue
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.parser import (
    LEGACY_FIELD_NOTE_PREFIX,
    collect_broken_markdown_links,
    collect_broken_rendered_site_links,
    extract_markdown_title,
    normalize_object_metadata,
)
from papyrus.infrastructure.markdown.serializer import ensure_iso_date, json_dump, parse_iso_date, similarity_ratio
from papyrus.infrastructure.markdown.serializer import ensure_iso_date_or_datetime
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import (
    ADDRESS_PATTERN,
    BRANDED_ADMIN_PATTERNS,
    BUILD_DIR,
    DB_PATH,
    DOMAIN_PATTERN,
    EMAIL_PATTERN,
    GENERATED_DIR,
    GENERATED_SITE_ASSET_PATHS,
    GENERATED_SITE_DOCS_DIR,
    GENERIC_BRAND_ALLOWLIST,
    IP_PATTERN,
    LEGACY_GENERATED_DOCS_DIR,
    LIKELY_BRANDED_PRODUCT_PATTERN,
    PHONE_PATTERN,
    REPORTS_DIR,
    ROOT,
    SECRET_PATTERNS,
    SITE_DIR,
    TAXONOMY_DIR,
    TEMPLATE_DIR,
    relative_path,
)
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    collect_article_paths,
    collect_decision_paths,
    collect_docs_source_paths,
    collect_root_markdown_paths,
    collect_sanitization_paths,
    load_knowledge_documents,
    load_object_schemas,
    load_policy,
    load_schema,
    load_taxonomies,
)
from papyrus.infrastructure.repositories.validation_repo import insert_validation_run
from papyrus.infrastructure.search.indexer import fts5_available, site_knowledge_output_path, site_relative_path_for_repo_path

MARKDOWN_SECTION_PATTERN = re.compile(r"^## (?P<title>.+?)\n+(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
BLUEPRINT_SECTION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "purpose": ("purpose", "overview", "summary", "use when"),
    "prerequisites": ("prerequisite", "before", "access"),
    "procedure": ("step", "procedure", "workflow"),
    "verification": ("verify", "validation", "confirm"),
    "rollback": ("rollback", "undo", "recovery"),
    "boundaries": ("boundary", "escalation", "scope"),
    "diagnosis": ("symptom", "scope", "cause", "overview"),
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


def validate_field(
    path: str,
    field_name: str,
    value: Any,
    spec: dict[str, Any],
    taxonomies: dict[str, dict[str, Any]],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    kind = spec.get("kind")

    if kind == "string":
        if not isinstance(value, str) or not value.strip():
            issues.append(ValidationIssue(path, "must be a non-empty string", field_name))
        pattern = spec.get("pattern")
        if pattern and isinstance(value, str) and not re.match(pattern, value):
            issues.append(ValidationIssue(path, f"must match pattern {pattern}", field_name))
    elif kind == "string_or_null":
        if value is not None and (not isinstance(value, str) or not value.strip()):
            issues.append(ValidationIssue(path, "must be null or a non-empty string", field_name))
    elif kind == "date":
        if not ensure_iso_date(value):
            issues.append(ValidationIssue(path, "must be an ISO 8601 date (YYYY-MM-DD)", field_name))
    elif kind == "list[string]":
        if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
            issues.append(ValidationIssue(path, "must be a list of non-empty strings", field_name))
    elif kind == "list[object]":
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            issues.append(ValidationIssue(path, "must be a list of objects", field_name))
        else:
            required_keys = set(spec.get("required_keys", []))
            allowed_keys = set(spec.get("allowed_keys", []))
            for index, item in enumerate(value, start=1):
                missing = required_keys.difference(item.keys())
                unknown = set(item.keys()).difference(allowed_keys)
                if missing:
                    issues.append(
                        ValidationIssue(
                            path,
                            f"entry {index} is missing keys: {', '.join(sorted(missing))}",
                            field_name,
                        )
                    )
                if unknown:
                    issues.append(
                        ValidationIssue(
                            path,
                            f"entry {index} contains unknown keys: {', '.join(sorted(unknown))}",
                            field_name,
                        )
                    )
                if "date" in item and not ensure_iso_date(item["date"]):
                    issues.append(
                        ValidationIssue(
                            path,
                            f"entry {index} has a non-ISO date value",
                            field_name,
                        )
                    )
                if field_name == "citations":
                    captured_at = item.get("captured_at")
                    if captured_at is not None and not ensure_iso_date_or_datetime(captured_at):
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has a non-ISO captured_at value",
                                field_name,
                            )
                        )
                    evidence_expiry_at = item.get("evidence_expiry_at")
                    if evidence_expiry_at is not None and not ensure_iso_date_or_datetime(evidence_expiry_at):
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has a non-ISO evidence_expiry_at value",
                                field_name,
                            )
                        )
                    evidence_last_validated_at = item.get("evidence_last_validated_at")
                    if evidence_last_validated_at is not None and not ensure_iso_date_or_datetime(evidence_last_validated_at):
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has a non-ISO evidence_last_validated_at value",
                                field_name,
                            )
                        )
                    validity_status = item.get("validity_status")
                    if validity_status is not None and str(validity_status) not in {
                        "verified",
                        "unverified",
                        "stale",
                        "broken",
                    }:
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has an unsupported validity_status '{validity_status}'",
                                field_name,
                            )
                        )
                    evidence_snapshot_path = item.get("evidence_snapshot_path")
                    if evidence_snapshot_path is not None and (
                        not isinstance(evidence_snapshot_path, str) or not evidence_snapshot_path.strip()
                    ):
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has an empty evidence_snapshot_path",
                                field_name,
                            )
                        )
                    claim_anchor = item.get("claim_anchor")
                    if claim_anchor is not None and (not isinstance(claim_anchor, str) or not claim_anchor.strip()):
                        issues.append(
                            ValidationIssue(
                                path,
                                f"entry {index} has an empty claim_anchor",
                                field_name,
                            )
                        )
    else:
        issues.append(ValidationIssue(path, f"unsupported schema kind: {kind}", field_name))

    taxonomy_name = spec.get("taxonomy")
    if taxonomy_name and taxonomy_name in taxonomies:
        allowed = set(taxonomies[taxonomy_name]["allowed_values"])
        if kind == "string" and isinstance(value, str) and value not in allowed:
            issues.append(
                ValidationIssue(
                    path,
                    f"value '{value}' is not in taxonomy '{taxonomy_name}'",
                    field_name,
                )
            )
        if kind == "list[string]" and isinstance(value, list):
            for item in value:
                if isinstance(item, str) and item not in allowed:
                    issues.append(
                        ValidationIssue(
                            path,
                            f"value '{item}' is not in taxonomy '{taxonomy_name}'",
                            field_name,
                        )
                    )

    return issues


def _markdown_sections(body_markdown: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in MARKDOWN_SECTION_PATTERN.finditer(str(body_markdown or "").strip())
    }


def _meaningful_text(value: Any) -> bool:
    text = str(value or "").strip()
    return bool(text) and not text.startswith(LEGACY_FIELD_NOTE_PREFIX)


def _meaningful_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return any(_meaningful_text(item) for item in value)


def _meaningful_value(kind: str, value: Any) -> bool:
    if kind == "references":
        return isinstance(value, list) and any(
            isinstance(item, dict)
            and (_meaningful_text(item.get("source_title")) or _meaningful_text(item.get("source_ref")))
            for item in value
        )
    if kind == "list":
        return _meaningful_list(value)
    if kind == "select":
        return False
    return _meaningful_text(value)


def _contains_legacy_placeholder(value: Any) -> bool:
    if isinstance(value, list):
        return any(_contains_legacy_placeholder(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_legacy_placeholder(item) for item in value.values())
    return str(value or "").strip().startswith(LEGACY_FIELD_NOTE_PREFIX)


def _uses_legacy_blueprint_fallback(
    *,
    metadata: dict[str, Any],
    section_content: dict[str, dict[str, Any]],
) -> bool:
    if str(metadata.get("legacy_article_type") or "").strip():
        return True
    if str(metadata.get("source_type") or "").strip() in {"imported", "derived"}:
        return True
    return any(_contains_legacy_placeholder(values) for values in section_content.values())


def _legacy_body_supports_section(
    *,
    section_id: str,
    display_name: str,
    body_headings: tuple[str, ...],
    body_markdown: str,
    metadata: dict[str, Any],
) -> bool:
    markdown_sections = _markdown_sections(body_markdown)
    normalized_body = str(body_markdown or "").lower()
    keywords = {
        section_id.replace("_", " ").lower(),
        display_name.lower(),
        *(heading.lower() for heading in body_headings),
        *BLUEPRINT_SECTION_KEYWORDS.get(section_id, ()),
    }

    for heading, section_body in markdown_sections.items():
        normalized_heading = heading.lower()
        normalized_section_body = section_body.lower()
        if any(keyword and keyword in normalized_heading for keyword in keywords):
            return True
        if any(len(keyword) > 3 and keyword in normalized_section_body for keyword in keywords):
            return True

    if section_id in {"purpose", "policy_scope"} and _meaningful_text(metadata.get("summary")):
        return True
    if section_id in {"boundaries", "escalation"} and "escalat" in normalized_body:
        return True
    if section_id == "operations" and bool(markdown_sections):
        return True
    return False


def _legacy_section_complete(
    *,
    section,
    section_values: dict[str, Any],
    metadata: dict[str, Any],
    body_markdown: str,
) -> bool:
    if section.section_id == "evidence":
        return _meaningful_value("references", section_values.get("citations", []))

    meaningful_required_fields = 0
    for field in section.fields:
        if not bool(field.get("required", True)):
            continue
        kind = str(field.get("kind") or "text")
        value = section_values.get(str(field["name"]))
        if _meaningful_value(kind, value):
            meaningful_required_fields += 1

    if meaningful_required_fields:
        return True

    if _legacy_body_supports_section(
        section_id=section.section_id,
        display_name=section.display_name,
        body_headings=section.body_headings,
        body_markdown=body_markdown,
        metadata=metadata,
    ):
        return True

    return bool(str(body_markdown or "").strip())


def validate_sanitization(paths: Iterable) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for path in paths:
        text = path.read_text(encoding="utf-8")
        rel_path = relative_path(path)

        if re.search(r"https?://|mailto:", text):
            issues.append(ValidationIssue(rel_path, "contains a raw URL or mailto link; use placeholders or local links"))
        if EMAIL_PATTERN.search(text):
            issues.append(ValidationIssue(rel_path, "contains an email address"))
        if PHONE_PATTERN.search(text):
            issues.append(ValidationIssue(rel_path, "contains a phone number"))
        if IP_PATTERN.search(text):
            issues.append(ValidationIssue(rel_path, "contains an IP address or subnet"))
        if ADDRESS_PATTERN.search(text):
            issues.append(ValidationIssue(rel_path, "contains a physical address"))
        if DOMAIN_PATTERN.search(text):
            issues.append(ValidationIssue(rel_path, "contains a domain or hostname"))
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            issues.append(ValidationIssue(rel_path, "contains a credential-like value"))
        if any(pattern.search(text) for pattern in BRANDED_ADMIN_PATTERNS):
            issues.append(ValidationIssue(rel_path, "contains branded admin-console terminology"))
        for match in LIKELY_BRANDED_PRODUCT_PATTERN.finditer(text):
            tokens = match.group(0).replace("-", " ").split()
            if not all(token in GENERIC_BRAND_ALLOWLIST for token in tokens[:-1]):
                issues.append(ValidationIssue(rel_path, "contains a likely branded product term"))
                break

    return issues


def validate_directory_contract(policy: dict[str, Any]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    directory_policy = policy["directories"]
    allowed_dirs = set(directory_policy["allowed_top_level_directories"])
    ignored_dirs = set(directory_policy["ignored_top_level_directories"])
    allowed_files = set(directory_policy["allowed_top_level_files"])

    for path in sorted(ROOT.iterdir()):
        if path.is_dir():
            if path.name in allowed_dirs or path.name in ignored_dirs:
                continue
            if path.name.startswith("."):
                continue
            issues.append(ValidationIssue(path.name, "unexpected top-level directory"))
        elif path.is_file():
            if path.name in allowed_files or path.name.startswith("."):
                continue
            issues.append(ValidationIssue(path.name, "unexpected top-level file"))

    template_root = ROOT / directory_policy["template_root"]
    actual_template_files = sorted(path.name for path in template_root.glob("*.md"))
    expected_template_files = sorted(policy["templates"]["approved_files"])
    if actual_template_files != expected_template_files:
        issues.append(
            ValidationIssue(
                relative_path(template_root),
                f"approved template set mismatch: expected {expected_template_files}, found {actual_template_files}",
            )
        )

    if LEGACY_GENERATED_DOCS_DIR.exists():
        legacy_files = [path for path in LEGACY_GENERATED_DOCS_DIR.rglob("*") if path.is_file()]
        if legacy_files:
            issues.append(
                ValidationIssue(
                    relative_path(LEGACY_GENERATED_DOCS_DIR),
                    "legacy generated docs path contains files; derived site docs must live under generated/",
                )
            )

    build_files = []
    if BUILD_DIR.exists():
        build_files = [relative_path(path) for path in BUILD_DIR.iterdir() if path.is_file()]
    allowed_build_files = {
        "build/knowledge.db",
        "build/knowledge.db-shm",
        "build/knowledge.db-wal",
        "build/demo-knowledge.db",
        "build/demo-knowledge.db-shm",
        "build/demo-knowledge.db-wal",
    }
    for item in build_files:
        if item not in allowed_build_files:
            issues.append(ValidationIssue(item, "unexpected build artifact"))

    if GENERATED_DIR.exists():
        allowed_generated_roots = {relative_path(GENERATED_SITE_DOCS_DIR)}
        for path in GENERATED_DIR.iterdir():
            if relative_path(path) not in allowed_generated_roots:
                issues.append(ValidationIssue(relative_path(path), "unexpected generated artifact root"))

    return issues


def expected_site_doc_paths(
    documents: list[KnowledgeDocument],
    database_path=DB_PATH,
) -> set[str]:
    expected: set[str] = set()

    for path in collect_docs_source_paths():
        site_relative = site_relative_path_for_repo_path(relative_path(path))
        if site_relative is not None:
            expected.add(relative_path(GENERATED_SITE_DOCS_DIR / site_relative))
    for path in collect_decision_paths():
        site_relative = site_relative_path_for_repo_path(relative_path(path))
        if site_relative is not None:
            expected.add(relative_path(GENERATED_SITE_DOCS_DIR / site_relative))

    from papyrus.infrastructure.paths import GENERATED_SITE_INDEX_PATHS

    expected.update(relative_path(GENERATED_SITE_DOCS_DIR / path) for path in GENERATED_SITE_INDEX_PATHS)
    expected.update(relative_path(GENERATED_SITE_DOCS_DIR / path) for path in GENERATED_SITE_ASSET_PATHS)

    for document in filter_approved_export_documents(documents, database_path):
        expected.add(relative_path(site_knowledge_output_path(document)))

    return expected


def validate_generated_site_docs(
    documents: list[KnowledgeDocument],
    database_path=DB_PATH,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not GENERATED_SITE_DOCS_DIR.exists():
        return issues
    try:
        expected = expected_site_doc_paths(documents, database_path)
    except ExportRuntimeUnavailableError as exc:
        return [ValidationIssue(relative_path(GENERATED_SITE_DOCS_DIR), str(exc))]
    actual = {
        relative_path(path)
        for path in GENERATED_SITE_DOCS_DIR.rglob("*")
        if path.is_file()
    }
    for path in sorted(actual.difference(expected)):
        issues.append(ValidationIssue(path, "unexpected generated site source file"))
    for path in sorted(expected.difference(actual)):
        issues.append(ValidationIssue(path, "missing generated site source file"))
    return issues


def validate_docs_duplication(
    documents: list[KnowledgeDocument],
    policy: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    threshold = float(policy["duplicate_detection"]["doc_duplication_threshold"])
    for doc_path in collect_docs_source_paths():
        if doc_path.suffix != ".md":
            continue
        doc_text = doc_path.read_text(encoding="utf-8")
        doc_title = extract_markdown_title(doc_path)
        for document in documents:
            title_similarity = similarity_ratio(doc_title, document.metadata.get("title", ""))
            body_similarity = similarity_ratio(doc_text, document.body)
            if title_similarity >= threshold and body_similarity >= threshold:
                issues.append(
                    ValidationIssue(
                        relative_path(doc_path),
                        f"appears to duplicate canonical content in {document.relative_path}",
                    )
                )
    return issues


def validate_knowledge_documents(
    documents: list[KnowledgeDocument],
    object_schemas: dict[str, dict[str, Any]],
    legacy_schema: dict[str, Any],
    taxonomies: dict[str, dict[str, Any]],
    policy: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen_ids: dict[str, str] = {}
    known_ids = {document.knowledge_object_id for document in documents if document.knowledge_object_id}

    for document in documents:
        path = document.relative_path
        blueprint = None
        try:
            normalized = normalize_object_metadata(document)
            metadata = normalized.metadata
            schema = object_schemas[normalized.object_type]
            blueprint = get_blueprint(normalized.object_type)
        except Exception:
            metadata = document.metadata
            schema = legacy_schema
        fields = schema.get("fields", {})

        if not document.body:
            issues.append(ValidationIssue(path, "body content is empty"))

        for field_name, spec in fields.items():
            required = bool(spec.get("required"))
            if required and field_name not in metadata:
                issues.append(ValidationIssue(path, "missing required field", field_name))

        for field_name in metadata:
            if field_name not in fields:
                issues.append(ValidationIssue(path, "unknown field", field_name))

        object_id = metadata.get("id")
        if isinstance(object_id, str):
            previous_path = seen_ids.get(object_id)
            if previous_path:
                issues.append(
                    ValidationIssue(
                        path,
                        f"duplicate id already used by {previous_path}",
                        "id",
                    )
                )
            seen_ids[object_id] = path

        for field_name, spec in fields.items():
            if field_name not in metadata:
                continue
            value = metadata[field_name]
            issues.extend(validate_field(path, field_name, value, spec, taxonomies))

        created = metadata.get("created")
        updated = metadata.get("updated")
        last_reviewed = metadata.get("last_reviewed")
        if all(ensure_iso_date(item) for item in [created, updated, last_reviewed]):
            created_date = parse_iso_date(created)
            updated_date = parse_iso_date(updated)
            reviewed_date = parse_iso_date(last_reviewed)
            if updated_date < created_date:
                issues.append(ValidationIssue(path, "updated cannot be earlier than created", "updated"))
            if reviewed_date < created_date:
                issues.append(ValidationIssue(path, "last_reviewed cannot be earlier than created", "last_reviewed"))

        if metadata.get("canonical_path") != path:
            issues.append(ValidationIssue(path, "canonical_path must match the source file path", "canonical_path"))

        if path.startswith("archive/knowledge/") and metadata.get("status") != "archived":
            issues.append(ValidationIssue(path, "archived paths must use status 'archived'", "status"))

        if path.startswith("knowledge/") and metadata.get("status") == "archived":
            issues.append(ValidationIssue(path, "archived knowledge objects must live under archive/knowledge/", "status"))

        replaced_by = metadata.get("superseded_by") or metadata.get("replaced_by")
        retirement_reason = metadata.get("retirement_reason")
        status = metadata.get("status")
        if status == "deprecated" and not (replaced_by or retirement_reason):
            issues.append(
                ValidationIssue(
                    path,
                    "deprecated content must declare replaced_by or retirement_reason",
                    "status",
                )
            )
        if status == "archived" and not retirement_reason:
            issues.append(
                ValidationIssue(
                    path,
                    "archived content must declare retirement_reason",
                    "status",
                )
            )
        if replaced_by:
            if replaced_by == object_id:
                issues.append(ValidationIssue(path, "replaced_by cannot reference itself", "replaced_by"))
            elif replaced_by not in known_ids:
                issues.append(ValidationIssue(path, f"replacement knowledge object not found: {replaced_by}", "replaced_by"))

        related_object_ids = metadata.get("related_object_ids") or metadata.get("related_articles", [])
        for related in related_object_ids:
            if related not in known_ids:
                issues.append(
                    ValidationIssue(
                        path,
                        f"related knowledge object id not found: {related}",
                        "related_object_ids",
                    )
                )

        citations = metadata.get("citations") or []
        if not citations:
            citations = metadata.get("references", [])

        for citation in citations:
            article_ref = citation.get("article_id")
            if article_ref and article_ref not in known_ids:
                issues.append(
                    ValidationIssue(
                        path,
                        f"referenced knowledge object id not found: {article_ref}",
                        "citations",
                    )
                )
            reference_path = citation.get("path")
            if reference_path:
                repo_target = ROOT / reference_path
                if not repo_target.exists():
                    issues.append(
                        ValidationIssue(
                            path,
                            f"reference path does not exist: {reference_path}",
                            "citations",
                        )
                    )
            source_ref = citation.get("source_ref")
            if source_ref and str(source_ref).startswith(("knowledge/", "archive/knowledge/", "docs/", "decisions/", "migration/")):
                repo_target = ROOT / str(source_ref)
                if not repo_target.exists():
                    issues.append(
                        ValidationIssue(
                            path,
                            f"citation source_ref does not exist: {source_ref}",
                            "citations",
                        )
                    )
            evidence_snapshot_path = citation.get("evidence_snapshot_path")
            if evidence_snapshot_path:
                snapshot_target = ROOT / str(evidence_snapshot_path)
                if not snapshot_target.exists():
                    issues.append(
                        ValidationIssue(
                            path,
                            f"evidence snapshot path does not exist: {evidence_snapshot_path}",
                            "citations",
                        )
                    )
            evidence_expiry_at = citation.get("evidence_expiry_at")
            if evidence_expiry_at and parse_iso_date_or_datetime(evidence_expiry_at) < dt.date.today():
                issues.append(
                    ValidationIssue(
                        path,
                        f"evidence snapshot expired at {evidence_expiry_at}",
                        "citations",
                    )
                )

        if blueprint is not None:
            section_content = derive_section_content(
                blueprint_id=blueprint.blueprint_id,
                metadata=metadata,
                body_markdown=document.body,
            )
            allow_legacy_fallback = _uses_legacy_blueprint_fallback(
                metadata=metadata,
                section_content=section_content,
            )
            completion = compute_completion_state(
                blueprint=blueprint,
                section_content=section_content,
                taxonomies=taxonomies,
            )
            for section_id in blueprint.required_sections:
                section_progress = completion["section_completion_map"].get(section_id)
                if section_progress and section_progress["completed"]:
                    continue
                section = blueprint.section(section_id)
                if allow_legacy_fallback and _legacy_section_complete(
                    section=section,
                    section_values=section_content.get(section_id, {}),
                    metadata=metadata,
                    body_markdown=document.body,
                ):
                    continue
                issues.append(
                    ValidationIssue(
                        path,
                        f"required blueprint section is incomplete: {section.display_name}",
                        section_id,
                    )
                )

    duplicates = find_possible_duplicate_documents(
        documents,
        float(policy["duplicate_detection"]["title_similarity_threshold"]),
    )
    for duplicate in duplicates:
        issues.append(
            ValidationIssue(
                duplicate.left_path,
                (
                    f"title is highly similar to {duplicate.right_path} "
                    f"({duplicate.similarity:.2f}) without explicit linkage"
                ),
                "title",
            )
        )

    return issues


def validate_repository(include_rendered_site: bool = False) -> list[ValidationIssue]:
    policy = load_policy()
    object_schemas = load_object_schemas()
    legacy_schema = load_schema()
    taxonomies = load_taxonomies()
    documents = load_knowledge_documents(policy)
    issues: list[ValidationIssue] = []
    issues.extend(validate_directory_contract(policy))
    issues.extend(validate_knowledge_documents(documents, object_schemas, legacy_schema, taxonomies, policy))
    issues.extend(validate_docs_duplication(documents, policy))
    issues.extend(validate_generated_site_docs(documents))

    markdown_paths = (
        collect_root_markdown_paths()
        + collect_docs_source_paths()
        + collect_decision_paths()
        + collect_article_paths(policy)
    )
    for broken_link in collect_broken_markdown_links(markdown_paths):
        issues.append(
            ValidationIssue(
                broken_link.source_path,
                f"broken link '{broken_link.target}': {broken_link.reason}",
            )
        )

    if include_rendered_site:
        if not SITE_DIR.exists():
            issues.append(
                ValidationIssue(
                    relative_path(SITE_DIR),
                    "rendered site validation requested but site/ does not exist; run mkdocs build first",
                )
            )
        else:
            for broken_link in collect_broken_rendered_site_links():
                issues.append(
                    ValidationIssue(
                        broken_link.source_path,
                        f"broken rendered link '{broken_link.target}': {broken_link.reason}",
                    )
                )

    issues.extend(validate_sanitization(collect_sanitization_paths(policy)))
    return issues


def record_validation_run(
    *,
    database_path=DB_PATH,
    run_id: str,
    run_type: str,
    status: str,
    finding_count: int,
    details: dict[str, Any],
    actor: str,
    started_at: dt.datetime | None = None,
    completed_at: dt.datetime | None = None,
) -> str:
    actor = require_actor_id(actor)
    started = started_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    completed = completed_at or started
    connection = open_runtime_database(database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
    try:
        apply_runtime_schema(connection, has_fts5=fts5_available(connection))
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (RUNTIME_SCHEMA_VERSION, started.isoformat()),
        )
        insert_validation_run(
            connection,
            run_id=run_id,
            run_type=run_type,
            started_at=started.isoformat(),
            completed_at=completed.isoformat(),
            status=status,
            finding_count=finding_count,
            details_json=json_dump(details),
        )
        insert_audit_event(
            connection,
            event_id=f"validation-run-{run_id}",
            event_type="validation_run_recorded",
            occurred_at=completed.isoformat(),
            actor=actor,
            object_id=None,
            revision_id=None,
            details_json=json_dump({"run_id": run_id, "run_type": run_type, "status": status}),
        )
        connection.commit()
        return run_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def orphaned_files(policy: dict[str, Any], documents: list[KnowledgeDocument]) -> list[str]:
    findings: list[str] = []
    if LEGACY_GENERATED_DOCS_DIR.exists():
        for path in sorted(LEGACY_GENERATED_DOCS_DIR.rglob("*")):
            if path.is_file():
                findings.append(relative_path(path))

    for document in documents:
        if document.relative_path.startswith("archive/knowledge/") and document.metadata.get("status") != "archived":
            findings.append(document.relative_path)
        if document.relative_path.startswith("knowledge/") and document.metadata.get("status") == "archived":
            findings.append(document.relative_path)

    if GENERATED_SITE_DOCS_DIR.exists():
        try:
            expected = expected_site_doc_paths(documents)
        except ExportRuntimeUnavailableError:
            expected = set()
        actual = {
            relative_path(path)
            for path in GENERATED_SITE_DOCS_DIR.rglob("*")
            if path.is_file()
        }
        findings.extend(sorted(actual.difference(expected)))

    return sorted(set(findings))
