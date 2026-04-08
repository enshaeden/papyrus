from __future__ import annotations

import datetime as dt
import hashlib
from pathlib import Path
from typing import Iterable

import yaml

from papyrus.domain.entities import BrokenLink, KnowledgeDocument, ParsedKnowledgeObjectSource
from papyrus.domain.policies import (
    approval_state_for_status,
    citation_health_rank_for_statuses,
    normalize_citation_validity_status,
    ownership_rank,
    primary_object_type,
    trust_state,
    freshness_rank,
)
from papyrus.infrastructure.paths import (
    FRONT_MATTER_PATTERN,
    HTML_HREF_PATTERN,
    MARKDOWN_LINK_PATTERN,
    PLACEHOLDER_PATTERN,
    BARE_PLACEHOLDER_PATTERN,
    ROOT,
    SITE_DIR,
    relative_path,
)
from papyrus.infrastructure.markdown.serializer import normalize_whitespace, parse_iso_date


LEGACY_FIELD_NOTE_PREFIX = "Legacy source does not declare structured"


def parse_knowledge_document(path: Path) -> KnowledgeDocument:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        raise ValueError(f"{relative_path(path)}: missing YAML front matter")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{relative_path(path)}: front matter must be a YAML mapping")
    body = match.group(2).strip()
    return KnowledgeDocument(
        source_path=path,
        relative_path=relative_path(path),
        metadata=metadata,
        body=body,
    )


def extract_markdown_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".md":
        match = FRONT_MATTER_PATTERN.match(text)
        if match:
            metadata = yaml.safe_load(match.group(1)) or {}
            if isinstance(metadata, dict) and isinstance(metadata.get("title"), str):
                return metadata["title"]
            text = match.group(2)
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").strip()


def is_placeholder_target(target: str) -> bool:
    normalized = target.strip()
    if not normalized:
        return False
    if PLACEHOLDER_PATTERN.fullmatch(normalized):
        return True
    if normalized.startswith("<") and normalized.endswith(">"):
        normalized = normalized[1:-1].strip()
    return bool(BARE_PLACEHOLDER_PATTERN.fullmatch(normalized))


def is_external_target(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("tel:")
        or lowered.startswith("javascript:")
        or lowered.startswith("//")
        or lowered.startswith("app://")
        or lowered.startswith("plugin://")
        or is_placeholder_target(target)
    )


def resolve_local_link(base_path: Path, target: str) -> Path | None:
    clean_target = target.split("#", 1)[0].strip()
    if not clean_target or is_external_target(clean_target):
        return None
    if clean_target.startswith("/"):
        return (ROOT / clean_target.lstrip("/")).resolve()
    return (base_path.parent / clean_target).resolve()


def collect_broken_markdown_links(paths: Iterable[Path]) -> list[BrokenLink]:
    issues: list[BrokenLink] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for _, target in MARKDOWN_LINK_PATTERN.findall(text):
            resolved = resolve_local_link(path, target)
            if resolved is None:
                continue
            if not resolved.exists():
                issues.append(
                    BrokenLink(
                        source_path=relative_path(path),
                        target=target,
                        reason="target does not exist",
                    )
                )
    return issues


def resolve_rendered_site_link(base_path: Path, target: str, site_root: Path) -> tuple[Path | None, str | None]:
    clean_target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if not clean_target or is_external_target(clean_target):
        return None, None

    if clean_target.startswith("/"):
        resolved = (site_root / clean_target.lstrip("/")).resolve()
    else:
        resolved = (base_path.parent / clean_target).resolve()

    try:
        resolved.relative_to(site_root)
    except ValueError:
        return None, "target escapes site root"
    return resolved, None


def collect_broken_rendered_site_links(site_dir: Path = SITE_DIR) -> list[BrokenLink]:
    if not site_dir.exists():
        return []

    issues: list[BrokenLink] = []
    site_root = site_dir.resolve()
    html_paths = sorted(path for path in site_dir.rglob("*.html") if path.is_file())

    for path in html_paths:
        text = path.read_text(encoding="utf-8")
        for target in HTML_HREF_PATTERN.findall(text):
            resolved, resolution_issue = resolve_rendered_site_link(path.resolve(), target, site_root)
            if resolution_issue:
                issues.append(
                    BrokenLink(
                        source_path=relative_path(path),
                        target=target,
                        reason=resolution_issue,
                    )
                )
                continue
            if resolved is None:
                continue
            if not resolved.exists():
                issues.append(
                    BrokenLink(
                        source_path=relative_path(path),
                        target=target,
                        reason="target does not exist in rendered site",
                    )
                )
    return issues


def extract_first_paragraph(body: str) -> str:
    for block in body.split("\n\n"):
        stripped = normalize_whitespace(block.replace("\n", " ").strip())
        if stripped and not stripped.startswith("#"):
            return stripped
    return ""


def _string_list(values: object) -> list[str]:
    if not isinstance(values, list):
        return []
    return [str(item).strip() for item in values if str(item).strip()]


def _normalize_citations(metadata: dict[str, object]) -> list[dict[str, object]]:
    existing = metadata.get("citations")
    if isinstance(existing, list) and existing:
        citations: list[dict[str, object]] = []
        for item in existing:
            if not isinstance(item, dict):
                continue
            source_ref = str(item.get("source_ref") or item.get("path") or item.get("url") or "").strip()
            source_title = str(item.get("source_title") or item.get("title") or source_ref).strip()
            if not source_ref or not source_title:
                continue
            citations.append(
                {
                    "article_id": item.get("article_id"),
                    "claim_anchor": str(item.get("claim_anchor")).strip() if item.get("claim_anchor") else None,
                    "source_title": source_title,
                    "source_type": str(item.get("source_type") or "document").strip() or "document",
                    "source_ref": source_ref,
                    "note": str(item.get("note")).strip() if item.get("note") else None,
                    "excerpt": str(item.get("excerpt")).strip() if item.get("excerpt") else None,
                    "captured_at": str(item.get("captured_at")).strip() if item.get("captured_at") else None,
                    "validity_status": normalize_citation_validity_status(
                        str(item.get("validity_status")) if item.get("validity_status") is not None else None
                    ),
                    "integrity_hash": str(item.get("integrity_hash")).strip() if item.get("integrity_hash") else None,
                }
            )
        return citations

    legacy = metadata.get("references")
    if not isinstance(legacy, list):
        return []

    citations: list[dict[str, object]] = []
    for item in legacy:
        if not isinstance(item, dict):
            continue
        source_ref = str(item.get("path") or item.get("url") or item.get("article_id") or item.get("title") or "").strip()
        if not source_ref:
            continue
        source_title = str(item.get("title") or source_ref).strip()
        note = str(item.get("note") or "").strip() or None
        citations.append(
            {
                "article_id": item.get("article_id"),
                "claim_anchor": None,
                "source_title": source_title,
                "source_type": "document",
                "source_ref": source_ref,
                "note": note,
                "excerpt": None,
                "captured_at": None,
                "validity_status": "verified" if source_ref else "unverified",
                "integrity_hash": None,
            }
        )
    return citations


def _legacy_note(field: str, context: str | None = None) -> str:
    suffix = f" {context}" if context else ""
    return f"{LEGACY_FIELD_NOTE_PREFIX} {field}.{suffix}".strip()


def _legacy_scope_note(summary: object) -> str:
    summary_text = normalize_whitespace(str(summary or "").strip())
    if summary_text:
        return _legacy_note("scope", f"Summary: {summary_text}")
    return _legacy_note("scope")


def _related_services(metadata: dict[str, object]) -> list[str]:
    values = metadata.get("related_services")
    if isinstance(values, list):
        return _string_list(values)
    return _string_list(metadata.get("services"))


def _related_object_ids(metadata: dict[str, object]) -> list[str]:
    values = metadata.get("related_object_ids")
    if isinstance(values, list):
        return _string_list(values)
    return _string_list(metadata.get("related_articles"))


def _service_name(metadata: dict[str, object]) -> str:
    explicit = metadata.get("service_name")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    related_services = _related_services(metadata)
    if len(related_services) == 1:
        return related_services[0]
    return str(metadata.get("title") or "").strip()


def normalize_object_metadata(
    document: KnowledgeDocument,
    *,
    review_cadence_days: int | None = None,
    as_of: dt.date | None = None,
) -> ParsedKnowledgeObjectSource:
    metadata = dict(document.metadata)
    object_type = primary_object_type(metadata)
    if object_type is None:
        raise ValueError(f"{document.relative_path}: unsupported or missing knowledge object type")

    legacy_type_value = metadata.get("legacy_article_type")
    if not isinstance(legacy_type_value, str) or not legacy_type_value.strip():
        legacy_type_candidate = metadata.get("type")
        legacy_type_value = str(legacy_type_candidate).strip() if legacy_type_candidate else None

    paragraph = extract_first_paragraph(document.body)
    citations = _normalize_citations(metadata)
    related_services = _related_services(metadata)
    related_object_ids = _related_object_ids(metadata)
    status = str(metadata.get("status") or "")
    owner = str(metadata.get("owner") or "")
    review_date = parse_iso_date(metadata.get("last_reviewed"))
    now = as_of or dt.date.today()

    if object_type == "runbook":
        metadata.setdefault("related_services", related_services)
        metadata.setdefault("citations", citations)
        metadata.setdefault("related_object_ids", related_object_ids)
        metadata.setdefault("superseded_by", metadata.get("replaced_by"))
        metadata.setdefault("replaced_by", metadata.get("superseded_by"))
    elif object_type == "known_error":
        metadata.setdefault("related_services", related_services)
        metadata.setdefault("citations", citations)
        metadata.setdefault("related_object_ids", related_object_ids)
        metadata.setdefault("symptoms", [str(metadata.get("summary") or "").strip()])
        metadata.setdefault(
            "scope",
            _legacy_scope_note(metadata.get("summary")),
        )
        metadata.setdefault("cause", _legacy_note("cause"))
        metadata.setdefault("diagnostic_checks", _string_list(metadata.get("steps")))
        metadata.setdefault(
            "mitigations",
            _string_list(metadata.get("rollback")) or [_legacy_note("mitigations")],
        )
        metadata.setdefault("permanent_fix_status", "unknown")
        metadata.setdefault("superseded_by", metadata.get("replaced_by"))
        metadata.setdefault("replaced_by", metadata.get("superseded_by"))
    elif object_type == "service_record":
        metadata.setdefault("service_name", _service_name(metadata))
        metadata.setdefault("service_criticality", "not_classified")
        metadata.setdefault("dependencies", _string_list(metadata.get("systems")))
        metadata.setdefault(
            "support_entrypoints",
            _string_list(metadata.get("support_entrypoints"))
            or [_legacy_note("support entrypoints")],
        )
        metadata.setdefault(
            "common_failure_modes",
            _string_list(metadata.get("common_failure_modes"))
            or [_legacy_note("common failure modes")],
        )
        metadata.setdefault("related_runbooks", [])
        metadata.setdefault("related_known_errors", [])
        metadata.setdefault("citations", citations)
        metadata.setdefault("related_object_ids", related_object_ids)
        metadata.setdefault("superseded_by", metadata.get("replaced_by"))
        metadata.setdefault("replaced_by", metadata.get("superseded_by"))
    else:  # pragma: no cover
        raise ValueError(f"{document.relative_path}: unsupported knowledge object type {object_type}")

    citation_rank = citation_health_rank_for_statuses(
        [str(citation.get("validity_status", "unverified")) for citation in citations]
    )
    owner_rank_value = ownership_rank(owner)
    fresh_rank = freshness_rank(status, review_date, review_cadence_days, now)

    return ParsedKnowledgeObjectSource(
        document=document,
        object_type=object_type,
        legacy_type=legacy_type_value,
        metadata=metadata,
        citations=citations,
        related_services=related_services,
        related_object_ids=related_object_ids,
        trust_state=trust_state(
            status=status,
            freshness_rank_value=fresh_rank,
            citation_health_rank_value=citation_rank,
            ownership_rank_value=owner_rank_value,
        ),
        approval_state=approval_state_for_status(status),
        freshness_rank=fresh_rank,
        citation_health_rank=citation_rank,
        ownership_rank=owner_rank_value,
    )
