from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ObjectLifecycleState(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class RevisionReviewState(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DraftProgressState(StrEnum):
    BLOCKED = "blocked"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"


class IngestionLifecycleState(StrEnum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    CLASSIFIED = "classified"
    MAPPED = "mapped"
    CONVERTED = "converted"


class SourceSyncState(StrEnum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    APPLIED = "applied"
    CONFLICTED = "conflicted"
    RESTORED = "restored"


OBJECT_LIFECYCLE_TRANSITIONS: dict[ObjectLifecycleState, tuple[ObjectLifecycleState, ...]] = {
    ObjectLifecycleState.DRAFT: (ObjectLifecycleState.ACTIVE,),
    ObjectLifecycleState.ACTIVE: (ObjectLifecycleState.DEPRECATED,),
    ObjectLifecycleState.DEPRECATED: (ObjectLifecycleState.ARCHIVED,),
    ObjectLifecycleState.ARCHIVED: (),
}

REVISION_REVIEW_TRANSITIONS: dict[RevisionReviewState, tuple[RevisionReviewState, ...]] = {
    RevisionReviewState.DRAFT: (RevisionReviewState.IN_REVIEW,),
    RevisionReviewState.IN_REVIEW: (
        RevisionReviewState.APPROVED,
        RevisionReviewState.REJECTED,
    ),
    RevisionReviewState.APPROVED: (RevisionReviewState.SUPERSEDED,),
    RevisionReviewState.REJECTED: (RevisionReviewState.DRAFT,),
    RevisionReviewState.SUPERSEDED: (),
}

DRAFT_PROGRESS_TRANSITIONS: dict[DraftProgressState, tuple[DraftProgressState, ...]] = {
    DraftProgressState.BLOCKED: (
        DraftProgressState.IN_PROGRESS,
        DraftProgressState.READY_FOR_REVIEW,
    ),
    DraftProgressState.IN_PROGRESS: (
        DraftProgressState.BLOCKED,
        DraftProgressState.READY_FOR_REVIEW,
    ),
    DraftProgressState.READY_FOR_REVIEW: (
        DraftProgressState.BLOCKED,
        DraftProgressState.IN_PROGRESS,
    ),
}

INGESTION_LIFECYCLE_TRANSITIONS: dict[IngestionLifecycleState, tuple[IngestionLifecycleState, ...]] = {
    IngestionLifecycleState.UPLOADED: (IngestionLifecycleState.PARSED,),
    IngestionLifecycleState.PARSED: (IngestionLifecycleState.CLASSIFIED,),
    IngestionLifecycleState.CLASSIFIED: (IngestionLifecycleState.MAPPED,),
    IngestionLifecycleState.MAPPED: (IngestionLifecycleState.CONVERTED,),
    IngestionLifecycleState.CONVERTED: (),
}

SOURCE_SYNC_TRANSITIONS: dict[SourceSyncState, tuple[SourceSyncState, ...]] = {
    SourceSyncState.NOT_REQUIRED: (
        SourceSyncState.PENDING,
        SourceSyncState.APPLIED,
    ),
    SourceSyncState.PENDING: (
        SourceSyncState.APPLIED,
        SourceSyncState.CONFLICTED,
    ),
    SourceSyncState.APPLIED: (
        SourceSyncState.PENDING,
        SourceSyncState.CONFLICTED,
        SourceSyncState.RESTORED,
    ),
    SourceSyncState.CONFLICTED: (
        SourceSyncState.PENDING,
        SourceSyncState.APPLIED,
    ),
    SourceSyncState.RESTORED: (
        SourceSyncState.PENDING,
        SourceSyncState.APPLIED,
    ),
}


MACHINE_TRANSITIONS = {
    "object_lifecycle_state": OBJECT_LIFECYCLE_TRANSITIONS,
    "revision_review_state": REVISION_REVIEW_TRANSITIONS,
    "draft_progress_state": DRAFT_PROGRESS_TRANSITIONS,
    "ingestion_state": INGESTION_LIFECYCLE_TRANSITIONS,
    "source_sync_state": SOURCE_SYNC_TRANSITIONS,
}


class TransitionSemantics(StrEnum):
    NO_OP = "no_op"
    ALLOWED = "allowed_transition"
    ILLEGAL = "illegal_transition"


@dataclass(frozen=True)
class TransitionDescriptor:
    machine: str
    from_state: str
    to_state: str
    semantics: TransitionSemantics
    allowed_targets: tuple[str, ...]

    @property
    def allowed(self) -> bool:
        return self.semantics != TransitionSemantics.ILLEGAL

    @property
    def changes_state(self) -> bool:
        return self.semantics == TransitionSemantics.ALLOWED


def allowed_transitions(machine: str, current_state: str) -> tuple[str, ...]:
    transitions = MACHINE_TRANSITIONS[machine]
    if machine == "object_lifecycle_state":
        current = ObjectLifecycleState(current_state)
    elif machine == "revision_review_state":
        current = RevisionReviewState(current_state)
    elif machine == "draft_progress_state":
        current = DraftProgressState(current_state)
    elif machine == "ingestion_state":
        current = IngestionLifecycleState(current_state)
    elif machine == "source_sync_state":
        current = SourceSyncState(current_state)
    else:  # pragma: no cover
        raise KeyError(f"unsupported lifecycle machine: {machine}")
    return tuple(str(item) for item in transitions[current])


def transition_is_allowed(machine: str, current_state: str, target_state: str) -> bool:
    return evaluate_transition(machine, current_state, target_state).allowed


def illegal_transition_message(machine: str, current_state: str, target_state: str) -> str:
    allowed = ", ".join(allowed_transitions(machine, current_state)) or "no further transitions"
    return f"illegal {machine} transition: {current_state} -> {target_state}; allowed: {allowed}"


def evaluate_transition(machine: str, current_state: str, target_state: str) -> TransitionDescriptor:
    allowed_targets = allowed_transitions(machine, current_state)
    if current_state == target_state:
        return TransitionDescriptor(
            machine=machine,
            from_state=current_state,
            to_state=target_state,
            semantics=TransitionSemantics.NO_OP,
            allowed_targets=allowed_targets,
        )
    if target_state not in allowed_targets:
        return TransitionDescriptor(
            machine=machine,
            from_state=current_state,
            to_state=target_state,
            semantics=TransitionSemantics.ILLEGAL,
            allowed_targets=allowed_targets,
        )
    return TransitionDescriptor(
        machine=machine,
        from_state=current_state,
        to_state=target_state,
        semantics=TransitionSemantics.ALLOWED,
        allowed_targets=allowed_targets,
    )


def require_transition(machine: str, current_state: str, target_state: str) -> TransitionDescriptor:
    transition = evaluate_transition(machine, current_state, target_state)
    if transition.semantics == TransitionSemantics.ILLEGAL:
        raise ValueError(illegal_transition_message(machine, current_state, target_state))
    return transition
