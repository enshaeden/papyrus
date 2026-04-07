#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from kb_common import load_policy, load_taxonomies, slugify

TYPE_TO_DIRECTORY = {
    "runbook": "runbooks",
    "SOP": "sops",
    "troubleshooting": "troubleshooting",
    "FAQ": "faqs",
    "reference": "reference",
    "policy": "policies",
    "onboarding": "onboarding",
    "offboarding": "offboarding",
    "access": "access",
    "asset": "assets",
    "incident": "incidents",
    "postmortem": "postmortems",
}


def render_template(template_text: str, substitutions: dict[str, str]) -> str:
    content = template_text
    for key, value in substitutions.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new knowledge article from an approved template")
    parser.add_argument("--root", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--title", required=True, help="Article title")
    parser.add_argument("--type", required=True, help="Article type from taxonomies/article_types.yml")
    parser.add_argument("--slug", help="Optional explicit slug. Derived from title when omitted.")
    parser.add_argument("--owner", default="TBD", help="Article owner")
    parser.add_argument("--team", default="Service Desk", help="Responsible team")
    parser.add_argument("--status", default="draft", help="Lifecycle status")
    parser.add_argument("--audience", default="service_desk", help="Primary audience")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    policy = load_policy(root / "schemas" / "repository_policy.yml")
    taxonomies = load_taxonomies(root / "taxonomies")

    def ensure_allowed(value: str, taxonomy_name: str, field_name: str) -> None:
        allowed = set(taxonomies[taxonomy_name]["allowed_values"])
        if value not in allowed:
            raise ValueError(f"{field_name} must be one of {sorted(allowed)}")

    allowed_types = set(taxonomies["article_types"]["allowed_values"])
    if args.type not in allowed_types:
        print(f"unsupported article type: {args.type}", file=sys.stderr)
        return 1

    try:
        ensure_allowed(args.status, "statuses", "status")
        ensure_allowed(args.team, "teams", "team")
        ensure_allowed(args.audience, "audiences", "audience")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    family_mapping = policy["templates"]["family_by_article_type"]
    family = family_mapping.get(args.type)
    if not family:
        print(f"no approved template family for article type: {args.type}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    article_id = f"kb-{args.type.lower().replace(' ', '-')}-{slug}"
    directory = root / "knowledge" / TYPE_TO_DIRECTORY[args.type]
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{slug}.md"
    if destination.exists():
        print(f"refusing to overwrite existing file: {destination}", file=sys.stderr)
        return 1

    template_path = root / "templates" / f"{family}.md"
    template_text = template_path.read_text(encoding="utf-8")
    today = dt.date.today().isoformat()
    rendered = render_template(
        template_text,
        {
            "id": article_id,
            "title": args.title,
            "canonical_path": destination.relative_to(root).as_posix(),
            "type": args.type,
            "status": args.status,
            "owner": args.owner,
            "team": args.team,
            "audience": args.audience,
            "today": today,
        },
    )
    destination.write_text(rendered, encoding="utf-8")
    print(destination.relative_to(root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
