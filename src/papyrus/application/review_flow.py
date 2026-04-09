from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any

from papyrus.application import writeback_flow
from papyrus.domain.actor import require_actor_id
from papyrus.domain.entities import AuditEvent, KnowledgeDocument, KnowledgeObject, KnowledgeRevision, ReviewAssignment
from papyrus.domain.policies import runtime_trust_state
from papyrus.domain.value_objects import (
    KnowledgeLifecycleStatus,
    ReviewAssignmentState,
    RevisionReviewStatus,
    TrustState,
)
from papyrus.infrastructure.db import RUNTIME_SCHEMA_VERSION, open_runtime_database
from papyrus.infrastructure.markdown.parser import normalize_object_metadata
from papyrus.infrastructure.markdown.serializer import json_dump
from papyrus.infrastructure.markdown.writer import MarkdownWriter
from papyrus.infrastructure.migrations import apply_runtime_schema
from papyrus.infrastructure.paths import DB_PATH, ROOT
from papyrus.infrastructure.repositories.audit_repo import insert_audit_event
from papyrus.infrastructure.repositories.knowledge_repo import (
    delete_search_document,
    find_revision_by_content_hash,
    get_knowledge_object,
    get_knowledge_revision,
    next_revision_number,
    upsert_knowledge_object,
    upsert_relationship,
    update_knowledge_object_runtime_state,
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
from papyrus.jobs.citation_scan import scan_citations
from papyrus.jobs.stale_scan import cadence_to_days
from papyrus.application.runtime_projection import persist_revision_artifacts, refresh_current_object_projection


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def _event_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def _content_hash(normalized_payload_json: str, body_markdown: str) -> str:
    return hashlib.sha256(f"{normalized_payload_json}\n{body_markdown}".encode("utf-8")).hexdigest()


def _relationship_id(source_type: str, source_id: str, target_type: str, target_id: str, rel_type: str) -> str:
    return hashlib.sha256(f"{source_type}|{source_id}|{target_type}|{target_id}|{rel_type}".encode("utf-8")).hexdigest()[:24]


def _row_to_object(row: sqlite3.Row) -> KnowledgeObject:
    return KnowledgeObject(
        object_id=row["object_id"],
        object_type=row["object_type"],
        title=row["title"],
        status=row["status"],
        owner=row["owner"],
        team=row["team"],
        canonical_path=row["canonical_path"],
    )


def _row_to_revision(row: sqlite3.Row) -> KnowledgeRevision:
    return KnowledgeRevision(
        revision_id=row["revision_id"],
        object_id=row["object_id"],
        revision_number=row["revision_number"],
        state=row["revision_state"],
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
    def __init__(self, database_path: Path = DB_PATH, source_root: Path = ROOT):
        self.database_path = Path(database_path)
        self.source_root = Path(source_root).resolve()
        self.taxonomies = None

    def _connection(self) -> sqlite3.Connection:
        connection = open_runtime_database(self.database_path, minimum_schema_version=RUNTIME_SCHEMA_VERSION)
        apply_runtime_schema(connection, has_fts5=fts5_available(connection))
        connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version, applied_at) VALUES (?, ?)",
            (RUNTIME_SCHEMA_VERSION, _now_utc().isoformat()),
        )
        return connection

    def _taxonomies(self) -> dict[str, dict[str, Any]]:
        if self.taxonomies is None:
            from papyrus.infrastructure.repositories.knowledge_repo import load_taxonomies

            self.taxonomies = load_taxonomies()
        return self.taxonomies

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

    def _build_document(self, metadata: dict[str, Any], body_markdown: str) -> KnowledgeDocument:
        canonical_path = str(metadata.get("canonical_path") or "")
        return KnowledgeDocument(
            source_path=self.source_root / canonical_path if canonical_path else self.source_root,
            relative_path=canonical_path,
            metadata=dict(metadata),
            body=body_markdown,
        )

    def _parsed_revision(self, metadata: dict[str, Any], body_markdown: str):
        document = self._build_document(metadata, body_markdown)
        cadence_days = cadence_to_days(str(metadata["review_cadence"]), self._taxonomies())
        return normalize_object_metadata(
            document,
            review_cadence_days=cadence_days,
            as_of=dt.date.today(),
        )

    def _refresh_search_projection(self, connection: sqlite3.Connection, object_id: str) -> None:
        object_row = self._require_object(connection, object_id)
        current_revision_id = object_row["current_revision_id"]
        if not current_revision_id:
            delete_search_document(connection, object_id)
            return
        scan_citations(
            connection,
            taxonomies=self._taxonomies(),
            as_of=dt.date.today(),
            object_ids=[object_id],
            persist=True,
        )
        refresh_current_object_projection(
            connection,
            object_id=object_id,
            taxonomies=self._taxonomies(),
            as_of=dt.date.today(),
        )

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
        status: str = KnowledgeLifecycleStatus.DRAFT.value,
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

            upsert_knowledge_object(
                connection,
                object_id=object_id,
                object_type=object_type,
                legacy_type=legacy_type,
                title=title,
                summary=summary,
                status=status,
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
                current_revision_id=None,
                tags_json=json_dump(tags or []),
                systems_json=json_dump(systems or []),
            )
            event_id = _event_id("object-created")
            details = {
                "object_type": object_type,
                "canonical_path": canonical_path,
                "status": status,
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
            parsed = self._parsed_revision(normalized_payload, body_markdown)
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
                revision_state=RevisionReviewStatus.DRAFT.value,
                source_path=str(parsed.metadata["canonical_path"]),
                content_hash=content_hash,
                body_markdown=body_markdown,
                normalized_payload_json=normalized_payload_json,
                legacy_metadata_json=json_dump(legacy_metadata or {}),
                imported_at=now.isoformat(),
                change_summary=change_summary,
            )

            upsert_knowledge_object(
                connection,
                object_id=object_row["object_id"],
                object_type=object_row["object_type"],
                legacy_type=object_row["legacy_type"],
                title=str(parsed.metadata["title"]),
                summary=str(parsed.metadata["summary"]),
                status=str(parsed.metadata["status"]),
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
            self._refresh_search_projection(connection, object_id)

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
            if revision_row["revision_state"] not in {
                RevisionReviewStatus.DRAFT.value,
                RevisionReviewStatus.REJECTED.value,
            }:
                raise ValueError(f"revision {revision_id} cannot be submitted from state {revision_row['revision_state']}")

            update_knowledge_revision_state(
                connection,
                revision_id=revision_id,
                revision_state=RevisionReviewStatus.IN_REVIEW.value,
            )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                current_revision_id=revision_id,
                trust_state=TrustState.SUSPECT.value,
            )
            self._refresh_search_projection(connection, object_id)

            event_id = _event_id("revision-submitted")
            details = {"notes": notes}
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
            if revision_row["revision_state"] != RevisionReviewStatus.IN_REVIEW.value:
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
        writeback_result: writeback_flow.SourceWritebackResult | None = None
        try:
            object_row = self._require_object(connection, object_id)
            revision_row = self._require_revision(connection, object_id=object_id, revision_id=revision_id)
            if revision_row["revision_state"] != RevisionReviewStatus.IN_REVIEW.value:
                raise ValueError(f"revision {revision_id} must be in_review before approval")
            revision_author = _revision_author_actor(connection, revision_id)
            if revision_author and revision_author == actor:
                raise ValueError("self-approval is not allowed; another actor must approve this revision")

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
                revision_state=RevisionReviewStatus.APPROVED.value,
            )
            payload = json.loads(revision_row["normalized_payload_json"])
            parsed = self._parsed_revision(payload, revision_row["body_markdown"])
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                status=str(parsed.metadata["status"]),
                trust_state=runtime_trust_state(
                    base_trust_state=parsed.trust_state,
                    revision_state=RevisionReviewStatus.APPROVED.value,
                    preserve_existing_warning=False,
                ),
                current_revision_id=revision_id,
            )
            self._refresh_search_projection(connection, object_id)
            writeback_result = writeback_flow.write_revision_to_source(
                connection,
                object_id=object_id,
                revision_id=revision_id,
                actor=actor,
                root_path=self.source_root,
            )

            event_id = _event_id("revision-approved")
            details = {
                "reviewer": reviewer,
                "assignment_id": active_assignment["assignment_id"],
                "notes": notes,
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
                occurred_at=now.isoformat(),
                actor=actor,
                object_id=object_id,
                revision_id=revision_id,
                details_json=json_dump(details),
            )
            connection.commit()
            return _row_to_revision(self._require_revision(connection, object_id=object_id, revision_id=revision_id))
        except Exception:
            if writeback_result is not None:
                MarkdownWriter(self.source_root).restore(
                    file_path=writeback_result.file_path,
                    previous_text=writeback_result.previous_text,
                )
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
            if revision_row["revision_state"] != RevisionReviewStatus.IN_REVIEW.value:
                raise ValueError(f"revision {revision_id} must be in_review before rejection")
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
                revision_state=RevisionReviewStatus.REJECTED.value,
            )
            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                current_revision_id=revision_id,
                trust_state=TrustState.SUSPECT.value,
            )
            self._refresh_search_projection(connection, object_id)

            event_id = _event_id("revision-rejected")
            details = {
                "reviewer": reviewer,
                "assignment_id": active_assignment["assignment_id"],
                "notes": notes,
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
                update_knowledge_revision_state(
                    connection,
                    revision_id=source_object["current_revision_id"],
                    revision_state=RevisionReviewStatus.SUPERSEDED.value,
                )

            update_knowledge_object_runtime_state(
                connection,
                object_id=object_id,
                status=KnowledgeLifecycleStatus.DEPRECATED.value,
                trust_state=TrustState.SUSPECT.value,
            )
            self._refresh_search_projection(connection, object_id)

            event_id = _event_id("object-superseded")
            details = {
                "replacement_object_id": replacement_object_id,
                "notes": notes,
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


def mark_object_suspect_due_to_change(
    *,
    database_path: Path = DB_PATH,
    object_id: str,
    actor: str,
    reason: str,
    changed_entity_type: str,
    changed_entity_id: str | None = None,
) -> AuditEvent:
    actor = require_actor_id(actor)
    workflow = GovernanceWorkflow(database_path)
    connection = workflow._connection()
    now = _now_utc()
    try:
        object_row = workflow._require_object(connection, object_id)
        update_knowledge_object_runtime_state(
            connection,
            object_id=object_id,
            trust_state=TrustState.SUSPECT.value,
        )
        workflow._refresh_search_projection(connection, object_id)

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
