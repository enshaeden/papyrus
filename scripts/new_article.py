#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

from _bootstrap import ensure_src_path

ensure_src_path()

from papyrus.compat.kb_common import FRONT_MATTER_PATTERN, load_policy, load_taxonomies, similarity_ratio, slugify

TYPE_TO_DIRECTORY = {
    "runbook": "runbooks",
    "known_error": "known-errors",
    "service_record": "service-records",
}

LISTABLE_TAXONOMIES = (
    "knowledge_object_types",
    "audiences",
    "services",
    "systems",
    "tags",
    "statuses",
    "teams",
    "review_cadences",
    "source_types",
    "service_criticality",
    "permanent_fix_status",
)


def render_template(template_text: str, substitutions: dict[str, str]) -> str:
    content = template_text
    for key, value in substitutions.items():
        content = content.replace(f"{{{{{key}}}}}", value)
    return content


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def render_yaml_field(field_name: str, values: list[str]) -> str:
    if not values:
        return f"{field_name}: []"
    return "\n".join([f"{field_name}:", *[f"- {value}" for value in values]])


def render_inline_list(values: list[str]) -> str:
    return yaml.safe_dump(values, default_flow_style=True, sort_keys=False).strip()


def load_existing_article_records(root: Path, policy: dict[str, object]) -> list[dict[str, object]]:
    records = []
    for directory in policy["directories"]["canonical_article_roots"]:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            match = FRONT_MATTER_PATTERN.match(text)
            if not match:
                continue
            metadata = yaml.safe_load(match.group(1)) or {}
            if not isinstance(metadata, dict):
                continue
            records.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "metadata": metadata,
                }
            )
    return records


def object_type(metadata: dict[str, object]) -> str:
    return str(metadata.get("knowledge_object_type") or metadata.get("type") or "")


def services_for(metadata: dict[str, object]) -> list[str]:
    values = metadata.get("related_services") or metadata.get("services") or []
    return [str(item) for item in values]


def related_article_suggestions(
    destination: Path,
    draft_metadata: dict[str, object],
    existing_records: list[dict[str, object]],
) -> list[tuple[int, dict[str, object], list[str]]]:
    results = []
    for record in existing_records:
        metadata = record["metadata"]
        if metadata.get("id") == draft_metadata["id"]:
            continue

        reasons = []
        score = 0
        shared_services = sorted(set(draft_metadata["services"]).intersection(services_for(metadata)))
        if shared_services:
            score += len(shared_services) * 4
            reasons.append(f"shared service: {', '.join(shared_services)}")

        shared_systems = sorted(set(draft_metadata["systems"]).intersection(metadata.get("systems", [])))
        if shared_systems:
            score += len(shared_systems) * 3
            reasons.append(f"shared system: {', '.join(shared_systems)}")

        shared_tags = sorted(set(draft_metadata["tags"]).intersection(metadata.get("tags", [])))
        if shared_tags:
            score += len(shared_tags) * 2
            reasons.append(f"shared tag: {', '.join(shared_tags)}")

        if draft_metadata["audience"] == metadata.get("audience"):
            score += 2
            reasons.append(f"shared audience: {draft_metadata['audience']}")

        if draft_metadata["team"] == metadata.get("team"):
            score += 1
            reasons.append(f"shared team: {draft_metadata['team']}")

        if draft_metadata["knowledge_object_type"] == object_type(metadata):
            score += 1
            reasons.append(f"shared object type: {draft_metadata['knowledge_object_type']}")

        if destination.parent.as_posix() == Path(record["path"]).parent.as_posix():
            score += 2
            reasons.append("same knowledge-tree section")

        title_similarity = similarity_ratio(str(draft_metadata["title"]), str(metadata.get("title", "")))
        if title_similarity >= 0.62:
            score += 3
            reasons.append(f"similar title ({title_similarity:.2f})")

        if score >= 3:
            results.append((score, record, reasons))

    return sorted(results, key=lambda item: (-item[0], item[1]["metadata"].get("title", "")))


def print_taxonomy(name: str, values: list[object]) -> None:
    print(f"[{name}]")
    for entry in values:
        if isinstance(entry, dict):
            description = entry.get("description", "")
            print(f"{entry['name']} | {description}")
        else:
            print(str(entry))


def emit_authoring_feedback(
    draft_metadata: dict[str, object],
    related_ids: list[str],
    suggestions: list[tuple[int, dict[str, object], list[str]]],
) -> None:
    empty_fields = [
        field_name
        for field_name in ("services", "systems", "tags")
        if not draft_metadata[field_name]
    ]
    if empty_fields:
        print(
            "Discovery warning: scaffold still has empty "
            + ", ".join(empty_fields)
            + ". Populate these before merging so runtime search and export views can classify the object.",
            file=sys.stderr,
        )
        print(
            "Hint: use --list-taxonomy services --list-taxonomy systems --list-taxonomy tags to review valid values.",
            file=sys.stderr,
        )

    if not related_ids:
        print(
            "Interoperability warning: related_object_ids is still empty. Add prerequisite, follow-on, escalation, or sibling knowledge links before merging when applicable.",
            file=sys.stderr,
        )

    if not suggestions:
        print(
            "[Inference] No strong related-object candidates were identified from the existing repository metadata.",
            file=sys.stderr,
        )
        return

    print("[Inference] Candidate related knowledge objects based on title and metadata overlap:", file=sys.stderr)
    for score, record, reasons in suggestions[:5]:
        metadata = record["metadata"]
        print(
            f"- {metadata.get('id', '<missing-id>')} | {metadata.get('title', '<missing-title>')} | "
            f"{record['path']} | {'; '.join(reasons)} | score {score}",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a new Papyrus knowledge object from an approved template")
    parser.add_argument("--root", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--title", help="Object title")
    parser.add_argument("--type", help="Knowledge object type from taxonomies/knowledge_object_types.yml")
    parser.add_argument("--slug", help="Optional explicit slug. Derived from title when omitted.")
    parser.add_argument("--owner", default="TBD", help="Object owner")
    parser.add_argument("--team", default="Service Desk", help="Responsible team")
    parser.add_argument("--status", default="draft", help="Lifecycle status")
    parser.add_argument("--audience", default="service_desk", help="Primary audience")
    parser.add_argument("--service", action="append", default=[], help="Service taxonomy value. Repeatable.")
    parser.add_argument("--system", action="append", default=[], help="System taxonomy value. Repeatable.")
    parser.add_argument("--tag", action="append", default=[], help="Tag taxonomy value. Repeatable.")
    parser.add_argument(
        "--related-object",
        action="append",
        dest="related_object",
        default=[],
        help="Existing knowledge object id to prefill in related_object_ids. Repeatable.",
    )
    parser.add_argument(
        "--related-article",
        action="append",
        dest="related_object",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--list-taxonomy",
        action="append",
        choices=LISTABLE_TAXONOMIES,
        help="Print allowed values and descriptions for a taxonomy, then exit.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    policy = load_policy(root / "schemas" / "repository_policy.yml")
    taxonomies = load_taxonomies(root / "taxonomies")

    if args.list_taxonomy:
        for name in args.list_taxonomy:
            print_taxonomy(name, taxonomies[name]["values"])
        return 0

    if not args.title or not args.type:
        parser.error("--title and --type are required unless --list-taxonomy is used.")

    def ensure_allowed(value: str, taxonomy_name: str, field_name: str) -> None:
        allowed = set(taxonomies[taxonomy_name]["allowed_values"])
        if value not in allowed:
            raise ValueError(f"{field_name} must be one of {sorted(allowed)}")

    allowed_types = set(taxonomies["knowledge_object_types"]["allowed_values"])
    if args.type not in allowed_types:
        print(f"unsupported knowledge object type: {args.type}", file=sys.stderr)
        return 1

    try:
        ensure_allowed(args.status, "statuses", "status")
        ensure_allowed(args.team, "teams", "team")
        ensure_allowed(args.audience, "audiences", "audience")
        for service in args.service:
            ensure_allowed(service, "services", "service")
        for system in args.system:
            ensure_allowed(system, "systems", "system")
        for tag in args.tag:
            ensure_allowed(tag, "tags", "tag")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    family_mapping = policy["templates"]["family_by_knowledge_object_type"]
    family = family_mapping.get(args.type)
    if not family:
        print(f"no approved template family for knowledge object type: {args.type}", file=sys.stderr)
        return 1

    slug = args.slug or slugify(args.title)
    article_id = f"kb-{args.type.replace('_', '-')}-{slug}"
    directory = root / "knowledge" / TYPE_TO_DIRECTORY[args.type]
    directory.mkdir(parents=True, exist_ok=True)
    destination = directory / f"{slug}.md"
    if destination.exists():
        print(f"refusing to overwrite existing file: {destination}", file=sys.stderr)
        return 1

    existing_records = load_existing_article_records(root, policy)
    known_ids = {record["metadata"].get("id") for record in existing_records if record["metadata"].get("id")}
    for related_id in args.related_object:
        if related_id not in known_ids:
            print(f"related knowledge object not found: {related_id}", file=sys.stderr)
            return 1

    template_path = root / "templates" / f"{family}.md"
    template_text = template_path.read_text(encoding="utf-8")
    today = dt.date.today().isoformat()

    services = unique_preserving_order(args.service)
    systems = unique_preserving_order(args.system)
    tags = unique_preserving_order(args.tag)
    related_objects = unique_preserving_order(args.related_object)

    draft_metadata = {
        "id": article_id,
        "title": args.title,
        "knowledge_object_type": args.type,
        "team": args.team,
        "audience": args.audience,
        "services": services,
        "systems": systems,
        "tags": tags,
    }

    rendered = render_template(
        template_text,
        {
            "id": article_id,
            "title": args.title,
            "canonical_path": destination.relative_to(root).as_posix(),
            "status": args.status,
            "owner": args.owner,
            "team": args.team,
            "audience": args.audience,
            "today": today,
            "related_services_field": render_yaml_field("related_services", services),
            "systems_field": render_yaml_field("systems", systems),
            "tags_field": render_yaml_field("tags", tags),
            "related_object_ids_field": render_yaml_field("related_object_ids", related_objects),
            "related_services_inline": render_inline_list(services),
            "related_object_ids_inline": render_inline_list(related_objects),
        },
    )
    destination.write_text(rendered, encoding="utf-8")
    print(destination.relative_to(root).as_posix())

    emit_authoring_feedback(
        draft_metadata,
        related_objects,
        related_article_suggestions(destination, draft_metadata, existing_records),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
