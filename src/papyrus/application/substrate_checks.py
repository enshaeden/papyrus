from __future__ import annotations

import ast
import re
from collections.abc import Iterable
from pathlib import Path

from papyrus.domain.entities import ValidationIssue
from papyrus.infrastructure.paths import ROOT, relative_path

FENCED_CODE_BLOCK_PATTERN = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")
REPO_PATH_TOKEN_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_.-/])"
    r"(?<!knowledge_engine/)"
    r"(?P<path>"
    r"(?:README\.md|AGENTS\.md|pyproject\.toml|requirements(?:-dev)?\.txt|"
    r"\.github/workflows/[A-Za-z0-9_.-]+|"
    r"(?:decisions|docs|knowledge|knowledge_engine|reports|scripts|src|tests|"
    r"schemas|taxonomies|templates)"
    r"(?:/[A-Za-z0-9_.-]+)*/?)"
    r")"
)
WEB_ROUTE_TOKEN_PATTERN = re.compile(
    r"/(?:read|write|review|import|governance|admin)(?:/[A-Za-z0-9{}:*._-]+)*(?:/\*)?"
)
STATIC_ASSET_PATTERN = re.compile(
    r"""(?:href|src)=["'](?P<asset>/static/[^"']+)["']""", re.IGNORECASE
)
STATIC_ASSET_LITERAL_PATTERN = re.compile(r"""["'](?P<asset>/static/[^"']+)["']""")
CSS_URL_PATTERN = re.compile(r"url\((?P<target>[^)]+)\)")
EXTERNAL_ASSET_PREFIXES = ("http://", "https://", "//", "data:", "#")
WEB_INTERFACE_ROOT = ROOT / "src" / "papyrus" / "interfaces" / "web"
WEB_COPY_POLICY_FORBIDDEN_PAGE_HEADER_FIELDS = frozenset(
    ("intro", "summary", "subtitle", "description", "helper", "supporting", "blurb")
)
WEB_COPY_POLICY_FORBIDDEN_PARAGRAPH_TAILS = frozenset(
    ("intro", "summary", "subtitle", "description", "helper", "supporting", "blurb")
)
WEB_COPY_POLICY_ALLOWED_HEADER_ADJACENT_PARAGRAPH_CLASSES = {
    "governed-summary": (
        "State-critical trust and workflow posture messaging prevents unsafe or incorrect actions."
    ),
    "governed-action-summary": (
        "State-critical action contract summary clarifies governed availability and transition state."
    ),
    "ingest-progress__summary": (
        "Workflow-critical current-stage summary prevents import operators from acting on the wrong step."
    ),
    "service-map__summary": (
        "State-critical service posture line communicates degraded or missing-guidance status."
    ),
}
WEB_COPY_POLICY_PARAGRAPH_CLASS_PATTERN = re.compile(
    r"""<p[^>]*class=["'](?P<class_names>[^"']+)["'][^>]*>""", re.IGNORECASE
)
WEB_COPY_POLICY_HEADING_CLOSE_PATTERN = re.compile(r"</h[1-6]>|</summary>", re.IGNORECASE)
WEB_COPY_POLICY_HEADING_LOOKAHEAD_CHARS = 240


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


def _resolve_documented_path(source_path: Path, candidate: str) -> Path:
    normalized = candidate.rstrip("/")
    root_relative = ROOT / normalized
    if root_relative.exists():
        return root_relative
    relative = (source_path.parent / normalized).resolve()
    if relative.exists():
        return relative
    return root_relative


def validate_documented_repository_paths(paths: Iterable[Path]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for path in paths:
        for code_span in _inline_code_spans(path):
            for match in REPO_PATH_TOKEN_PATTERN.finditer(code_span):
                candidate = match.group("path").rstrip(".,:;")
                if "{" in candidate or "}" in candidate:
                    continue
                candidate_path = _resolve_documented_path(path, candidate)
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


def _constant_str(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _subscript_key_chain(node: ast.AST) -> list[str] | None:
    chain: list[str] = []
    current = node
    while isinstance(current, ast.Subscript):
        key = _constant_str(current.slice)
        if key is None:
            return None
        chain.insert(0, key)
        current = current.value
    if isinstance(current, ast.Name):
        chain.insert(0, current.id)
        return chain
    return None


class _PageHeaderCopyFieldVisitor(ast.NodeVisitor):
    def __init__(self, *, source_path: Path):
        self.source_path = source_path
        self.issues: list[ValidationIssue] = []

    def _record_issue(self, *, field_name: str, lineno: int) -> None:
        self.issues.append(
            ValidationIssue(
                relative_path(self.source_path),
                (
                    f"page_header field '{field_name}' is forbidden by the web copy policy; "
                    "use headline, kicker, explicit state, or actions instead"
                ),
                field=f"line {lineno}",
            )
        )

    def _inspect_page_header_dict(self, node: ast.Dict) -> None:
        for key_node in node.keys:
            field_name = _constant_str(key_node)
            if field_name in WEB_COPY_POLICY_FORBIDDEN_PAGE_HEADER_FIELDS and key_node is not None:
                self._record_issue(
                    field_name=field_name,
                    lineno=int(getattr(key_node, "lineno", getattr(node, "lineno", 1))),
                )

    def visit_Dict(self, node: ast.Dict) -> None:
        for key_node, value_node in zip(node.keys, node.values, strict=False):
            if _constant_str(key_node) == "page_header" and isinstance(value_node, ast.Dict):
                self._inspect_page_header_dict(value_node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        for keyword in node.keywords:
            if keyword.arg == "page_header" and isinstance(keyword.value, ast.Dict):
                self._inspect_page_header_dict(keyword.value)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            chain = _subscript_key_chain(target)
            if not chain:
                continue
            if chain[-1] == "page_header" and isinstance(node.value, ast.Dict):
                self._inspect_page_header_dict(node.value)
                continue
            if len(chain) >= 2 and chain[-2] == "page_header":
                field_name = chain[-1]
                if field_name in WEB_COPY_POLICY_FORBIDDEN_PAGE_HEADER_FIELDS:
                    self._record_issue(
                        field_name=field_name,
                        lineno=int(getattr(target, "lineno", getattr(node, "lineno", 1))),
                    )
        self.generic_visit(node)


def _validate_web_page_header_copy_fields(source_path: Path, text: str) -> list[ValidationIssue]:
    try:
        tree = ast.parse(text, filename=str(source_path))
    except SyntaxError as error:
        return [
            ValidationIssue(
                relative_path(source_path),
                f"cannot parse Python source while validating web copy policy: {error.msg}",
                field=f"line {error.lineno or 1}",
            )
        ]
    visitor = _PageHeaderCopyFieldVisitor(source_path=source_path)
    visitor.visit(tree)
    return visitor.issues


def _paragraph_tail(class_name: str) -> str:
    parts = [part for part in re.split(r"__|-", class_name) if part]
    return parts[-1] if parts else class_name


def _validate_header_adjacent_paragraph_classes(
    source_path: Path, text: str
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: set[tuple[int, str]] = set()
    normalized_text = text.replace('\\"', '"').replace("\\'", "'")
    for heading_match in WEB_COPY_POLICY_HEADING_CLOSE_PATTERN.finditer(normalized_text):
        line_number = normalized_text.count("\n", 0, heading_match.start()) + 1
        lookahead = normalized_text[
            heading_match.end() : heading_match.end() + WEB_COPY_POLICY_HEADING_LOOKAHEAD_CHARS
        ]
        for paragraph_match in WEB_COPY_POLICY_PARAGRAPH_CLASS_PATTERN.finditer(lookahead):
            for class_name in paragraph_match.group("class_names").split():
                if class_name in WEB_COPY_POLICY_ALLOWED_HEADER_ADJACENT_PARAGRAPH_CLASSES:
                    continue
                if _paragraph_tail(class_name) not in WEB_COPY_POLICY_FORBIDDEN_PARAGRAPH_TAILS:
                    continue
                key = (line_number, class_name)
                if key in seen:
                    continue
                seen.add(key)
                issues.append(
                    ValidationIssue(
                        relative_path(source_path),
                        (
                            f"header-adjacent paragraph class '{class_name}' is forbidden by the "
                            "web copy policy; keep headings terse or add an explicit "
                            "state/safety justification to the allowlist"
                        ),
                        field=f"line {line_number}",
                    )
                )
    return issues


def validate_web_copy_policy_source(source_path: Path, text: str) -> list[ValidationIssue]:
    issues = _validate_header_adjacent_paragraph_classes(source_path, text)
    if source_path.suffix == ".py":
        issues.extend(_validate_web_page_header_copy_fields(source_path, text))
    return issues


def validate_web_copy_policy(paths: Iterable[Path] | None = None) -> list[ValidationIssue]:
    source_paths = (
        sorted(path for path in WEB_INTERFACE_ROOT.rglob("*") if path.suffix in {".py", ".html"})
        if paths is None
        else list(paths)
    )
    issues: list[ValidationIssue] = []
    for path in source_paths:
        if "__pycache__" in path.parts:
            continue
        issues.extend(validate_web_copy_policy_source(path, path.read_text(encoding="utf-8")))
    return issues
