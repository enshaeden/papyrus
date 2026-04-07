#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import difflib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
ARCHIVE_KNOWLEDGE_DIR = ROOT / "archive" / "knowledge"
DOCS_DIR = ROOT / "docs"
DECISIONS_DIR = ROOT / "decisions"
TEMPLATE_DIR = ROOT / "templates"
GENERATED_DIR = ROOT / "generated"
GENERATED_SITE_DOCS_DIR = GENERATED_DIR / "site_docs"
LEGACY_GENERATED_DOCS_DIR = DOCS_DIR / "generated"
REPORTS_DIR = ROOT / "reports"
SCHEMA_PATH = ROOT / "schemas" / "article.yml"
POLICY_PATH = ROOT / "schemas" / "repository_policy.yml"
TAXONOMY_DIR = ROOT / "taxonomies"
BUILD_DIR = ROOT / "build"
SITE_DIR = ROOT / "site"
DB_PATH = BUILD_DIR / "knowledge.db"
SYSTEM_DESIGN_DOCS_SITE_ROOT = Path("system-design-docs")
GENERATED_SITE_INDEX_PATHS = (
    "index.md",
    "knowledge/index.md",
    "knowledge/start-here.md",
    "knowledge/support.md",
    "knowledge/authors.md",
    "knowledge/managers.md",
    "knowledge/explorer.md",
    "knowledge/tree.md",
    "knowledge/by-type.md",
    "knowledge/by-audience.md",
    "knowledge/by-service.md",
    "knowledge/by-system.md",
    "knowledge/by-tag.md",
    "knowledge/by-team.md",
    "knowledge/by-status.md",
    "knowledge/content-health.md",
    "knowledge/coverage-matrix.md",
    "archive/index.md",
)
FRONT_MATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKDOWN_LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
PLACEHOLDER_PATTERN = re.compile(r"^<[A-Z0-9_]+>$")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"\b(?:\+\d{1,3}[ -]?)?(?:\(\d{3}\)|\d{3})[ -]\d{3}[ -]\d{4}\b")
IP_PATTERN = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b")
ADDRESS_PATTERN = re.compile(
    r"\b\d{1,5}\s+[A-Za-z0-9][A-Za-z0-9 .'-]{1,40}\s"
    r"(?:Street|St|Road|Rd|Avenue|Ave|Boulevard|Blvd|Lane|Ln|Drive|Dr|Way|Court|Ct|Place|Pl)\b",
    re.IGNORECASE,
)
DOMAIN_PATTERN = re.compile(
    r"\b[a-z0-9-]+(?:\.[a-z0-9-]+)+\.(?:com|net|org|io|local|internal|corp|lan|private)\b",
    re.IGNORECASE,
)
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]+PRIVATE KEY-----"),
    re.compile(
        r"(?i)\b(?:api[_ -]?key|token|client[_ -]?secret|password|passphrase|recovery[_ -]?code)\b"
        r"[^\n]{0,20}[:=][ \t]*['\"]?[A-Za-z0-9/_+=.-]{8,}"
    ),
]
BRANDED_ADMIN_PATTERNS = [
    re.compile(r"\badmin console\b", re.IGNORECASE),
    re.compile(r"\badmin center\b", re.IGNORECASE),
]
LIKELY_BRANDED_PRODUCT_PATTERN = re.compile(
    r"\b(?:[A-Z][a-z0-9]+(?:[ -][A-Z][a-z0-9]+){0,2})\s"
    r"(?:Platform|Suite|Portal|Cloud|Workspace|Center|Console|Directory)\b"
)
OPERATIONAL_HEADING_PATTERN = re.compile(
    r"^#{1,6}\s+(Prerequisites|Steps|Verification|Rollback)\b",
    re.IGNORECASE | re.MULTILINE,
)
DOCS_OPERATOR_LANGUAGE_PATTERNS = (
    ("standard operating procedure", re.compile(r"\b(?:standard operating procedure|SOP)\b", re.IGNORECASE)),
    ("runbook", re.compile(r"\brunbook\b", re.IGNORECASE)),
    ("troubleshooting", re.compile(r"\btroubleshooting\b", re.IGNORECASE)),
    (
        "service desk or operator language",
        re.compile(r"\b(?:service desk|help ?desk|on-call|operator)\b", re.IGNORECASE),
    ),
    (
        "procedural phrasing",
        re.compile(
            r"\b(?:before you begin|follow these steps|perform the following steps|to verify|"
            r"verification steps|rollback steps|escalate to)\b",
            re.IGNORECASE,
        ),
    ),
)
GENERIC_BRAND_ALLOWLIST = {
    "Asset",
    "Business",
    "Cloud",
    "Collaboration",
    "Conferencing",
    "Content",
    "Creative",
    "Developer",
    "Desk",
    "Disconnect",
    "Device",
    "Digital",
    "Directory",
    "Documentation",
    "Endpoint",
    "Enabled",
    "Enrollment",
    "HR",
    "Helpdesk",
    "Identity",
    "Instant",
    "Internal",
    "Knowledge",
    "License",
    "Management",
    "Messaging",
    "Multi-Factor",
    "Migration",
    "New",
    "Password",
    "Printer",
    "Productivity",
    "Remote",
    "Reporting",
    "Seed",
    "Self",
    "Service",
    "Shipping",
    "Support",
    "Ticketing",
    "Video",
    "Workflow",
    "Workspace",
    "Application",
    "Admin",
    "And",
    "VPN",
    "Workplace",
    "Label",
    "Network",
    "Software",
}


@dataclass
class Article:
    source_path: Path
    relative_path: str
    metadata: dict[str, Any]
    body: str

    @property
    def article_id(self) -> str:
        return str(self.metadata.get("id", ""))


@dataclass
class ValidationIssue:
    path: str
    message: str
    field: str | None = None

    def render(self) -> str:
        if self.field:
            return f"{self.path}: {self.field}: {self.message}"
        return f"{self.path}: {self.message}"


@dataclass
class BrokenLink:
    source_path: str
    target: str
    reason: str


@dataclass
class DuplicateCandidate:
    left_path: str
    right_path: str
    left_title: str
    right_title: str
    similarity: float


@dataclass
class DocsPlacementWarning:
    path: str
    score: int
    signals: list[str]


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping")
    return data


def load_schema(schema_path: Path = SCHEMA_PATH) -> dict[str, Any]:
    return load_yaml_file(schema_path)


def load_policy(policy_path: Path = POLICY_PATH) -> dict[str, Any]:
    return load_yaml_file(policy_path)


def load_taxonomies(taxonomy_dir: Path = TAXONOMY_DIR) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for path in sorted(taxonomy_dir.glob("*.yml")):
        data = load_yaml_file(path)
        values = data.get("values", [])
        allowed = []
        for entry in values:
            if isinstance(entry, dict) and "name" in entry:
                allowed.append(entry["name"])
            elif isinstance(entry, str):
                allowed.append(entry)
            else:
                raise ValueError(f"{path} contains an invalid taxonomy entry: {entry!r}")
        data["allowed_values"] = allowed
        results[path.stem] = data
    return results


def relative_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_article(path: Path) -> Article:
    text = path.read_text(encoding="utf-8")
    match = FRONT_MATTER_PATTERN.match(text)
    if not match:
        raise ValueError(f"{relative_path(path)}: missing YAML front matter")
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{relative_path(path)}: front matter must be a YAML mapping")
    body = match.group(2).strip()
    return Article(
        source_path=path,
        relative_path=relative_path(path),
        metadata=metadata,
        body=body,
    )


def article_roots(policy: dict[str, Any] | None = None) -> list[Path]:
    current_policy = policy or load_policy()
    return [ROOT / item for item in current_policy["directories"]["canonical_article_roots"]]


def collect_article_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    for root in article_roots(policy):
        if root.exists():
            paths.extend(sorted(path for path in root.rglob("*.md") if path.is_file()))
    return sorted(paths)


def load_articles(policy: dict[str, Any] | None = None) -> list[Article]:
    return [parse_article(path) for path in collect_article_paths(policy)]


def collect_docs_source_paths() -> list[Path]:
    if not DOCS_DIR.exists():
        return []
    paths = []
    for path in sorted(DOCS_DIR.rglob("*")):
        if not path.is_file():
            continue
        try:
            relative = path.relative_to(DOCS_DIR)
        except ValueError:
            continue
        if relative.parts and relative.parts[0] == "generated":
            continue
        paths.append(path)
    return paths


def site_relative_path_for_repo_path(repo_relative: str) -> Path | None:
    candidate = Path(repo_relative)
    if repo_relative.startswith("knowledge/"):
        return candidate
    if repo_relative.startswith("archive/knowledge/"):
        return candidate
    if repo_relative.startswith("docs/"):
        return SYSTEM_DESIGN_DOCS_SITE_ROOT / candidate.relative_to("docs")
    if repo_relative.startswith("decisions/"):
        return candidate
    return None


def collect_decision_paths() -> list[Path]:
    if not DECISIONS_DIR.exists():
        return []
    return sorted(path for path in DECISIONS_DIR.rglob("*") if path.is_file())


def collect_root_markdown_paths() -> list[Path]:
    candidates = [ROOT / "README.md", ROOT / "AGENTS.md"]
    return [path for path in candidates if path.exists()]


def collect_sanitization_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    scan_roots = [
        *article_roots(policy),
        DOCS_DIR,
        DECISIONS_DIR,
        GENERATED_SITE_DOCS_DIR,
        ROOT / "migration",
        TEMPLATE_DIR,
        TAXONOMY_DIR,
        REPORTS_DIR,
    ]
    for root in scan_roots:
        if not root.exists():
            continue
        paths.extend(
            path
            for path in sorted(root.rglob("*"))
            if path.is_file() and path.suffix in {".md", ".yml", ".yaml"}
        )
    paths.extend(collect_root_markdown_paths())
    return sorted(set(paths))


def normalize_whitespace(value: str) -> str:
    return " ".join(value.split())


def normalize_for_similarity(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return normalize_whitespace(normalized)


def similarity_ratio(left: str, right: str) -> float:
    return difflib.SequenceMatcher(None, normalize_for_similarity(left), normalize_for_similarity(right)).ratio()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def ensure_iso_date(value: Any) -> bool:
    if isinstance(value, dt.datetime):
        return False
    if isinstance(value, dt.date):
        return True
    if not isinstance(value, str):
        return False
    if not DATE_PATTERN.match(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def parse_iso_date(value: Any) -> dt.date:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(value)


def date_to_iso(value: Any) -> str:
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    return str(value)


def json_dump(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=True, default=date_to_iso)


def render_list(items: list[str]) -> str:
    if not items:
        return "- None documented.\n"
    return "".join(f"- {item}\n" for item in items)


def render_reference(reference: dict[str, Any]) -> str:
    parts = [reference["title"]]
    if reference.get("article_id"):
        parts.append(f"article_id: {reference['article_id']}")
    if reference.get("path"):
        parts.append(f"path: `{reference['path']}`")
    if reference.get("url"):
        parts.append(f"url: {reference['url']}")
    if reference.get("note"):
        parts.append(f"note: {reference['note']}")
    return " | ".join(parts)


def render_change_log(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "- None documented.\n"
    return "".join(
        f"- {date_to_iso(entry['date'])} | {entry['author']} | {entry['summary']}\n"
        for entry in entries
    )


def summarize_for_search(article: Article) -> str:
    metadata = article.metadata
    values: list[str] = [
        metadata.get("title", ""),
        metadata.get("summary", ""),
        metadata.get("type", ""),
        metadata.get("status", ""),
        metadata.get("owner", ""),
        metadata.get("team", ""),
        metadata.get("source_type", ""),
        " ".join(metadata.get("systems", [])),
        " ".join(metadata.get("services", [])),
        " ".join(metadata.get("tags", [])),
        article.body,
    ]
    return normalize_whitespace(" ".join(str(value) for value in values if value))


def cadence_to_days(cadence: str, taxonomies: dict[str, dict[str, Any]]) -> int | None:
    for entry in taxonomies["review_cadences"].get("values", []):
        if isinstance(entry, dict) and entry.get("name") == cadence:
            return entry.get("interval_days")
    return None


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


def explicitly_linked(left: Article, right: Article) -> bool:
    left_related = set(left.metadata.get("related_articles", []))
    right_related = set(right.metadata.get("related_articles", []))
    replacements = {
        left.metadata.get("replaced_by"),
        right.metadata.get("replaced_by"),
    }
    return (
        right.article_id in left_related
        or left.article_id in right_related
        or left.article_id in replacements
        or right.article_id in replacements
    )


def find_possible_duplicate_articles(
    articles: list[Article],
    threshold: float,
) -> list[DuplicateCandidate]:
    duplicates: list[DuplicateCandidate] = []
    for index, left in enumerate(articles):
        for right in articles[index + 1 :]:
            if explicitly_linked(left, right):
                continue
            similarity = similarity_ratio(left.metadata.get("title", ""), right.metadata.get("title", ""))
            if similarity >= threshold:
                duplicates.append(
                    DuplicateCandidate(
                        left_path=left.relative_path,
                        right_path=right.relative_path,
                        left_title=left.metadata.get("title", ""),
                        right_title=right.metadata.get("title", ""),
                        similarity=similarity,
                    )
                )
    return duplicates


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


def is_external_target(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("app://")
        or lowered.startswith("plugin://")
        or bool(PLACEHOLDER_PATTERN.fullmatch(target.strip()))
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


def validate_sanitization(paths: Iterable[Path]) -> list[ValidationIssue]:
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


def reference_graph(articles: list[Article]) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for article in articles:
        links = set(article.metadata.get("related_articles", []))
        replaced_by = article.metadata.get("replaced_by")
        if replaced_by:
            links.add(replaced_by)
        for reference in article.metadata.get("references", []):
            article_id = reference.get("article_id")
            if article_id:
                links.add(article_id)
        graph[article.article_id] = links
    return graph


def inverse_reference_graph(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    inverse: dict[str, set[str]] = {key: set() for key in graph}
    for source, targets in graph.items():
        for target in targets:
            inverse.setdefault(target, set()).add(source)
    return inverse


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


def expected_site_doc_paths(articles: list[Article]) -> set[str]:
    expected: set[str] = set()

    for path in collect_docs_source_paths():
        site_relative = site_relative_path_for_repo_path(relative_path(path))
        if site_relative is not None:
            expected.add(relative_path(GENERATED_SITE_DOCS_DIR / site_relative))
    for path in collect_decision_paths():
        site_relative = site_relative_path_for_repo_path(relative_path(path))
        if site_relative is not None:
            expected.add(relative_path(GENERATED_SITE_DOCS_DIR / site_relative))

    expected.update(relative_path(GENERATED_SITE_DOCS_DIR / path) for path in GENERATED_SITE_INDEX_PATHS)

    for article in articles:
        if article.metadata.get("status") == "archived":
            expected.add(relative_path(GENERATED_SITE_DOCS_DIR / article.source_path.relative_to(ROOT)))
        else:
            expected.add(
                relative_path(
                    GENERATED_SITE_DOCS_DIR / "knowledge" / article.source_path.relative_to(KNOWLEDGE_DIR)
                )
            )

    return expected


def validate_generated_site_docs(articles: list[Article]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not GENERATED_SITE_DOCS_DIR.exists():
        return issues
    expected = expected_site_doc_paths(articles)
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
    articles: list[Article],
    policy: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    threshold = float(policy["duplicate_detection"]["doc_duplication_threshold"])
    for doc_path in collect_docs_source_paths():
        if doc_path.suffix != ".md":
            continue
        doc_text = doc_path.read_text(encoding="utf-8")
        doc_title = extract_markdown_title(doc_path)
        for article in articles:
            title_similarity = similarity_ratio(doc_title, article.metadata.get("title", ""))
            body_similarity = similarity_ratio(doc_text, article.body)
            if title_similarity >= threshold and body_similarity >= threshold:
                issues.append(
                    ValidationIssue(
                        relative_path(doc_path),
                        f"appears to duplicate canonical content in {article.relative_path}",
                    )
                )
    return issues


def validate_articles(
    articles: list[Article],
    schema: dict[str, Any],
    taxonomies: dict[str, dict[str, Any]],
    policy: dict[str, Any],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    fields = schema.get("fields", {})
    seen_ids: dict[str, str] = {}
    known_ids = {article.article_id for article in articles if article.article_id}

    for article in articles:
        metadata = article.metadata
        path = article.relative_path

        if not article.body:
            issues.append(ValidationIssue(path, "body content is empty"))

        for field_name, spec in fields.items():
            required = bool(spec.get("required"))
            if required and field_name not in metadata:
                issues.append(ValidationIssue(path, "missing required field", field_name))

        for field_name in metadata:
            if field_name not in fields:
                issues.append(ValidationIssue(path, "unknown field", field_name))

        article_id = metadata.get("id")
        if isinstance(article_id, str):
            previous_path = seen_ids.get(article_id)
            if previous_path:
                issues.append(
                    ValidationIssue(
                        path,
                        f"duplicate id already used by {previous_path}",
                        "id",
                    )
                )
            seen_ids[article_id] = path

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
                issues.append(
                    ValidationIssue(path, "last_reviewed cannot be earlier than created", "last_reviewed")
                )

        if metadata.get("canonical_path") != path:
            issues.append(ValidationIssue(path, "canonical_path must match the article path", "canonical_path"))

        if path.startswith("archive/knowledge/") and metadata.get("status") != "archived":
            issues.append(ValidationIssue(path, "archived paths must use status 'archived'", "status"))

        if path.startswith("knowledge/") and metadata.get("status") == "archived":
            issues.append(ValidationIssue(path, "archived articles must live under archive/knowledge/", "status"))

        replaced_by = metadata.get("replaced_by")
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
            if replaced_by == article_id:
                issues.append(ValidationIssue(path, "replaced_by cannot reference itself", "replaced_by"))
            elif replaced_by not in known_ids:
                issues.append(ValidationIssue(path, f"replacement article not found: {replaced_by}", "replaced_by"))

        for related in metadata.get("related_articles", []):
            if related not in known_ids:
                issues.append(
                    ValidationIssue(
                        path,
                        f"related article id not found: {related}",
                        "related_articles",
                    )
                )

        for reference in metadata.get("references", []):
            article_ref = reference.get("article_id")
            if article_ref and article_ref not in known_ids:
                issues.append(
                    ValidationIssue(
                        path,
                        f"reference article id not found: {article_ref}",
                        "references",
                    )
                )
            reference_path = reference.get("path")
            if reference_path:
                repo_target = ROOT / reference_path
                if not repo_target.exists():
                    issues.append(
                        ValidationIssue(
                            path,
                            f"reference path does not exist: {reference_path}",
                            "references",
                        )
                    )

    duplicates = find_possible_duplicate_articles(
        articles,
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


def validate_repository() -> list[ValidationIssue]:
    policy = load_policy()
    schema = load_schema()
    taxonomies = load_taxonomies()
    articles = load_articles(policy)
    issues = []
    issues.extend(validate_directory_contract(policy))
    issues.extend(validate_articles(articles, schema, taxonomies, policy))
    issues.extend(validate_docs_duplication(articles, policy))
    issues.extend(validate_generated_site_docs(articles))

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

    issues.extend(validate_sanitization(collect_sanitization_paths(policy)))

    return issues


def docs_knowledge_like_warnings(
    schema: dict[str, Any] | None = None,
) -> list[DocsPlacementWarning]:
    article_fields = set((schema or load_schema()).get("fields", {}))
    warnings: list[DocsPlacementWarning] = []

    for path in collect_docs_source_paths():
        if path.suffix != ".md":
            continue

        text = path.read_text(encoding="utf-8")
        body = text
        signals: list[str] = []
        score = 0
        has_front_matter_signal = False

        match = FRONT_MATTER_PATTERN.match(text)
        if match:
            metadata = yaml.safe_load(match.group(1)) or {}
            body = match.group(2)
            if isinstance(metadata, dict):
                overlapping_fields = sorted(set(metadata).intersection(article_fields))
                strong_fields = [
                    field
                    for field in overlapping_fields
                    if field in {"canonical_path", "last_reviewed", "prerequisites", "review_cadence", "rollback", "source_type", "steps", "verification"}
                ]
                if strong_fields or len(overlapping_fields) >= 5:
                    has_front_matter_signal = True
                    preview_fields = strong_fields or overlapping_fields[:6]
                    preview = ", ".join(preview_fields)
                    if len(overlapping_fields) > len(preview_fields):
                        preview += ", ..."
                    signals.append(f"front matter overlaps article schema: {preview}")
                    score += 5 + len(strong_fields)

        heading_hits = sorted({match.group(1).title() for match in OPERATIONAL_HEADING_PATTERN.finditer(body)})
        if heading_hits:
            signals.append("operational headings: " + ", ".join(heading_hits))
            score += len(heading_hits) * 2

        phrase_hits = [
            label for label, pattern in DOCS_OPERATOR_LANGUAGE_PATTERNS if pattern.search(body)
        ]
        if phrase_hits:
            signals.append("operator-oriented language: " + ", ".join(phrase_hits))
            score += len(phrase_hits)

        has_procedural_language_signal = "procedural phrasing" in phrase_hits
        should_warn = (
            has_front_matter_signal
            or len(heading_hits) >= 2
            or (len(heading_hits) >= 1 and len(phrase_hits) >= 1)
            or (has_procedural_language_signal and len(phrase_hits) >= 2)
        )
        if should_warn:
            warnings.append(DocsPlacementWarning(relative_path(path), score, signals))

    return sorted(warnings, key=lambda item: (-item.score, item.path))


def relationless_articles(articles: list[Article]) -> list[Article]:
    graph = reference_graph(articles)
    inverse = inverse_reference_graph(graph)
    isolated = []
    for article in articles:
        outbound = graph.get(article.article_id, set())
        inbound = inverse.get(article.article_id, set())
        if not outbound and not inbound:
            isolated.append(article)
    return isolated


def missing_owner_articles(articles: list[Article]) -> list[Article]:
    return [article for article in articles if not str(article.metadata.get("owner", "")).strip()]


def stale_articles(
    articles: list[Article],
    taxonomies: dict[str, dict[str, Any]],
    as_of: dt.date,
    allowed_statuses: set[str] | None = None,
) -> list[tuple[int, Article, dt.date]]:
    stale_rows = []
    for article in articles:
        status = article.metadata.get("status")
        if allowed_statuses and status not in allowed_statuses:
            continue
        cadence_days = cadence_to_days(article.metadata["review_cadence"], taxonomies)
        if cadence_days is None:
            continue
        review_date = parse_iso_date(article.metadata["last_reviewed"])
        due_date = review_date + dt.timedelta(days=cadence_days)
        if due_date < as_of:
            stale_rows.append(((as_of - due_date).days, article, due_date))
    return sorted(stale_rows, key=lambda row: (row[0], row[1].metadata["title"]), reverse=True)


def orphaned_files(policy: dict[str, Any], articles: list[Article]) -> list[str]:
    findings: list[str] = []
    if LEGACY_GENERATED_DOCS_DIR.exists():
        for path in sorted(LEGACY_GENERATED_DOCS_DIR.rglob("*")):
            if path.is_file():
                findings.append(relative_path(path))

    graph = reference_graph(articles)
    inverse = inverse_reference_graph(graph)
    for article in articles:
        if article.relative_path.startswith("archive/knowledge/") and article.metadata.get("status") != "archived":
            findings.append(article.relative_path)
        if article.relative_path.startswith("knowledge/") and article.metadata.get("status") == "archived":
            findings.append(article.relative_path)

    if GENERATED_SITE_DOCS_DIR.exists():
        expected = expected_site_doc_paths(articles)
        actual = {
            relative_path(path)
            for path in GENERATED_SITE_DOCS_DIR.rglob("*")
            if path.is_file()
        }
        findings.extend(sorted(actual.difference(expected)))

    return sorted(set(findings))


def articles_missing_list_field(articles: list[Article], field_name: str) -> list[Article]:
    return [article for article in articles if not article.metadata.get(field_name)]


def searchable_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["searchable_statuses_default"])


def navigation_statuses(policy: dict[str, Any]) -> list[str]:
    return list(policy["lifecycle"]["active_navigation_statuses"])


def status_rank_map(policy: dict[str, Any]) -> dict[str, int]:
    order = policy["lifecycle"]["searchable_status_order"]
    return {status: index for index, status in enumerate(order)}


def site_article_output_path(article: Article) -> Path:
    if article.metadata.get("status") == "archived":
        return GENERATED_SITE_DOCS_DIR / article.source_path.relative_to(ROOT)
    return GENERATED_SITE_DOCS_DIR / "knowledge" / article.source_path.relative_to(KNOWLEDGE_DIR)


def fts5_available(connection: sqlite3.Connection) -> bool:
    try:
        connection.execute("CREATE VIRTUAL TABLE temp.fts_probe USING fts5(content)")
        connection.execute("DROP TABLE temp.fts_probe")
    except sqlite3.OperationalError:
        return False
    return True
