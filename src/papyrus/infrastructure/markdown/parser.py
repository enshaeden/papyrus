from __future__ import annotations

from pathlib import Path
from typing import Iterable

import yaml

from papyrus.domain.entities import BrokenLink, KnowledgeDocument
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

