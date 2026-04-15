from __future__ import annotations

import re
from collections.abc import Iterable
from pathlib import Path

from papyrus.domain.entities import ValidationIssue
from papyrus.infrastructure.paths import ROOT, relative_path

FENCED_CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
REPO_PATH_TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"(?P<path>"
    r"(?:README\.md|AGENTS\.md|pyproject\.toml|requirements(?:-dev)?\.txt|"
    r"\.github/workflows/[A-Za-z0-9_.-]+|"
    r"(?:archive|decisions|docs|knowledge|schemas|scripts|src|taxonomies|templates|tests)"
    r"(?:/[A-Za-z0-9_.-]+)*/?)"
    r")"
)
WEB_ROUTE_TOKEN_PATTERN = re.compile(r"/(?:reader|operator|admin)(?:/[A-Za-z0-9{}:*._-]+)*(?:/\*)?")
STATIC_ASSET_PATTERN = re.compile(
    r"""(?:href|src)=["'](?P<asset>/static/[^"']+)["']""", re.IGNORECASE
)
STATIC_ASSET_LITERAL_PATTERN = re.compile(r"""["'](?P<asset>/static/[^"']+)["']""")
CSS_URL_PATTERN = re.compile(r"url\((?P<target>[^)]+)\)")
EXTERNAL_ASSET_PREFIXES = ("http://", "https://", "//", "data:", "#")


def _strip_fenced_code_blocks(text: str) -> str:
    return FENCED_CODE_BLOCK_PATTERN.sub("", text)


def _inline_code_spans(path: Path) -> list[str]:
    text = _strip_fenced_code_blocks(path.read_text(encoding="utf-8"))
    return INLINE_CODE_PATTERN.findall(text)


def _normalize_documented_route(route: str) -> str:
    clean_route = route.strip().split("?", 1)[0].split("#", 1)[0]
    if clean_route == "/":
        return clean_route
    if clean_route.endswith("/*"):
        clean_route = clean_route[:-2] + "/*"
    normalized_segments: list[str] = []
    wildcard_suffix = clean_route.endswith("/*")
    route_body = clean_route[:-2] if wildcard_suffix else clean_route
    for segment in route_body.strip("/").split("/"):
        if not segment:
            continue
        if segment.startswith(":") or (segment.startswith("{") and segment.endswith("}")):
            normalized_segments.append("{}")
            continue
        normalized_segments.append(segment)
    normalized = "/" + "/".join(normalized_segments)
    if wildcard_suffix:
        normalized += "/*"
    return normalized


def _normalized_registered_web_routes() -> set[str]:
    from papyrus.interfaces.web.route_catalog import collect_registered_routes

    normalized: set[str] = set()
    for route in collect_registered_routes():
        if route.pattern == "/":
            normalized.add(route.pattern)
            continue
        normalized_segments: list[str] = []
        for segment in route.pattern.strip("/").split("/"):
            if segment.startswith("{") and segment.endswith("}"):
                normalized_segments.append("{}")
                continue
            normalized_segments.append(segment)
        normalized.add("/" + "/".join(normalized_segments))
    return normalized


def validate_documented_repository_paths(paths: Iterable[Path]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in paths:
        for code_span in _inline_code_spans(path):
            for match in REPO_PATH_TOKEN_PATTERN.finditer(code_span):
                candidate = match.group("path").rstrip(".,:;")
                if "{" in candidate or "}" in candidate:
                    continue
                candidate_path = ROOT / candidate.rstrip("/")
                if (
                    candidate.endswith("/")
                    and candidate_path.exists()
                    and not candidate_path.is_dir()
                ):
                    issues.append(
                        ValidationIssue(
                            relative_path(path),
                            f"documented path '{candidate}' is not a directory",
                        )
                    )
                    continue
                if candidate_path.exists():
                    continue
                issues.append(
                    ValidationIssue(
                        relative_path(path),
                        f"documented path '{candidate}' does not exist",
                    )
                )
    return issues


def validate_documented_web_routes(paths: Iterable[Path]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    registered_routes = _normalized_registered_web_routes()
    for path in paths:
        route_tokens: set[str] = set()
        for code_span in _inline_code_spans(path):
            if code_span.strip() == "/":
                route_tokens.add("/")
            route_tokens.update(WEB_ROUTE_TOKEN_PATTERN.findall(code_span))
        for route in sorted(route_tokens):
            normalized_route = _normalize_documented_route(route)
            if normalized_route.endswith("/*"):
                prefix = normalized_route[:-2]
                if any(
                    item == prefix or item.startswith(prefix + "/") for item in registered_routes
                ):
                    continue
            elif normalized_route in registered_routes:
                continue
            issues.append(
                ValidationIssue(
                    relative_path(path),
                    f"documented web route '{route}' does not exist in the registered route map",
                )
            )
    return issues


def _web_static_asset_path(asset_reference: str) -> Path:
    return (
        ROOT
        / "src"
        / "papyrus"
        / "interfaces"
        / "web"
        / "static"
        / asset_reference.removeprefix("/static/")
    )


def _validate_static_asset_reference(
    source_path: Path, asset_reference: str
) -> ValidationIssue | None:
    asset_path = _web_static_asset_path(asset_reference)
    if asset_path.exists() and asset_path.is_file():
        return None
    return ValidationIssue(
        relative_path(source_path),
        f"static asset reference '{asset_reference}' does not exist",
    )


def _validate_web_template_assets() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    template_root = ROOT / "src" / "papyrus" / "interfaces" / "web" / "templates"
    for path in sorted(template_root.rglob("*.html")):
        text = path.read_text(encoding="utf-8")
        for match in STATIC_ASSET_PATTERN.finditer(text):
            issue = _validate_static_asset_reference(path, match.group("asset"))
            if issue is not None:
                issues.append(issue)
    return issues


def _validate_route_script_assets() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    route_root = ROOT / "src" / "papyrus" / "interfaces" / "web" / "routes"
    for path in sorted(route_root.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in STATIC_ASSET_LITERAL_PATTERN.finditer(text):
            issue = _validate_static_asset_reference(path, match.group("asset"))
            if issue is not None:
                issues.append(issue)
    return issues


def _clean_css_url_target(target: str) -> str:
    return target.strip().strip("'\"")


def _validate_css_asset_urls() -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    css_roots = (
        ROOT / "src" / "papyrus" / "interfaces" / "web" / "static" / "css",
        ROOT / "docs" / "assets",
    )
    for root in css_roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.css")):
            text = path.read_text(encoding="utf-8")
            for match in CSS_URL_PATTERN.finditer(text):
                target = _clean_css_url_target(match.group("target"))
                if not target or target.startswith(EXTERNAL_ASSET_PREFIXES):
                    continue
                if target.startswith("/static/"):
                    issue = _validate_static_asset_reference(path, target)
                    if issue is not None:
                        issues.append(issue)
                    continue
                resolved = (path.parent / target).resolve()
                if resolved.exists() and resolved.is_file():
                    continue
                issues.append(
                    ValidationIssue(
                        relative_path(path),
                        f"css asset reference '{target}' does not exist",
                    )
                )
    return issues


def validate_static_asset_references() -> list[ValidationIssue]:
    issues = []
    issues.extend(_validate_web_template_assets())
    issues.extend(_validate_route_script_assets())
    issues.extend(_validate_css_asset_urls())
    return issues
