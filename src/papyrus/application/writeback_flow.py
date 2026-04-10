from __future__ import annotations

import datetime as dt
import json
import re
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from papyrus.application.policy_authority import PolicyAuthority, policy_decision_payload
from papyrus.domain.lifecycle import RevisionReviewState, SourceSyncState
from papyrus.domain.actor import require_actor_id
from papyrus.infrastructure.markdown.serializer import slugify
from papyrus.infrastructure.markdown.writer import MarkdownWriter, SourceWriteConflictError
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    get_knowledge_object,
    get_knowledge_revision,
    load_object_schemas,
    update_knowledge_object_runtime_state,
)
from papyrus.infrastructure.transactional_mutation import MutationRecoveryError, TransactionalMutation


SECTION_PATTERN = re.compile(r"^## (?P<title>.+?)\n\n(?P<body>.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _source_sync_state(row: sqlite3.Row) -> str:
    return str(row["source_sync_state"] or SourceSyncState.NOT_REQUIRED.value)


def _revision_review_state(row: sqlite3.Row) -> str:
    return str(row["revision_review_state"] or row["revision_state"])


def _policy_authority(authority: PolicyAuthority | None) -> PolicyAuthority:
    return authority or PolicyAuthority.from_repository_policy()


def _ensure_mutation_recovery(*, source_root: Path, authority: PolicyAuthority) -> None:
    try:
        TransactionalMutation.recover_pending_mutations(
            source_root=source_root,
            authority=authority,
        )
    except MutationRecoveryError as exc:
        raise ValueError(str(exc)) from exc


def _state_change_payload(decision) -> dict[str, str]:
    return {
        "machine": str(decision.transition.machine),
        "from_state": str(decision.transition.from_state),
        "to_state": str(decision.transition.to_state),
    }


@dataclass(frozen=True)
class SourceWritebackPreview:
    object_id: str
    revision_id: str
    file_path: Path
    current_source_text: str | None
    expected_previous_text: str | None
    rendered_text: str
    previous_revision_id: str | None
    changed_fields: list[str]
    changed_sections: list[str]
    conflict_detected: bool
    conflict_reason: str | None
    source_sync_state: str
    transition: dict[str, Any]
    required_acknowledgements: tuple[str, ...]
    source_of_truth: str
    state_change: dict[str, str]
    invalidated_assumptions: tuple[str, ...]
    operator_message: str


@dataclass(frozen=True)
class SourceWritebackResult:
    object_id: str
    revision_id: str
    file_path: Path
    previous_text: str | None
    new_text: str
    backup_path: Path | None
    previous_revision_id: str | None
    changed_fields: list[str]
    changed_sections: list[str]
    changed: bool
    mutation_id: str
    source_sync_state: str
    transition: dict[str, Any]
    required_acknowledgements: tuple[str, ...]
    acknowledgements: tuple[str, ...]
    source_of_truth: str
    state_change: dict[str, str]
    invalidated_assumptions: tuple[str, ...]
    operator_message: str


@dataclass(frozen=True)
class SourceWritebackRestoreResult:
    object_id: str
    revision_id: str | None
    restored_event_id: str
    file_path: Path
    backup_path: Path | None
    restored_to_missing: bool
    mutation_id: str
    source_sync_state: str
    transition: dict[str, Any]
    required_acknowledgements: tuple[str, ...]
    acknowledgements: tuple[str, ...]
    source_of_truth: str
    state_change: dict[str, str]
    invalidated_assumptions: tuple[str, ...]
    operator_message: str


@dataclass
class PendingSourceWriteback:
    mutation: TransactionalMutation
    result: SourceWritebackResult

    def commit(self, connection: sqlite3.Connection) -> SourceWritebackResult:
        connection.commit()
        self.mutation.mark_committed()
        self.mutation.close()
        return self.result

    def rollback(self, connection: sqlite3.Connection) -> None:
        connection.rollback()
        self.mutation.rollback_files()
        self.mutation.mark_rolled_back()
        self.mutation.close()


def _ordered_metadata(metadata: dict[str, Any], object_type: str) -> dict[str, Any]:
    object_schema = load_object_schemas().get(object_type)
    if object_schema is None:
        raise ValueError(f"unsupported knowledge object type for writeback: {object_type}")

    ordered: dict[str, Any] = {}
    for field_name, field_spec in object_schema.get("fields", {}).items():
        if field_name not in metadata:
            if not bool(field_spec.get("required", False)):
                continue
            raise ValueError(f"revision payload is missing required writeback field: {field_name}")
        ordered[field_name] = metadata[field_name]

    for key in sorted(metadata):
        if key not in ordered:
            ordered[key] = metadata[key]
    return ordered


def render_revision_markdown(*, object_type: str, metadata: dict[str, Any], body_markdown: str) -> str:
    ordered_metadata = _ordered_metadata(metadata, object_type)
    front_matter = yaml.safe_dump(
        ordered_metadata,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=False,
        width=88,
    ).strip()
    body = body_markdown.strip()
    if body:
        return f"---\n{front_matter}\n---\n\n{body}\n"
    return f"---\n{front_matter}\n---\n"


def _previous_approved_revision(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    excluding_revision_id: str,
) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT revision_id, normalized_payload_json, body_markdown
        FROM knowledge_revisions
        WHERE object_id = ?
          AND revision_id != ?
          AND COALESCE(revision_review_state, revision_state) = 'approved'
        ORDER BY revision_number DESC
        LIMIT 1
        """,
        (object_id, excluding_revision_id),
    ).fetchone()


def _body_sections(body_markdown: str) -> dict[str, str]:
    return {
        match.group("title").strip(): match.group("body").strip()
        for match in SECTION_PATTERN.finditer(str(body_markdown or "").strip())
    }


def _has_prior_writeback(connection: sqlite3.Connection, *, object_id: str) -> bool:
    row = connection.execute(
        """
        SELECT 1
        FROM audit_events
        WHERE object_id = ?
          AND event_type = 'source_writeback'
        LIMIT 1
        """,
        (object_id,),
    ).fetchone()
    return row is not None


def _changed_fields(previous_metadata: dict[str, Any], current_metadata: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    for key in sorted(set(previous_metadata) | set(current_metadata)):
        if previous_metadata.get(key) != current_metadata.get(key):
            fields.append(key)
    return fields


def _changed_sections(previous_body: str, current_body: str) -> list[str]:
    previous_sections = _body_sections(previous_body)
    current_sections = _body_sections(current_body)
    changed: list[str] = []
    for title in sorted(set(previous_sections) | set(current_sections)):
        if previous_sections.get(title) != current_sections.get(title):
            changed.append(title)
    return changed


def _writeback_preview_from_connection(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    root_path: Path = ROOT,
    writer: MarkdownWriter | None = None,
    authority: PolicyAuthority | None = None,
) -> SourceWritebackPreview:
    current_authority = _policy_authority(authority)
    object_row = get_knowledge_object(connection, object_id)
    if object_row is None:
        raise ValueError(f"knowledge object not found: {object_id}")
    revision_row = get_knowledge_revision(connection, revision_id)
    if revision_row is None:
        raise ValueError(f"knowledge revision not found: {revision_id}")
    if revision_row["object_id"] != object_id:
        raise ValueError(f"revision {revision_id} does not belong to knowledge object {object_id}")

    metadata = json.loads(revision_row["normalized_payload_json"])
    markdown = render_revision_markdown(
        object_type=str(object_row["object_type"]),
        metadata=metadata,
        body_markdown=str(revision_row["body_markdown"]),
    )
    current_writer = writer or MarkdownWriter(root_path, authority=current_authority)
    file_path, current_source_text = current_writer.read_current_text(
        object_type=str(object_row["object_type"]),
        canonical_path=str(metadata.get("canonical_path") or object_row["canonical_path"]),
        object_id=object_id,
        title=str(metadata.get("title") or object_row["title"]),
    )

    previous_revision = _previous_approved_revision(
        connection,
        object_id=object_id,
        excluding_revision_id=revision_id,
    )
    expected_previous_text: str | None = None
    previous_metadata: dict[str, Any] = {}
    previous_body = ""
    previous_revision_id: str | None = None
    if previous_revision is not None:
        previous_revision_id = str(previous_revision["revision_id"])
        previous_metadata = json.loads(previous_revision["normalized_payload_json"])
        previous_body = str(previous_revision["body_markdown"])
        expected_previous_text = render_revision_markdown(
            object_type=str(object_row["object_type"]),
            metadata=previous_metadata,
            body_markdown=previous_body,
        )

    # Imported source may predate Papyrus writeback and differ from our deterministic render.
    # Until Papyrus has written the canonical file once, use the current source state itself as
    # the writeback baseline and only compare deterministic previous revisions after that point.
    expected_source_baseline = (
        expected_previous_text
        if _has_prior_writeback(connection, object_id=object_id)
        else current_source_text
    )

    conflict_detected = current_writer.would_conflict(
        current_text=current_source_text,
        expected_previous_text=expected_source_baseline,
        new_text=markdown,
    )
    conflict_reason = None
    if conflict_detected:
        conflict_reason = (
            "Canonical source changed unexpectedly relative to the last approved revision or expected empty state."
        )
    current_source_sync_state = _source_sync_state(object_row)
    decision = current_authority.require_source_sync_transition(
        current_source_sync_state,
        SourceSyncState.CONFLICTED.value if conflict_detected else SourceSyncState.APPLIED.value,
    )
    decision_payload = policy_decision_payload(decision)

    return SourceWritebackPreview(
        object_id=object_id,
        revision_id=revision_id,
        file_path=file_path,
        current_source_text=current_source_text,
        expected_previous_text=expected_source_baseline,
        rendered_text=markdown,
        previous_revision_id=previous_revision_id,
        changed_fields=_changed_fields(previous_metadata, metadata),
        changed_sections=_changed_sections(previous_body, str(revision_row["body_markdown"])),
        conflict_detected=conflict_detected,
        conflict_reason=conflict_reason,
        source_sync_state=current_source_sync_state,
        transition=decision_payload["transition"],
        required_acknowledgements=decision.required_acknowledgements,
        source_of_truth=decision.source_of_truth,
        state_change=_state_change_payload(decision),
        invalidated_assumptions=decision.invalidated_assumptions,
        operator_message=decision.operator_message,
    )


def preview_revision_writeback(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    revision_id: str,
    root_path: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> SourceWritebackPreview:
    current_authority = _policy_authority(authority)
    root_path = Path(root_path).resolve()
    _ensure_mutation_recovery(source_root=root_path, authority=current_authority)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        return _writeback_preview_from_connection(
            connection,
            object_id=object_id,
            revision_id=revision_id,
            root_path=root_path,
            authority=current_authority,
        )
    finally:
        connection.close()


def write_revision_to_source(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    actor: str,
    root_path: Path = ROOT,
    writer: MarkdownWriter | None = None,
    record_audit: bool = True,
    authority: PolicyAuthority | None = None,
    acknowledgements: list[str] | tuple[str, ...] | set[str] | None = None,
    require_acknowledgements: bool = False,
) -> SourceWritebackResult:
    pending = prepare_revision_writeback(
        connection,
        object_id=object_id,
        revision_id=revision_id,
        actor=actor,
        root_path=root_path,
        writer=writer,
        record_audit=record_audit,
        authority=authority,
        acknowledgements=acknowledgements,
        require_acknowledgements=require_acknowledgements,
    )
    try:
        return pending.commit(connection)
    except Exception:
        pending.rollback(connection)
        raise


def prepare_revision_writeback(
    connection: sqlite3.Connection,
    *,
    object_id: str,
    revision_id: str,
    actor: str,
    root_path: Path = ROOT,
    writer: MarkdownWriter | None = None,
    record_audit: bool = True,
    authority: PolicyAuthority | None = None,
    acknowledgements: list[str] | tuple[str, ...] | set[str] | None = None,
    require_acknowledgements: bool = False,
) -> PendingSourceWriteback:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    root_path = Path(root_path).resolve()
    acknowledgement_list = tuple(str(item) for item in acknowledgements or [])
    revision_row = get_knowledge_revision(connection, revision_id)
    if revision_row is None:
        raise ValueError(f"knowledge revision not found: {revision_id}")
    if revision_row["object_id"] != object_id:
        raise ValueError(f"revision {revision_id} does not belong to knowledge object {object_id}")
    if _revision_review_state(revision_row) != RevisionReviewState.APPROVED.value:
        raise ValueError(f"writeback requires an approved revision: {revision_id}")

    preview = _writeback_preview_from_connection(
        connection,
        object_id=object_id,
        revision_id=revision_id,
        root_path=root_path,
        writer=writer,
        authority=current_authority,
    )
    if require_acknowledgements and preview.required_acknowledgements:
        provided = set(acknowledgement_list)
        missing = [item for item in preview.required_acknowledgements if item not in provided]
        if missing:
            raise ValueError("missing required acknowledgements: " + ", ".join(missing))
    object_row = get_knowledge_object(connection, object_id)
    if object_row is None:
        raise ValueError(f"knowledge object not found: {object_id}")
    mutation_id = f"source-sync-{uuid.uuid4().hex[:12]}"
    if preview.conflict_detected:
        update_knowledge_object_runtime_state(
            connection,
            object_id=object_id,
            source_sync_state=SourceSyncState.CONFLICTED.value,
            source_sync_revision_id=revision_id,
            source_sync_content_hash=str(revision_row["content_hash"]),
            source_sync_mutation_id=mutation_id,
        )
        raise SourceWriteConflictError(preview.conflict_reason or f"canonical source changed unexpectedly for {object_id}")

    metadata = json.loads(revision_row["normalized_payload_json"])
    current_text = preview.current_source_text
    backup_path: Path | None = None
    if current_text is not None:
        timestamp = _now_utc().strftime("%Y%m%dT%H%M%SZ")
        backup_path = (
            current_authority.backup_root(source_root=root_path)
            / slugify(object_id)
            / f"{timestamp}-{preview.file_path.name}"
        )

    mutation = TransactionalMutation(
        source_root=root_path,
        mutation_id=mutation_id,
        mutation_type="source_sync_apply",
        object_id=object_id,
        authority=current_authority,
    ).start()
    try:
        mutation.set_metadata(
            revision_id=revision_id,
            target_path=preview.file_path.relative_to(root_path).as_posix(),
            content_hash=str(revision_row["content_hash"]),
            expected_previous_text=preview.expected_previous_text,
        )
        if backup_path is not None:
            mutation.stage_write(
                target_path=backup_path,
                previous_text=None,
                new_text=current_text,
            )
        if current_text != preview.rendered_text:
            mutation.stage_write(
                target_path=preview.file_path,
                previous_text=current_text,
                new_text=preview.rendered_text,
            )
        update_knowledge_object_runtime_state(
            connection,
            object_id=object_id,
            source_sync_state=SourceSyncState.APPLIED.value,
            source_sync_revision_id=revision_id,
            source_sync_content_hash=str(revision_row["content_hash"]),
            source_sync_mutation_id=mutation_id,
        )

        if record_audit:
            insert_audit_event(
                connection,
                event_id=_event_id("source-writeback"),
                event_type="source_writeback",
                occurred_at=_now_utc().isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json.dumps(
                    {
                        "file_path": str(metadata.get("canonical_path") or object_row["canonical_path"]),
                        "backup_path": (
                            backup_path.relative_to(root_path).as_posix()
                            if backup_path is not None
                            else None
                        ),
                        "previous_revision_id": preview.previous_revision_id,
                        "changed": current_text != preview.rendered_text,
                        "changed_fields": preview.changed_fields,
                        "changed_sections": preview.changed_sections,
                        "mutation_id": mutation_id,
                        "source_sync_state": SourceSyncState.APPLIED.value,
                        "transition": preview.transition,
                        "required_acknowledgements": list(preview.required_acknowledgements),
                        "acknowledgements": list(acknowledgement_list),
                        "source_of_truth": preview.source_of_truth,
                        "state_change": preview.state_change,
                        "invalidated_assumptions": list(preview.invalidated_assumptions),
                        "operator_message": preview.operator_message,
                        "policy_decision": {
                            "allowed": True,
                            "required_acknowledgements": list(preview.required_acknowledgements),
                            "source_of_truth": preview.source_of_truth,
                            "transition": preview.transition,
                            "invalidated_assumptions": list(preview.invalidated_assumptions),
                            "operator_message": preview.operator_message,
                        },
                    },
                    sort_keys=True,
                    ensure_ascii=True,
                ),
            )

        mutation.apply_files()
    except Exception:
        mutation.rollback_files()
        mutation.mark_rolled_back()
        mutation.close()
        raise

    return PendingSourceWriteback(
        mutation=mutation,
        result=SourceWritebackResult(
            object_id=object_id,
            revision_id=revision_id,
            file_path=preview.file_path,
            previous_text=current_text,
            new_text=preview.rendered_text,
            backup_path=backup_path,
            previous_revision_id=preview.previous_revision_id,
            changed_fields=preview.changed_fields,
            changed_sections=preview.changed_sections,
            changed=current_text != preview.rendered_text,
            mutation_id=mutation_id,
            source_sync_state=SourceSyncState.APPLIED.value,
            transition=preview.transition,
            required_acknowledgements=preview.required_acknowledgements,
            acknowledgements=acknowledgement_list,
            source_of_truth=preview.source_of_truth,
            state_change=preview.state_change,
            invalidated_assumptions=preview.invalidated_assumptions,
            operator_message=preview.operator_message,
        )
    )


def write_object_to_source(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    root_path: Path = ROOT,
    authority: PolicyAuthority | None = None,
    acknowledgements: list[str] | tuple[str, ...] | set[str] | None = None,
) -> SourceWritebackResult:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    root_path = Path(root_path).resolve()
    _ensure_mutation_recovery(source_root=root_path, authority=current_authority)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        revision_id = str(object_row["current_revision_id"] or "").strip()
        if not revision_id:
            raise ValueError(f"knowledge object has no current revision: {object_id}")
        result = write_revision_to_source(
            connection,
            object_id=object_id,
            revision_id=revision_id,
            actor=actor,
            root_path=root_path,
            authority=current_authority,
            acknowledgements=acknowledgements,
            require_acknowledgements=True,
        )
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def write_all_approved_revisions(
    *,
    database_path: Path = DB_PATH,
    actor: str,
    root_path: Path = ROOT,
    authority: PolicyAuthority | None = None,
) -> list[SourceWritebackResult]:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    root_path = Path(root_path).resolve()
    _ensure_mutation_recovery(source_root=root_path, authority=current_authority)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    pending_results: list[PendingSourceWriteback] = []
    try:
        rows = connection.execute(
            """
            SELECT o.object_id, o.current_revision_id
            FROM knowledge_objects AS o
            JOIN knowledge_revisions AS r ON r.revision_id = o.current_revision_id
            WHERE COALESCE(r.revision_review_state, r.revision_state) = 'approved'
            ORDER BY o.object_id
            """
        ).fetchall()
        for row in rows:
            pending_results.append(
                prepare_revision_writeback(
                    connection,
                    object_id=str(row["object_id"]),
                    revision_id=str(row["current_revision_id"]),
                    actor=actor,
                    root_path=root_path,
                    authority=current_authority,
                )
            )
        connection.commit()
        committed_results: list[SourceWritebackResult] = []
        for pending in pending_results:
            pending.mutation.mark_committed()
            pending.mutation.close()
            committed_results.append(pending.result)
        return committed_results
    except Exception:
        for pending in reversed(pending_results):
            pending.rollback(connection)
        connection.rollback()
        raise
    finally:
        connection.close()


def restore_last_writeback(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    revision_id: str | None = None,
    root_path: Path = ROOT,
    authority: PolicyAuthority | None = None,
    acknowledgements: list[str] | tuple[str, ...] | set[str] | None = None,
) -> SourceWritebackRestoreResult:
    current_authority = _policy_authority(authority)
    actor = require_actor_id(actor)
    root_path = Path(root_path).resolve()
    _ensure_mutation_recovery(source_root=root_path, authority=current_authority)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    try:
        acknowledgement_list = tuple(str(item) for item in acknowledgements or [])
        object_row = get_knowledge_object(connection, object_id)
        if object_row is None:
            raise ValueError(f"knowledge object not found: {object_id}")

        row = connection.execute(
            """
            SELECT event_id, revision_id, details_json
            FROM audit_events
            WHERE object_id = ?
              AND event_type = 'source_writeback'
              AND (? IS NULL OR revision_id = ?)
            ORDER BY occurred_at DESC, rowid DESC
            LIMIT 1
            """,
            (object_id, revision_id, revision_id),
        ).fetchone()
        if row is None:
            qualifier = f" revision {revision_id}" if revision_id else ""
            raise ValueError(f"no writeback audit event found for {object_id}{qualifier}")

        details = json.loads(str(row["details_json"]) or "{}")
        if not bool(details.get("changed", True)):
            raise ValueError(f"latest writeback for {object_id} did not change canonical source")

        file_path = (root_path / str(details.get("file_path") or object_row["canonical_path"])).resolve()
        backup_path: Path | None = None
        previous_text: str | None = None
        backup_rel = str(details.get("backup_path") or "").strip()
        if backup_rel:
            backup_path = (root_path / backup_rel).resolve()
            if not backup_path.exists():
                raise ValueError(f"writeback backup is missing for {object_id}: {backup_path}")
            previous_text = backup_path.read_text(encoding="utf-8")
        current_text = file_path.read_text(encoding="utf-8") if file_path.exists() else None
        mutation_id = f"source-sync-restore-{uuid.uuid4().hex[:12]}"
        decision = current_authority.require_source_sync_transition(
            _source_sync_state(object_row),
            SourceSyncState.RESTORED.value,
        )
        current_authority.assert_acknowledgements(decision, acknowledgement_list)
        decision_payload = policy_decision_payload(decision)
        restore_backup_path: Path | None = None
        if current_text is not None:
            timestamp = _now_utc().strftime("%Y%m%dT%H%M%SZ")
            restore_backup_path = (
                current_authority.backup_root(source_root=root_path)
                / slugify(object_id)
                / f"{timestamp}-restore-{file_path.name}"
            )
        with TransactionalMutation(
            source_root=root_path,
            mutation_id=mutation_id,
            mutation_type="source_sync_restore",
            object_id=object_id,
            authority=current_authority,
        ) as mutation:
            mutation.set_metadata(
                restored_from_event_id=str(row["event_id"]),
                target_path=file_path.relative_to(root_path).as_posix(),
                previous_backup_path=backup_rel or None,
            )
            if restore_backup_path is not None:
                mutation.stage_write(
                    target_path=restore_backup_path,
                    previous_text=None,
                    new_text=current_text,
                )
            if previous_text is None:
                mutation.stage_delete(target_path=file_path, previous_text=current_text)
            else:
                mutation.stage_write(target_path=file_path, previous_text=current_text, new_text=previous_text)
            mutation.execute(
                connection=connection,
                mutate=lambda _: update_knowledge_object_runtime_state(
                    connection,
                    object_id=object_id,
                    source_sync_state=SourceSyncState.RESTORED.value,
                    source_sync_revision_id=str(row["revision_id"]) if row["revision_id"] is not None else None,
                    source_sync_mutation_id=mutation_id,
                ),
            )
        restored_event_id = _event_id("source-writeback-restored")
        insert_audit_event(
            connection,
            event_id=restored_event_id,
            event_type="source_writeback_restored",
            occurred_at=_now_utc().isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=str(row["revision_id"]) if row["revision_id"] is not None else None,
            details_json=json.dumps(
                {
                    "restored_from_event_id": str(row["event_id"]),
                    "file_path": file_path.relative_to(root_path).as_posix(),
                    "backup_path": backup_rel or None,
                    "restored_to_missing": previous_text is None,
                    "mutation_id": mutation_id,
                    "source_sync_state": SourceSyncState.RESTORED.value,
                    "transition": decision_payload["transition"],
                    "required_acknowledgements": list(decision.required_acknowledgements),
                    "acknowledgements": list(acknowledgement_list),
                    "source_of_truth": decision.source_of_truth,
                    "state_change": _state_change_payload(decision),
                    "invalidated_assumptions": list(decision.invalidated_assumptions),
                    "operator_message": decision.operator_message,
                    "policy_decision": decision_payload,
                },
                sort_keys=True,
                ensure_ascii=True,
            ),
        )
        connection.commit()
        return SourceWritebackRestoreResult(
            object_id=object_id,
            revision_id=str(row["revision_id"]) if row["revision_id"] is not None else None,
            restored_event_id=restored_event_id,
            file_path=file_path,
            backup_path=backup_path,
            restored_to_missing=previous_text is None,
            mutation_id=mutation_id,
            source_sync_state=SourceSyncState.RESTORED.value,
            transition=decision_payload["transition"],
            required_acknowledgements=decision.required_acknowledgements,
            acknowledgements=acknowledgement_list,
            source_of_truth=decision.source_of_truth,
            state_change=_state_change_payload(decision),
            invalidated_assumptions=decision.invalidated_assumptions,
            operator_message=decision.operator_message,
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
