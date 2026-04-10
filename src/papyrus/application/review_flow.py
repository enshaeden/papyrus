from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from papyrus.application.revision_runtime import RevisionRuntimeServices
from papyrus.application import writeback_flow
from papyrus.application.policy_authority import PolicyAuthority, policy_decision_payload
from papyrus.domain.actor import require_actor_id
from papyrus.domain.entities import AuditEvent, KnowledgeObject, KnowledgeRevision, ReviewAssignment
from papyrus.domain.lifecycle import (
    DraftProgressState,
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
)
from papyrus.domain.policies import runtime_trust_state
from papyrus.domain.value_objects import (
    KnowledgeLifecycleStatus,
    ReviewAssignmentState,
    RevisionReviewStatus,
    TrustState,
)
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.serializer import json_dump, slugify
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    find_revision_by_content_hash,
    get_knowledge_object,
    get_knowledge_revision,
    next_revision_number,
    upsert_knowledge_object,
    upsert_relationship,
    update_knowledge_object_runtime_state,
    update_knowledge_revision_content,
    update_knowledge_revision_state,
    insert_knowledge_revision,
)
from papyrus.infrastructure.repositories.review_repo import (
    get_review_assignment,
    insert_review_assignment,
    list_review_assignments_for_revision,
    update_review_assignment,
)
from papyrus.infrastructure.search.indexer import fts5_available
from papyrus.infrastructure.transactional_mutation import MutationRecoveryError, TransactionalMutation
from papyrus.application.runtime_projection import persist_revision_artifacts


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _content_hash(normalized_payload_json: str, body_markdown: str) -> str:
    return hashlib.sha256(f"{normalized_payload_json}\n{body_markdown}".encode("utf-8")).hexdigest()


def _relationship_id(source_type: str, source_id: str, target_type: str, target_id: str, rel_type: str) -> str:
    return hashlib.sha256(f"{source_type}|{source_id}|{target_type}|{target_id}|{rel_type}".encode("utf-8")).hexdigest()[:24]


def _archive_canonical_path(canonical_path: str) -> str:
    normalized = canonical_path.strip().replace("\\", "/")
    if normalized.startswith("archive/knowledge/"):
        raise ValueError("knowledge object is already archived")
    if not normalized.startswith("knowledge/"):
        raise ValueError("archive requires a canonical path under knowledge/")
    return f"archive/{normalized}"


def _object_lifecycle_state(row: sqlite3.Row) -> str:
    return str(row["object_lifecycle_state"])


def _revision_review_state(row: sqlite3.Row) -> str:
    return str(row["revision_review_state"])


def _draft_progress_state(row: sqlite3.Row) -> str:
    return str(row["draft_progress_state"] or DraftProgressState.READY_FOR_REVIEW.value)


def _source_sync_state(row: sqlite3.Row) -> str:
    return str(row["source_sync_state"] or SourceSyncState.NOT_REQUIRED.value)


def _ensure_mutation_recovery(*, source_root: Path, authority: PolicyAuthority) -> None:
    try:
        TransactionalMutation.recover_pending_mutations(
            source_root=source_root,
            authority=authority,
        )
    except MutationRecoveryError as exc:
        raise ValueError(str(exc)) from exc


def _row_to_object(row: sqlite3.Row) -> KnowledgeObject:
    return KnowledgeObject(
        object_id=row["object_id"],
        object_type=row["object_type"],
        title=row["title"],
        object_lifecycle_state=_object_lifecycle_state(row),
        owner=row["owner"],
        team=row["team"],
        canonical_path=row["canonical_path"],
    )


def _row_to_revision(row: sqlite3.Row) -> KnowledgeRevision:
    return KnowledgeRevision(
        revision_id=row["revision_id"],
        object_id=row["object_id"],
        revision_number=row["revision_number"],
        state=_revision_review_state(row),
    )


def _row_to_assignment(row: sqlite3.Row) -> ReviewAssignment:
    return ReviewAssignment(
        assignment_id=row["assignment_id"],
        object_id=row["object_id"],
        revision_id=row["revision_id"],
        reviewer=row["reviewer"],
        state=row["state"],
        assigned_at=dt.datetime.fromisoformat(row["assigned_at"]) if row["assigned_at"] else None,
        due_at=dt.datetime.fromisoformat(row["due_at"]) if row["due_at"] else None,
        notes=row["notes"],
    )


def _audit_event(
    *,
    event_id: str,
    event_type: str,
    occurred_at: dt.datetime,
    actor: str,
    object_id: str | None,
    revision_id: str | None,
    details: dict[str, Any],
) -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        event_type=event_type,
        occurred_at=occurred_at,
        actor=actor,
        object_id=object_id,
        revision_id=revision_id,
        details=details,
    )


def _revision_author_actor(connection: sqlite3.Connection, revision_id: str) -> str | None:
    row = connection.execute(
        """
        SELECT actor
        FROM audit_events
        WHERE revision_id = ? AND event_type = 'revision_created'
        ORDER BY occurred_at ASC
        LIMIT 1
        """,
        (revision_id,),
    ).fetchone()
    if row is None:
        return None
    return str(row["actor"]).strip() or None


class GovernanceWorkflow:
    def __init__(
        self,
        database_path: Path = DB_PATH,
        source_root: Path = ROOT,
        *,
        authority: PolicyAuthority | None = None,
    ):
        self.database_path = Path(database_path)
        self.source_root = Path(source_root).resolve()
        self.runtime = RevisionRuntimeServices(source_root=self.source_root)
        self.authority = authority or PolicyAuthority.from_repository_policy()
        _ensure_mutation_recovery(source_root=self.source_root, authority=self.authority)

    def _connection(self) -> sqlite3.Connection:
        connection = open_runtime_database(self.database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
        apply_runtime_schema(connection, has_fts5=fts5_available(connection))
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
        )
        return connection

    def _require_object(self, connection: sqlite3.Connection, object_id: str) -> sqlite3.Row:
        row = get_knowledge_object(connection, object_id)
        if row is None:
            raise ValueError(f"knowledge object not found: {object_id}")
        return row

    def _require_revision(
        self,
        connection: sqlite3.Connection,
        *,
        object_id: str,
        revision_id: str,
    ) -> sqlite3.Row:
        row = get_knowledge_revision(connection, revision_id)
        if row is None:
            raise ValueError(f"revision not found: {revision_id}")
        if row["object_id"] != object_id:
            raise ValueError(f"revision {revision_id} does not belong to knowledge object {object_id}")
        return row

    def _require_assignment(
        self,
        connection: sqlite3.Connection,
        *,
        revision_id: str,
        reviewer: str,
    ) -> sqlite3.Row:
        assignments = list_review_assignments_for_revision(connection, revision_id)
        for assignment in reversed(assignments):
            if assignment["reviewer"] == reviewer and assignment["state"] == ReviewAssignmentState.ASSIGNED.value:
                return assignment
        raise ValueError(f"no active review assignment for reviewer {reviewer} on revision {revision_id}")

    def create_object(
        self,
        *,
        object_id: str,
        object_type: str,
        title: str,
        summary: str,
        owner: str,
        team: str,
        canonical_path: str,
        actor: str,
        object_lifecycle_state: str = KnowledgeLifecycleStatus.DRAFT.value,
        source_type: str = "native",
        source_system: str = "repository",
        source_title: str | None = None,
        review_cadence: str = "after_change",
        legacy_type: str | None = None,
        tags: list[str] | None = None,
        systems: list[str] | None = None,
    ) -> KnowledgeObject:
        actor = require_actor_id(actor)
        now = _now_utc()
        connection = self._connection()
        try:
            if get_knowledge_object(connection, object_id) is not None:
                raise ValueError(f"knowledge object already exists: {object_id}")
            self.authority.validate_canonical_repo_relative_path(canonical_path)
            ObjectLifecycleState(object_lifecycle_state)

            upsert_knowledge_object(
                connection,
                object_id=object_id,
                object_type=object_type,
                legacy_type=legacy_type,
                title=title,
                summary=summary,
                object_lifecycle_state=object_lifecycle_state,
                owner=owner,
                team=team,
                canonical_path=canonical_path,
                source_type=source_type,
                source_system=source_system,
                source_title=source_title or title,
                created_date=now.date().isoformat(),
                updated_date=now.date().isoformat(),
                last_reviewed=now.date().isoformat(),
                review_cadence=review_cadence,
                trust_state=TrustState.SUSPECT.value,
                source_sync_state=SourceSyncState.NOT_REQUIRED.value,
                current_revision_id=None,
                tags_json=json_dump(tags or []),
                systems_json=json_dump(systems or []),
            )
            event_id = _event_id("object-created")
            details = {
                "object_type": object_type,
                "canonical_path": canonical_path,
                "object_lifecycle_state": object_lifecycle_state,
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="object_created",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=None,
                details_json=json_dump(details),
            )
            connection.commit()
            return _row_to_object(self._require_object(connection, object_id))
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def create_revision(
        self,
        *,
        object_id: str,
        normalized_payload: dict[str, Any],
        body_markdown: str,
        actor: str,
        legacy_metadata: dict[str, Any] | None = None,
        change_summary: str | None = None,
    ) -> KnowledgeRevision:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            object_row = self._require_object(connection, object_id)
            parsed = self.runtime.parse_revision(normalized_payload, body_markdown)
            if str(parsed.metadata["id"]) != object_id:
                raise ValueError(f"revision payload id does not match knowledge object {object_id}")
            if parsed.object_type != object_row["object_type"]:
                raise ValueError(
                    f"revision payload type {parsed.object_type} does not match knowledge object type {object_row['object_type']}"
                )

            normalized_payload_json = json_dump(parsed.metadata)
            content_hash = _content_hash(normalized_payload_json, body_markdown)
            duplicate = find_revision_by_content_hash(connection, object_id, content_hash)
            if duplicate is not None:
                raise ValueError(f"revision content already exists for knowledge object {object_id}")

            revision_number = next_revision_number(connection, object_id)
            revision_id = f"{object_id}-rev-{content_hash[:12]}"
            insert_knowledge_revision(
                connection,
                revision_id=revision_id,
                object_id=object_id,
                revision_number=revision_number,
                revision_review_state=RevisionReviewState.DRAFT.value,
                draft_progress_state=DraftProgressState.READY_FOR_REVIEW.value,
                source_path=str(parsed.metadata["canonical_path"]),
                content_hash=content_hash,
                body_markdown=body_markdown,
                normalized_payload_json=normalized_payload_json,
                legacy_metadata_json=json_dump(legacy_metadata or {}),
                imported_at=now.isoformat(),
                change_summary=change_summary,
            )

            current_object_lifecycle = _object_lifecycle_state(object_row)
            next_object_lifecycle = str(parsed.metadata["object_lifecycle_state"])
            self.authority.require_object_lifecycle_transition(
                current_object_lifecycle,
                next_object_lifecycle,
            )
            upsert_knowledge_object(
                connection,
                object_id=object_row["object_id"],
                object_type=object_row["object_type"],
                legacy_type=object_row["legacy_type"],
                title=str(parsed.metadata["title"]),
                summary=str(parsed.metadata["summary"]),
                object_lifecycle_state=next_object_lifecycle,
                owner=str(parsed.metadata["owner"]),
                team=str(parsed.metadata["team"]),
                canonical_path=str(parsed.metadata["canonical_path"]),
                source_type=str(parsed.metadata["source_type"]),
                source_system=str(parsed.metadata["source_system"]),
                source_title=str(parsed.metadata["source_title"]),
                created_date=str(parsed.metadata["created"]),
                updated_date=str(parsed.metadata["updated"]),
                last_reviewed=str(parsed.metadata["last_reviewed"]),
                review_cadence=str(parsed.metadata["review_cadence"]),
                trust_state=TrustState.SUSPECT.value,
                source_sync_state=_source_sync_state(object_row),
                current_revision_id=revision_id,
                tags_json=json_dump(parsed.metadata.get("tags", [])),
                systems_json=json_dump(parsed.metadata.get("systems", [])),
            )
            persist_revision_artifacts(
                connection,
                parsed=parsed,
                revision_id=revision_id,
                relationship_provenance="workflow_projection",
            )
            self.runtime.refresh_object_projection(connection, object_id=object_id)

            event_id = _event_id("revision-created")
            details = {
                "revision_number": revision_number,
                "change_summary": change_summary,
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="revision_created",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            connection.commit()
            return _row_to_revision(self._require_revision(connection, object_id=object_id, revision_id=revision_id))
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def submit_for_review(
        self,
        *,
        object_id: str,
        revision_id: str,
        actor: str,
        notes: str | None = None,
    ) -> AuditEvent:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            self._require_object(connection, object_id)
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=revision_id)
            revision_state = _revision_review_state(revision_row)
            draft_progress_state = _draft_progress_state(revision_row)
            if draft_progress_state != DraftProgressState.READY_FOR_REVIEW.value:
                raise ValueError(
                    f"revision {revision_id} is not ready for review; current draft_progress_state is {draft_progress_state}"
                )
            decision = self.authority.require_revision_review_transition(
                revision_state,
                RevisionReviewState.IN_REVIEW.value,
            )

            update_knowledge_revision_state(
                connection,
                revision_id=revision_id,
                revision_review_state=RevisionReviewState.IN_REVIEW.value,
                draft_progress_state=draft_progress_state,
            )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                current_revision_id=revision_id,
                trust_state=TrustState.SUSPECT.value,
            )
            self.runtime.refresh_object_projection(connection, object_id=object_id)

            event_id = _event_id("revision-submitted")
            details = {
                "notes": notes,
                "policy_decision": policy_decision_payload(decision),
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="revision_submitted_for_review",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            connection.commit()
            return _audit_event(
                event_id=event_id,
                event_type="revision_submitted_for_review",
                occurred_at=now,
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details=details,
            )
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def assign_reviewer(
        self,
        *,
        object_id: str,
        revision_id: str,
        reviewer: str,
        actor: str,
        due_at: dt.datetime | None = None,
        notes: str | None = None,
    ) -> ReviewAssignment:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            self._require_object(connection, object_id)
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=revision_id)
            if _revision_review_state(revision_row) != RevisionReviewState.IN_REVIEW.value:
                raise ValueError(f"revision {revision_id} must be in_review before assigning reviewers")

            existing = list_review_assignments_for_revision(connection, revision_id)
            for assignment in existing:
                if assignment["reviewer"] == reviewer and assignment["state"] == ReviewAssignmentState.ASSIGNED.value:
                    raise ValueError(f"reviewer {reviewer} is already assigned to revision {revision_id}")

            assignment_id = _event_id("review-assignment")
            insert_review_assignment(
                connection,
                assignment_id=assignment_id,
                object_id=object_id,
                revision_id=revision_id,
                reviewer=reviewer,
                state=ReviewAssignmentState.ASSIGNED.value,
                assigned_at=now.isoformat(),
                due_at=due_at.isoformat() if due_at is not None else None,
                notes=notes,
            )
            event_id = _event_id("reviewer-assigned")
            details = {
                "assignment_id": assignment_id,
                "reviewer": reviewer,
                "due_at": due_at.isoformat() if due_at is not None else None,
                "notes": notes,
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="reviewer_assigned",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            connection.commit()
            assignment_row = get_review_assignment(connection, assignment_id)
            if assignment_row is None:  # pragma: no cover
                raise ValueError(f"review assignment not found after insert: {assignment_id}")
            return _row_to_assignment(assignment_row)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def approve_revision(
        self,
        *,
        object_id: str,
        revision_id: str,
        reviewer: str,
        actor: str,
        notes: str | None = None,
    ) -> KnowledgeRevision:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        pending_writeback: writeback_flow.PendingSourceWriteback | None = None
        writeback_result: writeback_flow.SourceWritebackResult | None = None
        try:
            object_row = self._require_object(connection, object_id)
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=revision_id)
            revision_state = _revision_review_state(revision_row)
            if revision_state != RevisionReviewState.IN_REVIEW.value:
                raise ValueError(f"revision {revision_id} must be in_review before approval")
            revision_author = _revision_author_actor(connection, revision_id)
            if revision_author and revision_author == actor:
                raise ValueError("self-approval is not allowed; another actor must approve this revision")
            revision_decision = self.authority.require_revision_review_transition(
                revision_state,
                RevisionReviewState.APPROVED.value,
            )

            active_assignment = self._require_assignment(connection, revision_id=revision_id, reviewer=reviewer)
            assignments = list_review_assignments_for_revision(connection, revision_id)
            for assignment in assignments:
                if assignment["assignment_id"] == active_assignment["assignment_id"]:
                    update_review_assignment(
                        connection,
                        assignment_id=assignment["assignment_id"],
                        state=ReviewAssignmentState.APPROVED.value,
                        notes=notes,
                    )
                elif assignment["state"] == ReviewAssignmentState.ASSIGNED.value:
                    update_review_assignment(
                        connection,
                        assignment_id=assignment["assignment_id"],
                        state=ReviewAssignmentState.CANCELLED.value,
                        notes="Closed after approval on the revision.",
                    )

            update_knowledge_revision_state(
                connection,
                revision_id=revision_id,
                revision_review_state=RevisionReviewState.APPROVED.value,
                draft_progress_state=_draft_progress_state(revision_row),
            )
            payload = json.loads(revision_row["normalized_payload_json"])
            parsed = self.runtime.parse_revision(payload, revision_row["body_markdown"])
            next_object_lifecycle = str(parsed.metadata["object_lifecycle_state"])
            object_decision = None
            current_object_lifecycle = _object_lifecycle_state(object_row)
            if current_object_lifecycle != next_object_lifecycle:
                object_decision = self.authority.require_object_lifecycle_transition(
                    current_object_lifecycle,
                    next_object_lifecycle,
                )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                object_lifecycle_state=next_object_lifecycle,
                trust_state=runtime_trust_state(
                    base_trust_state=parsed.trust_state,
                    revision_state=RevisionReviewStatus.APPROVED.value,
                    preserve_existing_warning=False,
                ),
                current_revision_id=revision_id,
            )
            self.runtime.refresh_object_projection(connection, object_id=object_id)
            pending_writeback = writeback_flow.prepare_revision_writeback(
                connection,
                object_id=object_id,
                revision_id=revision_id,
                actor=actor,
                root_path=self.source_root,
                authority=self.authority,
            )
            writeback_result = pending_writeback.result
            self.runtime.refresh_object_projection(connection, object_id=object_id)

            recorded_at = _now_utc()
            event_id = _event_id("revision-approved")
            details = {
                "reviewer": reviewer,
                "assignment_id": active_assignment["assignment_id"],
                "notes": notes,
                "policy_decision": policy_decision_payload(revision_decision),
                "object_lifecycle_decision": policy_decision_payload(object_decision),
                "previous_revision_id": writeback_result.previous_revision_id,
                "source_writeback_path": writeback_result.file_path.relative_to(self.source_root).as_posix(),
                "writeback_backup_path": (
                    writeback_result.backup_path.relative_to(self.source_root).as_posix()
                    if writeback_result.backup_path is not None
                    else None
                ),
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="revision_approved",
                occurred_at=recorded_at.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            if pending_writeback is not None:
                pending_writeback.commit(connection)
                pending_writeback = None
            else:
                connection.commit()
            return _row_to_revision(self._require_revision(connection, object_id=object_id, revision_id=revision_id))
        except Exception:
            if pending_writeback is not None:
                pending_writeback.rollback(connection)
            else:
                connection.rollback()
            raise
        finally:
            connection.close()

    def reject_revision(
        self,
        *,
        object_id: str,
        revision_id: str,
        reviewer: str,
        actor: str,
        notes: str,
    ) -> KnowledgeRevision:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            self._require_object(connection, object_id)
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=revision_id)
            revision_state = _revision_review_state(revision_row)
            if revision_state != RevisionReviewState.IN_REVIEW.value:
                raise ValueError(f"revision {revision_id} must be in_review before rejection")
            decision = self.authority.require_revision_review_transition(
                revision_state,
                RevisionReviewState.REJECTED.value,
            )
            active_assignment = self._require_assignment(connection, revision_id=revision_id, reviewer=reviewer)
            assignments = list_review_assignments_for_revision(connection, revision_id)
            for assignment in assignments:
                if assignment["assignment_id"] == active_assignment["assignment_id"]:
                    update_review_assignment(
                        connection,
                        assignment_id=assignment["assignment_id"],
                        state=ReviewAssignmentState.REJECTED.value,
                        notes=notes,
                    )
                elif assignment["state"] == ReviewAssignmentState.ASSIGNED.value:
                    update_review_assignment(
                        connection,
                        assignment_id=assignment["assignment_id"],
                        state=ReviewAssignmentState.CANCELLED.value,
                        notes="Closed after rejection on the revision.",
                    )

            update_knowledge_revision_state(
                connection,
                revision_id=revision_id,
                revision_review_state=RevisionReviewState.REJECTED.value,
                draft_progress_state=_draft_progress_state(revision_row),
            )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                current_revision_id=revision_id,
                trust_state=TrustState.SUSPECT.value,
            )
            self.runtime.refresh_object_projection(connection, object_id=object_id)

            event_id = _event_id("revision-rejected")
            details = {
                "reviewer": reviewer,
                "assignment_id": active_assignment["assignment_id"],
                "notes": notes,
                "policy_decision": policy_decision_payload(decision),
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="revision_rejected",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            connection.commit()
            return _row_to_revision(self._require_revision(connection, object_id=object_id, revision_id=revision_id))
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def supersede_object(
        self,
        *,
        object_id: str,
        replacement_object_id: str,
        actor: str,
        notes: str | None = None,
    ) -> KnowledgeObject:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            source_object = self._require_object(connection, object_id)
            self._require_object(connection, replacement_object_id)
            if object_id == replacement_object_id:
                raise ValueError("knowledge object cannot supersede itself")

            upsert_relationship(
                connection,
                relationship_id=_relationship_id(
                    "knowledge_object",
                    object_id,
                    "knowledge_object",
                    replacement_object_id,
                    "superseded_by",
                ),
                source_entity_type="knowledge_object",
                source_entity_id=object_id,
                target_entity_type="knowledge_object",
                target_entity_id=replacement_object_id,
                relationship_type="superseded_by",
                provenance="workflow",
            )
            if source_object["current_revision_id"]:
                current_revision_row = self._require_revision(
                    connection,
                    object_id=object_id,
                    revision_id=str(source_object["current_revision_id"]),
                )
                if _revision_review_state(current_revision_row) == RevisionReviewState.APPROVED.value:
                    self.authority.require_revision_review_transition(
                        RevisionReviewState.APPROVED.value,
                        RevisionReviewState.SUPERSEDED.value,
                    )
                    update_knowledge_revision_state(
                        connection,
                        revision_id=source_object["current_revision_id"],
                        revision_review_state=RevisionReviewState.SUPERSEDED.value,
                    )

            decision = self.authority.require_object_lifecycle_transition(
                _object_lifecycle_state(source_object),
                ObjectLifecycleState.DEPRECATED.value,
            )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                object_lifecycle_state=ObjectLifecycleState.DEPRECATED.value,
                trust_state=TrustState.SUSPECT.value,
            )
            self.runtime.refresh_object_projection(connection, object_id=object_id)

            event_id = _event_id("object-superseded")
            details = {
                "replacement_object_id": replacement_object_id,
                "notes": notes,
                "policy_decision": policy_decision_payload(decision),
            }
            insert_audit_event(
                connection,
                event_id=event_id,
                event_type="object_superseded",
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=source_object["current_revision_id"],
                details_json=json_dump(details),
            )
            connection.commit()
            return _row_to_object(self._require_object(connection, object_id))
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def archive_object(
        self,
        *,
        object_id: str,
        actor: str,
        retirement_reason: str,
        notes: str | None = None,
        acknowledgements: list[str] | tuple[str, ...] | set[str] | None = None,
    ) -> dict[str, Any]:
        actor = require_actor_id(actor)
        connection = self._connection()
        now = _now_utc()
        try:
            acknowledgement_list = tuple(str(item) for item in acknowledgements or [])
            object_row = self._require_object(connection, object_id)
            decision = self.authority.require_object_lifecycle_transition(
                _object_lifecycle_state(object_row),
                ObjectLifecycleState.ARCHIVED.value,
            )
            self.authority.assert_acknowledgements(decision, acknowledgement_list)

            current_revision_id = str(object_row["current_revision_id"] or "").strip()
            if not current_revision_id:
                raise ValueError("archive requires a current revision so canonical content can be updated coherently")
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=current_revision_id)

            metadata = json.loads(str(revision_row["normalized_payload_json"]))
            current_canonical_path = str(metadata.get("canonical_path") or object_row["canonical_path"])
            archived_canonical_path = _archive_canonical_path(current_canonical_path)
            current_file_path = self.authority.resolve_canonical_target_path(
                source_root=self.source_root,
                canonical_path=current_canonical_path,
            )
            archived_file_path = self.authority.resolve_canonical_target_path(
                source_root=self.source_root,
                canonical_path=archived_canonical_path,
            )
            if archived_file_path.exists():
                raise ValueError(f"archive target already exists: {archived_canonical_path}")

            current_source_text = current_file_path.read_text(encoding="utf-8") if current_file_path.exists() else None
            archived_metadata = dict(metadata)
            archived_metadata["object_lifecycle_state"] = ObjectLifecycleState.ARCHIVED.value
            archived_metadata["canonical_path"] = archived_canonical_path
            archived_metadata["retirement_reason"] = retirement_reason
            archived_metadata["updated"] = now.date().isoformat()
            archived_payload_json = json_dump(archived_metadata)
            archived_content_hash = _content_hash(archived_payload_json, str(revision_row["body_markdown"]))
            archived_markdown = writeback_flow.render_revision_markdown(
                object_type=str(object_row["object_type"]),
                metadata=archived_metadata,
                body_markdown=str(revision_row["body_markdown"]),
            )

            mutation_id = f"archive-{uuid.uuid4().hex[:12]}"
            backup_path: Path | None = None
            if current_source_text is not None:
                timestamp = now.strftime("%Y%m%dT%H%M%SZ")
                backup_path = (
                    self.authority.backup_root(source_root=self.source_root)
                    / slugify(object_id)
                    / f"{timestamp}-archive-{current_file_path.name}"
                )

            with TransactionalMutation(
                source_root=self.source_root,
                mutation_id=mutation_id,
                mutation_type="archive_object",
                object_id=object_id,
                authority=self.authority,
            ) as mutation:
                mutation.set_metadata(
                    revision_id=current_revision_id,
                    from_path=current_canonical_path,
                    archived_path=archived_canonical_path,
                    retirement_reason=retirement_reason,
                )
                if backup_path is not None:
                    mutation.stage_write(
                        target_path=backup_path,
                        previous_text=None,
                        new_text=current_source_text,
                    )
                mutation.stage_write(
                    target_path=archived_file_path,
                    previous_text=None,
                    new_text=archived_markdown,
                )
                if current_source_text is not None:
                    mutation.stage_delete(
                        target_path=current_file_path,
                        previous_text=current_source_text,
                    )

                update_knowledge_revision_content(
                    connection,
                    revision_id=current_revision_id,
                    content_hash=archived_content_hash,
                    body_markdown=str(revision_row["body_markdown"]),
                    normalized_payload_json=archived_payload_json,
                    blueprint_id=str(revision_row["blueprint_id"] or object_row["object_type"]),
                    draft_progress_state=_draft_progress_state(revision_row),
                    section_content_json=str(revision_row["section_content_json"]),
                    section_completion_json=str(revision_row["section_completion_json"]),
                    change_summary=str(revision_row["change_summary"]) if revision_row["change_summary"] is not None else None,
                )
                update_knowledge_object_runtime_state(
                    connection,
                    object_id=object_id,
                    canonical_path=archived_canonical_path,
                    object_lifecycle_state=ObjectLifecycleState.ARCHIVED.value,
                    source_sync_state=SourceSyncState.APPLIED.value,
                    source_sync_revision_id=current_revision_id,
                    source_sync_content_hash=archived_content_hash,
                    source_sync_mutation_id=mutation_id,
                    updated_date=now.date().isoformat(),
                )
                self.runtime.refresh_object_projection(connection, object_id=object_id)
                insert_audit_event(
                    connection,
                    event_id=_event_id("object-archived"),
                    event_type="object_archived",
                    occurred_at=now.isoformat(),
                    actor=actor,
                    object_id=object_id,
                    revision_id=current_revision_id,
                    details_json=json_dump(
                        {
                            "notes": notes,
                            "retirement_reason": retirement_reason,
                            "previous_canonical_path": current_canonical_path,
                            "archived_canonical_path": archived_canonical_path,
                            "backup_path": (
                                backup_path.relative_to(self.source_root).as_posix()
                                if backup_path is not None
                                else None
                            ),
                            "mutation_id": mutation_id,
                            "transition": policy_decision_payload(decision)["transition"],
                            "required_acknowledgements": list(decision.required_acknowledgements),
                            "acknowledgements": list(acknowledgement_list),
                            "source_of_truth": decision.source_of_truth,
                            "state_change": {
                                "machine": decision.transition.machine,
                                "from_state": decision.transition.from_state,
                                "to_state": decision.transition.to_state,
                            },
                            "invalidated_assumptions": list(decision.invalidated_assumptions),
                            "operator_message": decision.operator_message,
                            "policy_decision": policy_decision_payload(decision),
                        }
                    ),
                )
                mutation.apply_files()
                connection.commit()
                mutation.mark_committed()

            return {
                "object_id": object_id,
                "revision_id": current_revision_id,
                "previous_canonical_path": current_canonical_path,
                "archived_canonical_path": archived_canonical_path,
                "backup_path": backup_path,
                "mutation_id": mutation_id,
                "object_lifecycle_state": ObjectLifecycleState.ARCHIVED.value,
                "required_acknowledgements": decision.required_acknowledgements,
                "acknowledgements": acknowledgement_list,
                "source_of_truth": decision.source_of_truth,
                "transition": policy_decision_payload(decision)["transition"],
                "state_change": {
                    "machine": decision.transition.machine,
                    "from_state": decision.transition.from_state,
                    "to_state": decision.transition.to_state,
                },
                "invalidated_assumptions": decision.invalidated_assumptions,
                "operator_message": decision.operator_message,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


def mark_object_suspect_due_to_change(
    *,
    database_path: Path = DB_PATH,
    source_root: Path = ROOT,
    object_id: str,
    actor: str,
    reason: str,
    changed_entity_type: str,
    changed_entity_id: str | None = None,
    authority: PolicyAuthority | None = None,
) -> AuditEvent:
    actor = require_actor_id(actor)
    workflow = GovernanceWorkflow(
        database_path,
        source_root=source_root,
        authority=authority,
    )
    connection = workflow._connection()
    now = _now_utc()
    try:
        object_row = workflow._require_object(connection, object_id)
        update_knowledge_object_runtime_state(
            connection,
            object_id=object_id,
            trust_state=TrustState.SUSPECT.value,
        )
        workflow.runtime.refresh_object_projection(connection, object_id=object_id)

        event_id = _event_id("object-suspect")
        details = {
            "reason": reason,
            "changed_entity_type": changed_entity_type,
            "changed_entity_id": changed_entity_id,
        }
        insert_audit_event(
            connection,
            event_id=event_id,
            event_type="object_marked_suspect_due_to_change",
            occurred_at=now.isoformat(),
            actor=actor,
            object_id=object_id,
            revision_id=object_row["current_revision_id"],
            details_json=json_dump(details),
        )
        connection.commit()
        return _audit_event(
            event_id=event_id,
            event_type="object_marked_suspect_due_to_change",
            occurred_at=now,
            actor=actor,
            object_id=object_id,
            revision_id=object_row["current_revision_id"],
            details=details,
        )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
