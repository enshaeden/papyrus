from __future__ import annotations

import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

from papyrus.application.authoring_flow import create_draft_from_blueprint, update_section, validate_draft_progress
from papyrus.application.commands import (
    archive_object_command,
    approve_revision_command,
    assign_reviewer_command,
    create_object_command,
    mark_object_suspect_due_to_change_command,
    reject_revision_command,
    restore_writeback_command,
    submit_for_review_command,
    supersede_object_command,
    writeback_object_command,
)
from papyrus.application.ingestion_flow import ingest_file, ingestion_detail, list_ingestions
from papyrus.application.mapping_flow import convert_to_draft
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
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.knowledge_repo import load_policy
from papyrus.interfaces.startup_guard import resolve_operator_source_root


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
            f"{row.object_id} | {row.title} | {row.content_type} | {row.object_lifecycle_state} | "
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


def _parse_field_assignments(assignments: list[str]) -> dict[str, object]:
    values: dict[str, object] = {}
    for assignment in assignments:
        if "=" not in assignment:
            raise ValueError(f"field assignment must use name=value syntax: {assignment}")
        name, raw_value = assignment.split("=", 1)
        if "|" in raw_value:
            values[name] = [item.strip() for item in raw_value.split("|") if item.strip()]
        else:
            values[name] = raw_value
    return values


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
    common.add_argument(
        "--source-root",
        default=str(ROOT),
        help="Canonical source root for governed writeback, previews, and draft validation.",
    )
    common.add_argument(
        "--allow-noncanonical-source-root",
        action="store_true",
        help="Allow a non-repository source root for sandboxed authoring or test workflows.",
    )
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

    create_draft_parser = subparsers.add_parser("create-draft", help="Create a structured draft from a blueprint.", parents=[common])
    create_draft_parser.add_argument("--type", required=True, dest="blueprint_id", help="Blueprint ID.")
    create_draft_parser.add_argument("--object-id", required=True, help="Knowledge object ID.")
    create_draft_parser.add_argument("--title", required=True, help="Title.")
    create_draft_parser.add_argument("--summary", required=True, help="Summary.")
    create_draft_parser.add_argument("--owner", required=True, help="Owner.")
    create_draft_parser.add_argument("--team", required=True, help="Team.")
    create_draft_parser.add_argument("--canonical-path", required=True, help="Canonical Markdown path.")
    create_draft_parser.add_argument("--review-cadence", default="quarterly", help="Review cadence.")
    create_draft_parser.add_argument("--status", default="draft", help="Lifecycle status.")
    create_draft_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    edit_section_parser = subparsers.add_parser("edit-section", help="Update one structured draft section.", parents=[common])
    edit_section_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    edit_section_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")
    edit_section_parser.add_argument("--section", required=True, help="Blueprint section ID.")
    edit_section_parser.add_argument("--field", action="append", default=[], help="Field assignment in name=value form. Use a|b|c for list values.")
    edit_section_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    submit_review_parser = subparsers.add_parser("submit-review", help="Submit a draft revision for review.", parents=[common])
    submit_review_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    submit_review_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")
    submit_review_parser.add_argument("--notes", default=None, help="Optional submission notes.")
    submit_review_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    assign_review_parser = subparsers.add_parser("assign-reviewer", help="Assign a reviewer to an in-review revision.", parents=[common])
    assign_review_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    assign_review_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")
    assign_review_parser.add_argument("--reviewer", required=True, help="Reviewer identifier.")
    assign_review_parser.add_argument("--due-at", default=None, help="Optional ISO timestamp.")
    assign_review_parser.add_argument("--notes", default=None, help="Optional assignment notes.")
    assign_review_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    approve_review_parser = subparsers.add_parser("approve-review", help="Approve an in-review revision.", parents=[common])
    approve_review_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    approve_review_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")
    approve_review_parser.add_argument("--reviewer", required=True, help="Reviewer identifier.")
    approve_review_parser.add_argument("--notes", default=None, help="Optional approval notes.")
    approve_review_parser.add_argument("--actor", default="local.reviewer", help="Actor for the governed change.")

    reject_review_parser = subparsers.add_parser("reject-review", help="Reject an in-review revision.", parents=[common])
    reject_review_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    reject_review_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")
    reject_review_parser.add_argument("--reviewer", required=True, help="Reviewer identifier.")
    reject_review_parser.add_argument("--notes", required=True, help="Rejection notes.")
    reject_review_parser.add_argument("--actor", default="local.reviewer", help="Actor for the governed change.")

    supersede_parser = subparsers.add_parser("supersede-object", help="Deprecate an object in favor of a replacement.", parents=[common])
    supersede_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    supersede_parser.add_argument("--replacement", required=True, dest="replacement_object_id", help="Replacement object ID.")
    supersede_parser.add_argument("--notes", default=None, help="Optional supersede notes.")
    supersede_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    archive_parser = subparsers.add_parser("archive-object", help="Archive a deprecated object and move its canonical file under archive/knowledge/.", parents=[common])
    archive_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    archive_parser.add_argument("--retirement-reason", required=True, help="Required rationale for archival.")
    archive_parser.add_argument("--notes", default=None, help="Optional operator notes for the archive action.")
    archive_parser.add_argument("--ack", action="append", default=[], help="Required acknowledgement token. Repeat for multiple acknowledgements.")
    archive_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    suspect_parser = subparsers.add_parser("mark-suspect", help="Mark an object suspect due to a change event.", parents=[common])
    suspect_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    suspect_parser.add_argument("--reason", required=True, help="Reason for suspect posture.")
    suspect_parser.add_argument("--changed-entity-type", required=True, help="Changed entity type.")
    suspect_parser.add_argument("--changed-entity-id", default=None, help="Optional changed entity ID.")
    suspect_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    show_progress_parser = subparsers.add_parser("show-progress", help="Show structured draft completion state.", parents=[common])
    show_progress_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    show_progress_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")

    subparsers.add_parser("list-ingestions", help="List ingestion jobs.", parents=[common])

    review_ingestion_parser = subparsers.add_parser("review-ingestion", help="Show ingestion job detail.", parents=[common])
    review_ingestion_parser.add_argument("ingestion_id", help="Ingestion job ID.")

    convert_ingestion_parser = subparsers.add_parser("convert-ingestion", help="Convert an ingestion into a structured draft.", parents=[common])
    convert_ingestion_parser.add_argument("ingestion_id", help="Ingestion job ID.")
    convert_ingestion_parser.add_argument("--object-id", required=True, help="Knowledge object ID.")
    convert_ingestion_parser.add_argument("--title", required=True, help="Draft title.")
    convert_ingestion_parser.add_argument("--canonical-path", required=True, help="Canonical Markdown path.")
    convert_ingestion_parser.add_argument("--owner", required=True, help="Owner.")
    convert_ingestion_parser.add_argument("--team", required=True, help="Team.")
    convert_ingestion_parser.add_argument("--review-cadence", default="quarterly", help="Review cadence.")
    convert_ingestion_parser.add_argument("--status", default="draft", help="Lifecycle status.")
    convert_ingestion_parser.add_argument("--audience", default="service_desk", help="Audience.")
    convert_ingestion_parser.add_argument("--actor", default="local.operator", help="Actor.")

    preview_sync_parser = subparsers.add_parser("preview-source-sync", help="Preview canonical source sync for a revision.", parents=[common])
    preview_sync_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    preview_sync_parser.add_argument("--revision", required=True, dest="revision_id", help="Revision ID.")

    apply_sync_parser = subparsers.add_parser("apply-source-sync", help="Apply canonical source sync for the current approved revision.", parents=[common])
    apply_sync_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    apply_sync_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    restore_sync_parser = subparsers.add_parser("restore-source-sync", help="Restore the last canonical source sync.", parents=[common])
    restore_sync_parser.add_argument("--object", required=True, dest="object_id", help="Knowledge object ID.")
    restore_sync_parser.add_argument("--revision", default=None, dest="revision_id", help="Optional revision ID.")
    restore_sync_parser.add_argument("--actor", default="local.operator", help="Actor for the governed change.")

    args = parser.parse_args()
    database_path = args.db or str(DB_PATH)
    output_format = args.format or "text"
    try:
        source_root = resolve_operator_source_root(
            args.source_root,
            allow_noncanonical=args.allow_noncanonical_source_root,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

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

    if args.command == "create-draft":
        create_object_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            object_type=args.blueprint_id,
            title=args.title,
            summary=args.summary,
            owner=args.owner,
            team=args.team,
            canonical_path=args.canonical_path,
            review_cadence=args.review_cadence,
            status=args.status,
            actor=args.actor,
        )
        created = create_draft_from_blueprint(
            object_id=args.object_id,
            blueprint_id=args.blueprint_id,
            actor=args.actor,
            database_path=Path(database_path),
            source_root=source_root,
        )
        return _emit_payload(
            {
                "object_id": args.object_id,
                "revision_id": created["revision_id"],
                "completion": created["completion"],
            },
            output_format=output_format,
        )

    if args.command == "edit-section":
        updated = update_section(
            object_id=args.object_id,
            revision_id=args.revision_id,
            section_id=args.section,
            values=_parse_field_assignments(args.field),
            actor=args.actor,
            database_path=Path(database_path),
            source_root=source_root,
        )
        return _emit_payload(
            {
                "object_id": args.object_id,
                "revision_id": args.revision_id,
                "completion": updated["completion"],
            },
            output_format=output_format,
        )

    if args.command == "submit-review":
        result = submit_for_review_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            revision_id=args.revision_id,
            actor=args.actor,
            notes=args.notes,
        )
        return _emit_payload(
            {
                "object_id": args.object_id,
                "revision_id": args.revision_id,
                "event_type": result.event.event_type,
                "details": result.event.details,
            },
            output_format=output_format,
        )

    if args.command == "assign-reviewer":
        due_at = dt.datetime.fromisoformat(args.due_at) if args.due_at else None
        assignment = assign_reviewer_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            revision_id=args.revision_id,
            reviewer=args.reviewer,
            actor=args.actor,
            due_at=due_at,
            notes=args.notes,
        )
        return _emit_payload(
            {
                "object_id": args.object_id,
                "revision_id": args.revision_id,
                "assignment_id": assignment.assignment_id,
                "reviewer": assignment.reviewer,
                "state": assignment.state,
            },
            output_format=output_format,
        )

    if args.command == "approve-review":
        approved = approve_revision_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            revision_id=args.revision_id,
            reviewer=args.reviewer,
            actor=args.actor,
            notes=args.notes,
        )
        return _emit_payload(
            {
                "object_id": approved.object_id,
                "revision_id": approved.revision_id,
                "revision_review_state": approved.state,
            },
            output_format=output_format,
        )

    if args.command == "reject-review":
        rejected = reject_revision_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            revision_id=args.revision_id,
            reviewer=args.reviewer,
            actor=args.actor,
            notes=args.notes,
        )
        return _emit_payload(
            {
                "object_id": rejected.object_id,
                "revision_id": rejected.revision_id,
                "revision_review_state": rejected.state,
            },
            output_format=output_format,
        )

    if args.command == "supersede-object":
        result = supersede_object_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            replacement_object_id=args.replacement_object_id,
            actor=args.actor,
            notes=args.notes,
        )
        return _emit_payload(
            {
                "object_id": result.object_id,
                "object_lifecycle_state": result.status,
                "replacement_object_id": args.replacement_object_id,
            },
            output_format=output_format,
        )

    if args.command == "archive-object":
        result = archive_object_command(
            database_path=Path(database_path),
            source_root=source_root,
            object_id=args.object_id,
            actor=args.actor,
            retirement_reason=args.retirement_reason,
            notes=args.notes,
            acknowledgements=args.ack,
        )
        return _emit_payload(
            {
                "object_id": result.object_id,
                "revision_id": result.revision_id,
                "previous_canonical_path": result.previous_canonical_path,
                "archived_canonical_path": result.archived_canonical_path,
                "backup_path": str(result.backup_path) if result.backup_path is not None else None,
                "mutation_id": result.mutation_id,
                "object_lifecycle_state": result.object_lifecycle_state,
                "required_acknowledgements": list(result.required_acknowledgements),
                "source_of_truth": result.source_of_truth,
                "state_change": result.state_change,
                "invalidated_assumptions": list(result.invalidated_assumptions),
                "operator_message": result.operator_message,
            },
            output_format=output_format,
        )

    if args.command == "mark-suspect":
        result = mark_object_suspect_due_to_change_command(
            database_path=Path(database_path),
            object_id=args.object_id,
            actor=args.actor,
            reason=args.reason,
            changed_entity_type=args.changed_entity_type,
            changed_entity_id=args.changed_entity_id,
        )
        return _emit_payload(
            {
                "object_id": args.object_id,
                "event_type": result.event.event_type,
                "details": result.event.details,
            },
            output_format=output_format,
        )

    if args.command == "show-progress":
        payload = validate_draft_progress(
            object_id=args.object_id,
            revision_id=args.revision_id,
            database_path=Path(database_path),
            source_root=source_root,
        )
        return _emit_payload(payload, output_format=output_format)

    if args.command == "list-ingestions":
        return _emit_payload({"ingestions": list_ingestions(database_path=Path(database_path))}, output_format=output_format)

    if args.command == "review-ingestion":
        return _emit_payload(
            ingestion_detail(ingestion_id=args.ingestion_id, database_path=Path(database_path)),
            output_format=output_format,
        )

    if args.command == "convert-ingestion":
        payload = convert_to_draft(
            ingestion_id=args.ingestion_id,
            object_id=args.object_id,
            title=args.title,
            canonical_path=args.canonical_path,
            owner=args.owner,
            team=args.team,
            review_cadence=args.review_cadence,
            status=args.status,
            audience=args.audience,
            actor=args.actor,
            database_path=Path(database_path),
            source_root=source_root,
        )
        return _emit_payload(payload, output_format=output_format)

    if args.command == "preview-source-sync":
        preview = preview_revision_writeback(
            database_path=Path(database_path),
            object_id=args.object_id,
            revision_id=args.revision_id,
            root_path=source_root,
        )
        return _emit_payload(
            {
                "object_id": preview.object_id,
                "revision_id": preview.revision_id,
                "file_path": str(preview.file_path),
                "changed_fields": preview.changed_fields,
                "changed_sections": preview.changed_sections,
                "conflict_detected": preview.conflict_detected,
                "source_sync_state": preview.source_sync_state,
                "required_acknowledgements": list(preview.required_acknowledgements),
                "source_of_truth": preview.source_of_truth,
                "state_change": preview.state_change,
                "invalidated_assumptions": list(preview.invalidated_assumptions),
                "operator_message": preview.operator_message,
            },
            output_format=output_format,
        )

    if args.command == "apply-source-sync":
        result = writeback_object_command(
            database_path=Path(database_path),
            object_id=args.object_id,
            actor=args.actor,
            source_root=source_root,
        )
        return _emit_payload(
            {
                "object_id": result.object_id,
                "revision_id": result.revision_id,
                "file_path": str(result.file_path),
                "mutation_id": result.mutation_id,
                "source_sync_state": result.source_sync_state,
                "required_acknowledgements": list(result.required_acknowledgements),
                "source_of_truth": result.source_of_truth,
                "state_change": result.state_change,
                "invalidated_assumptions": list(result.invalidated_assumptions),
                "operator_message": result.operator_message,
            },
            output_format=output_format,
        )

    if args.command == "restore-source-sync":
        result = restore_writeback_command(
            database_path=Path(database_path),
            object_id=args.object_id,
            actor=args.actor,
            revision_id=args.revision_id,
            source_root=source_root,
        )
        return _emit_payload(
            {
                "object_id": result.object_id,
                "revision_id": result.revision_id,
                "file_path": str(result.file_path),
                "restored_event_id": result.restored_event_id,
                "backup_path": str(result.backup_path) if result.backup_path is not None else None,
                "restored_to_missing": result.restored_to_missing,
                "mutation_id": result.mutation_id,
                "source_sync_state": result.source_sync_state,
                "required_acknowledgements": list(result.required_acknowledgements),
                "source_of_truth": result.source_of_truth,
                "state_change": result.state_change,
                "invalidated_assumptions": list(result.invalidated_assumptions),
                "operator_message": result.operator_message,
            },
            output_format=output_format,
        )

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
                + f"{current_revision['revision_id']} | state={current_revision['revision_review_state']} | change={current_revision.get('change_summary') or 'no change summary'}"
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
            root_path=source_root,
        )
        lines = [
            f"{payload['object']['object_id']} | revision={payload['revision']['revision_id']} | state={payload['revision']['revision_review_state']}",
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
