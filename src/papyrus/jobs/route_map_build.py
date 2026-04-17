from __future__ import annotations

import argparse
import json
from pathlib import Path

from papyrus.infrastructure.paths import (
    GENERATED_ROUTE_MAP_JSON_PATH,
    GENERATED_ROUTE_MAP_MARKDOWN_PATH,
    ROOT,
    relative_path,
)
from papyrus.interfaces.web.route_catalog import collect_registered_routes


def _normalized_registered_routes() -> list[dict[str, object]]:
    return [
        route.as_dict()
        for route in sorted(
            collect_registered_routes(), key=lambda route: (route.pattern, route.methods)
        )
    ]


def render_route_map_json() -> str:
    return (
        json.dumps(
            {"routes": _normalized_registered_routes()}, indent=2, sort_keys=True, ensure_ascii=True
        )
        + "\n"
    )


def render_route_map_markdown() -> str:
    lines = [
        "# Route Map",
        "",
        "Derived from the registered Papyrus web routes. Do not edit by hand.",
        "",
        "| Methods | Pattern | Minimum Role | Owner |",
        "| --- | --- | --- | --- |",
    ]
    for route in _normalized_registered_routes():
        methods = ", ".join(str(method) for method in route["methods"])
        owner = f"`{route['handler_module']}.{route['handler_name']}`"
        lines.append(
            f"| `{methods}` | `{route['pattern']}` | `{route['minimum_visible_role']}` | {owner} |"
        )
    lines.append("")
    return "\n".join(lines)


def _write_text(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def build_route_map(*, json_output: Path, markdown_output: Path) -> tuple[Path, Path]:
    _write_text(json_output, render_route_map_json())
    _write_text(markdown_output, render_route_map_markdown())
    return json_output, markdown_output


def check_route_map(*, json_output: Path, markdown_output: Path) -> list[str]:
    expected = (
        (json_output, render_route_map_json()),
        (markdown_output, render_route_map_markdown()),
    )
    findings: list[str] = []
    for path, contents in expected:
        if not path.exists():
            findings.append(
                f"{relative_path(path) if path.is_relative_to(ROOT) else str(path)} is missing; run scripts/build_route_map.py"
            )
            continue
        existing = path.read_text(encoding="utf-8")
        if existing != contents:
            findings.append(
                f"{relative_path(path) if path.is_relative_to(ROOT) else str(path)} is stale; run scripts/build_route_map.py"
            )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build or verify the derived Papyrus web route map."
    )
    parser.add_argument(
        "--check", action="store_true", help="Fail if the checked-in route map artifacts are stale."
    )
    parser.add_argument(
        "--json-output",
        default=str(GENERATED_ROUTE_MAP_JSON_PATH),
        help="JSON output path. Defaults to generated/route-map.json.",
    )
    parser.add_argument(
        "--markdown-output",
        default=str(GENERATED_ROUTE_MAP_MARKDOWN_PATH),
        help="Markdown output path. Defaults to generated/route-map.md.",
    )
    args = parser.parse_args()

    json_output = Path(args.json_output)
    markdown_output = Path(args.markdown_output)

    if args.check:
        findings = check_route_map(json_output=json_output, markdown_output=markdown_output)
        if findings:
            for finding in findings:
                print(finding)
            return 1
        print("route map is current")
        return 0

    build_route_map(json_output=json_output, markdown_output=markdown_output)
    print(f"wrote {json_output}")
    print(f"wrote {markdown_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
