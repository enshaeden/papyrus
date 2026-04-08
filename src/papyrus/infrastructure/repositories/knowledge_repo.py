from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from papyrus.domain.entities import KnowledgeDocument
from papyrus.infrastructure.markdown.parser import parse_knowledge_document
from papyrus.infrastructure.paths import (
    ARTICLE_SCHEMA_PATH,
    DECISIONS_DIR,
    DOCS_DIR,
    GENERATED_SITE_DOCS_DIR,
    POLICY_PATH,
    REPORTS_DIR,
    ROOT,
    TAXONOMY_DIR,
    TEMPLATE_DIR,
)


def load_yaml_file(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a YAML mapping")
    return data


def load_schema(schema_path: Path = ARTICLE_SCHEMA_PATH) -> dict[str, Any]:
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


def knowledge_source_roots(policy: dict[str, Any] | None = None) -> list[Path]:
    current_policy = policy or load_policy()
    return [ROOT / item for item in current_policy["directories"]["canonical_article_roots"]]


def collect_source_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    paths: list[Path] = []
    for root in knowledge_source_roots(policy):
        if root.exists():
            paths.extend(sorted(path for path in root.rglob("*.md") if path.is_file()))
    return sorted(paths)


def load_knowledge_documents(policy: dict[str, Any] | None = None) -> list[KnowledgeDocument]:
    return [parse_knowledge_document(path) for path in collect_source_paths(policy)]


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
        *knowledge_source_roots(policy),
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


def collect_article_paths(policy: dict[str, Any] | None = None) -> list[Path]:
    return collect_source_paths(policy)


def load_articles(policy: dict[str, Any] | None = None) -> list[KnowledgeDocument]:
    return load_knowledge_documents(policy)

