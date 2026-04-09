from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

from papyrus.application.commands import build_projection_command, validate_repository_command
from papyrus.application.queries import (
    CONTENT_HEALTH_SECTIONS,
    collect_content_health_sections,
    event_history,
    knowledge_object_detail,
    knowledge_queue,
    manage_queue,
    review_detail,
    search_projection,
    stale_projection,
    trust_dashboard,
    validation_run_history,
)
from papyrus.application.writeback_flow import preview_revision_writeback
from papyrus.domain.policies import searchable_statuses
from papyrus.infrastructure.markdown.serializer import parse_iso_date
from papyrus.infrastructure.paths import DB_PATH
from papyrus.infrastructure.repositories.knowledge_repo import load_policy


def validate_main() -> int:
    parser = argparse.ArgumentParser(description="Validate repository source content and optional rendered site output.")
    parser.add_argument(
        "--include-rendered-site",
        action="store_true",
        help="also validate built site/ HTML href targets",
    )
    args = parser.parse_args()

    try:
        result = validate_repository_command(include_rendered_site=args.include_rendered_site)
    except Exception as exc:  # pragma: no cover - exercised via CLI tests
        print(f"validation setup failed: {exc}", file=sys.stderr)
        return 1

    if result.issues:
        for issue in result.issues:
            print(issue.render(), file=sys.stderr)
        print(f"validation failed with {len(result.issues)} issue(s)", file=sys.stderr)
        return 1

    print(f"validated {result.document_count} knowledge object source file(s)")
    return 0


def search_main() -> int:
    policy = load_policy()
    parser = argparse.ArgumentParser(description="Search the local knowledge index")
    parser.add_argument("query", help="FTS or substring query")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results to return")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the SQLite database")
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include archived content in search results.",
    )
    parser.add_argument(
        "--include-draft",
        action="store_true",
        help="Include draft content in search results.",
    )
    args = parser.parse_args()

    statuses = list(searchable_statuses(policy))
    if args.include_draft and "draft" not in statuses:
        statuses.append("draft")
    if args.include_archived and "archived" not in statuses:
        statuses.append("archived")

    try:
        rows = search_projection(args.query, args.limit, args.db, statuses)
    except sqlite3.OperationalError as exc:
        print(f"search failed: {exc}", file=sys.stderr)
        return 1

    if not rows:
        print("no matches found")
        return 0

    for row in rows:
        print(
            f"{row.object_id} | {row.title} | {row.content_type} | {row.status} | "
            f"{row.path}\n  {row.summary}"
        )
    return 0


def report_stale_main() -> int:
    parser = argparse.ArgumentParser(description="Report active or deprecated articles due for review")
    parser.add_argument(
        "--as-of",
        default=dt.date.today().isoformat(),
        help="Report date in ISO 8601 format. Defaults to today.",
    )
    parser.add_argument(
        "--include-deprecated",
        action="store_true",
        help="Include deprecated content in the stale report.",
    )
    args = parser.parse_args()

    rows = stale_projection(
        as_of=parse_iso_date(args.as_of),
        include_deprecated=args.include_deprecated,
        database_path=DB_PATH,
    )
    if not rows:
        print("no stale knowledge objects found")
        return 0

    for days_overdue, object_id, title, path, due_date in rows:
        print(
            f"{days_overdue:>4} days overdue | {due_date.isoformat()} | "
            f"{object_id} | {title} | {path}"
        )
    return 0


def report_content_health_main() -> int:
    parser = argparse.ArgumentParser(description="Report repository content health and drift signals")
    parser.add_argument(
        "--section",
        choices=CONTENT_HEALTH_SECTIONS,
        action="append",
        help="Limit output to one or more sections.",
    )
    args = parser.parse_args()

    selected = args.section or list(CONTENT_HEALTH_SECTIONS)
    outputs = collect_content_health_sections(selected)
    for section in selected:
        print(f"[{section}]")
        lines = outputs.get(section, [])
        if not lines:
            print("none")
            continue
        for line in lines:
            print(line)
    return 0


def build_index_main() -> int:
    try:
        result = build_projection_command()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"built {result.database_path} with {result.document_count} knowledge object(s) using {result.mode}")
    return 0


def _emit_payload(payload: object, *, output_format: str) -> int:
    if output_format == "json":
        print(json.dumps(payload, sort_keys=True, ensure_ascii=True, indent=2))
        return 0
    if isinstance(payload, list):
        for item in payload:
            print(item)
        return 0
    print(payload)
    return 0


def _safe_to_use_text(*, approval_state: str | None, trust_state: str | None) -> str:
    approval = str(approval_state or "").strip()
    trust = str(trust_state or "").strip()
    if approval == "approved" and trust == "trusted":
        return "safe to use now"
    if approval in {"draft", "rejected"}:
        return "complete or revise before use"
    if approval == "in_review":
        return "review decision pending before use"
    if trust == "weak_evidence":
        return "verify evidence before use"
    if trust == "stale":
        return "revalidate freshness before use"
    if trust == "suspect":
        return "do not rely on this until reviewed"
    return "inspect the lifecycle posture before use"


def _line_block(*lines: str) -> list[str]:
    return [line for line in lines if line]


def operator_main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Papyrus lifecycle, stewardship, and consequence surfaces from the terminal.")
    parser.add_argument("--db", default=str(DB_PATH), help="Path to the runtime SQLite database.")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Output format.")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--db", default=None, help=argparse.SUPPRESS)
    common.add_argument("--format", choices=("text", "json"), default=None, help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    queue_parser = subparsers.add_parser("queue", help="Show guided read results.", parents=[common])
    queue_parser.add_argument("--limit", type=int, default=25, help="Maximum queue items.")

    dashboard_parser = subparsers.add_parser(
        "dashboard",
        aliases=["health"],
        help="Show knowledge health and stewardship signals.",
        parents=[common],
    )
    dashboard_parser.add_argument("--limit", type=int, default=25, help="Maximum queue items in text mode.")

    object_parser = subparsers.add_parser("object", help="Show guided object detail.", parents=[common])
    object_parser.add_argument("object_id", help="Knowledge object ID.")

    review_parser = subparsers.add_parser("review", help="Show review detail for a revision.", parents=[common])
    review_parser.add_argument("object_id", help="Knowledge object ID.")
    review_parser.add_argument("revision_id", help="Revision ID.")

    events_parser = subparsers.add_parser(
        "events",
        aliases=["activity"],
        help="Show operational activity and consequence history.",
        parents=[common],
    )
    events_parser.add_argument("--limit", type=int, default=25, help="Maximum events to return.")
    events_parser.add_argument("--entity-type", default=None, help="Optional entity type filter.")
    events_parser.add_argument("--entity-id", default=None, help="Optional entity ID filter.")
    events_parser.add_argument("--event-type", default=None, help="Optional event type filter.")

    subparsers.add_parser("manage-queue", help="Show review and stewardship buckets.", parents=[common])
    subparsers.add_parser("validation-runs", help="Show validation run history.", parents=[common])

    args = parser.parse_args()
    database_path = args.db or str(DB_PATH)
    output_format = args.format or "text"

    if args.command == "queue":
        payload = knowledge_queue(limit=args.limit, database_path=database_path)
        if output_format == "json":
            return _emit_payload({"queue": payload}, output_format=output_format)
        lines = ["Read guidance", f"results={len(payload)}"]
        for item in payload:
            linked_services = ", ".join(service["service_name"] for service in item.get("linked_services", [])) or "no linked services"
            lines.extend(
                _line_block(
                    f"{item['object_id']} | {item['title']}",
                    f"  use_now={_safe_to_use_text(approval_state=item.get('approval_state'), trust_state=item.get('trust_state'))}",
                    f"  trust={item['trust_state']} | approval={item['approval_state']} | services={linked_services}",
                    f"  next={item['posture']['trust_summary']}",
                )
            )
        return _emit_payload(lines, output_format="text")

    if args.command in {"dashboard", "health"}:
        payload = trust_dashboard(database_path=database_path)
        if output_format == "json":
            return _emit_payload(payload, output_format=output_format)
        lines = [
            "Knowledge health",
            f"objects={payload['object_count']}",
            "trust=" + ", ".join(f"{key}={value}" for key, value in sorted(payload["trust_counts"].items())),
            "approval=" + ", ".join(f"{key}={value}" for key, value in sorted(payload["approval_counts"].items())),
            "validation=" + payload["validation_posture"]["summary"],
        ]
        lines.extend(
            f"needs_attention | {item['object_id']} | trust={item['trust_state']} | approval={item['approval_state']} | next={item['posture']['trust_summary']}"
            for item in payload["queue"][: args.limit]
        )
        return _emit_payload(lines, output_format="text")

    if args.command == "object":
        payload = knowledge_object_detail(args.object_id, database_path=database_path)
        if output_format == "json":
            return _emit_payload(payload, output_format=output_format)
        current_revision = payload.get("current_revision") or {}
        audit_events = payload.get("audit_events") or []
        latest_event = audit_events[0] if audit_events else None
        lines = [
            f"{payload['object']['object_id']} | {payload['object']['title']}",
            f"use_now={_safe_to_use_text(approval_state=payload['object']['approval_state'], trust_state=payload['object']['trust_state'])}",
            f"trust={payload['object']['trust_state']} | approval={payload['object']['approval_state']} | owner={payload['object']['owner']}",
            f"last_reviewed={payload['object'].get('last_reviewed') or 'unknown'} | cadence={payload['object'].get('review_cadence') or 'unknown'}",
            "guidance=" + str(payload["posture"]["trust_summary"]),
            "detail=" + str(payload["posture"]["trust_detail"]),
        ]
        if current_revision:
            lines.append(
                "current_revision="
                + f"{current_revision['revision_id']} | state={current_revision['revision_state']} | change={current_revision.get('change_summary') or 'no change summary'}"
            )
        if latest_event:
            lines.append(
                "recent_change="
                + f"{latest_event['event_type']} at {latest_event['occurred_at']} by {latest_event['actor']}"
            )
        lines.extend(
            f"service | {service['service_name']} | {service['status']}"
            for service in payload["related_services"]
        )
        return _emit_payload(lines, output_format="text")

    if args.command == "review":
        payload = review_detail(args.object_id, args.revision_id, database_path=database_path)
        if output_format == "json":
            return _emit_payload(payload, output_format=output_format)
        preview = preview_revision_writeback(
            database_path=Path(database_path),
            object_id=args.object_id,
            revision_id=args.revision_id,
        )
        lines = [
            f"{payload['object']['object_id']} | revision={payload['revision']['revision_id']} | state={payload['revision']['revision_state']}",
            f"approval={payload['object']['approval_state']} | trust={payload['object']['trust_state']}",
            f"citations={len(payload['citations'])} | assignments={len(payload['assignments'])}",
            "writeback_preview="
            + (
                "conflict detected"
                if preview.conflict_detected
                else "ready to become canonical guidance"
            ),
            "changed_fields=" + (", ".join(preview.changed_fields) if preview.changed_fields else "none"),
            "changed_sections=" + (", ".join(preview.changed_sections) if preview.changed_sections else "none"),
        ]
        lines.extend(
            f"assignment | reviewer={assignment['reviewer']} | state={assignment['state']}"
            for assignment in payload["assignments"]
        )
        return _emit_payload(lines, output_format="text")

    if args.command in {"events", "activity"}:
        payload = event_history(
            limit=args.limit,
            entity_type=args.entity_type,
            entity_id=args.entity_id,
            event_type=args.event_type,
            database_path=database_path,
        )
        if output_format == "json":
            return _emit_payload({"events": payload}, output_format=output_format)
        lines = [
            f"{item['occurred_at']} | {item['group']} | {item['what_happened']} | affected={item['entity_type']}:{item['entity_id']} | next={item['next_action']}"
            for item in payload
        ]
        return _emit_payload(lines or ["no events found"], output_format="text")

    if args.command == "manage-queue":
        payload = manage_queue(database_path=database_path)
        if output_format == "json":
            return _emit_payload(payload, output_format=output_format)
        lines = [
            "Review and stewardship work",
            f"ready_for_review={len(payload['ready_for_review'])}",
            f"needs_decision={len(payload['needs_decision'])}",
            f"needs_revalidation={len(payload['needs_revalidation'])}",
            f"weak_evidence={len(payload['weak_evidence_items'])}",
            f"stale={len(payload['stale_items'])}",
        ]
        lines.extend(
            f"decision | {item['object_id']} | revision={item['revision_id']} | next={item['posture']['trust_summary']}"
            for item in payload["review_required"][:10]
        )
        return _emit_payload(lines, output_format="text")

    payload = validation_run_history(database_path=database_path)
    if output_format == "json":
        return _emit_payload({"validation_runs": payload}, output_format=output_format)
    lines = [
        f"{run['run_id']} | {run['run_type']} | status={run['status']} | findings={run['finding_count']}"
        for run in payload
    ]
    return _emit_payload(lines, output_format="text")
