from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from papyrus.domain.lifecycle import (
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
    TransitionDescriptor,
    TransitionSemantics,
    evaluate_transition,
    illegal_transition_message,
)
from papyrus.infrastructure.repositories.knowledge_repo import load_policy


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    required_acknowledgements: tuple[str, ...]
    source_of_truth: str
    transition: TransitionDescriptor
    invalidated_assumptions: tuple[str, ...]
    operator_message: str

    @property
    def state_change(self) -> TransitionDescriptor:
        return self.transition


def transition_payload(transition: TransitionDescriptor | None) -> dict[str, Any] | None:
    if transition is None:
        return None
    return {
        "machine": transition.machine,
        "from_state": transition.from_state,
        "to_state": transition.to_state,
        "semantics": transition.semantics.value,
        "allowed_targets": list(transition.allowed_targets),
        "allowed": transition.allowed,
        "changes_state": transition.changes_state,
    }


def policy_decision_payload(decision: PolicyDecision | None) -> dict[str, Any] | None:
    if decision is None:
        return None
    return {
        "allowed": decision.allowed,
        "required_acknowledgements": list(decision.required_acknowledgements),
        "source_of_truth": decision.source_of_truth,
        "transition": transition_payload(decision.transition),
        "invalidated_assumptions": list(decision.invalidated_assumptions),
        "operator_message": decision.operator_message,
    }


class PolicyAuthority:
    def __init__(self, policy: dict[str, Any] | None = None) -> None:
        self.policy = policy or load_policy()

    @classmethod
    def from_repository_policy(cls) -> "PolicyAuthority":
        return cls(load_policy())

    def canonical_write_roots(self, *, source_root: Path) -> tuple[Path, ...]:
        configured = self.policy.get("path_policy", {}).get("canonical_write_roots", [])
        return tuple(self._resolve_policy_path(source_root, item).resolve() for item in configured)

    def local_ingest_read_roots(self, *, source_root: Path) -> tuple[Path, ...]:
        configured = self.policy.get("path_policy", {}).get("local_ingest_read_roots", [])
        return tuple(self._resolve_policy_path(source_root, item).resolve() for item in configured)

    def mutation_root(self, *, source_root: Path) -> Path:
        configured = str(self.policy.get("path_policy", {}).get("mutation_root", "build/mutations"))
        return self._resolve_policy_path(source_root, configured).resolve()

    def backup_root(self, *, source_root: Path) -> Path:
        configured = str(self.policy.get("path_policy", {}).get("backup_root", "build/writeback-backups"))
        return self._resolve_policy_path(source_root, configured).resolve()

    def archive_root(self, *, source_root: Path) -> Path:
        configured = str(self.policy.get("path_policy", {}).get("archive_root", "archive/knowledge"))
        return self._resolve_policy_path(source_root, configured).resolve()

    def validate_canonical_repo_relative_path(
        self,
        canonical_path: str,
        *,
        allow_archive: bool = True,
    ) -> str:
        normalized = str(canonical_path or "").strip().replace("\\", "/")
        if not normalized.endswith(".md"):
            raise ValueError("Canonical path must end in .md.")
        allowed_roots = [
            Path(item).as_posix()
            for item in self.policy.get("path_policy", {}).get("canonical_write_roots", [])
        ]
        if not allow_archive:
            allowed_roots = [root for root in allowed_roots if root != "archive/knowledge"]
        if not any(normalized == root or normalized.startswith(f"{root}/") for root in allowed_roots):
            raise ValueError("Canonical path must stay under an approved canonical write root.")
        parts = Path(normalized).parts
        if any(part in {"", ".", ".."} for part in parts):
            raise ValueError("Canonical path must not contain empty, current-directory, or parent-directory segments.")
        return normalized

    def resolve_canonical_target_path(
        self,
        *,
        source_root: Path,
        canonical_path: str,
    ) -> Path:
        normalized = self.validate_canonical_repo_relative_path(canonical_path)
        candidate = (Path(source_root) / normalized).absolute()
        self._assert_within_roots(candidate, self.canonical_write_roots(source_root=Path(source_root)))
        self._assert_no_symlink_traversal(candidate, require_leaf=False)
        return candidate

    def validate_local_ingest_source_path(
        self,
        *,
        source_root: Path,
        candidate_path: str | Path,
    ) -> Path:
        candidate = Path(candidate_path).expanduser()
        if not candidate.is_absolute():
            raise ValueError("Local file path ingestion requires an absolute path on the machine running Papyrus.")
        if not candidate.exists():
            raise ValueError("Local source path not found.")
        if not candidate.is_file():
            raise ValueError("Local source path must point to a file.")
        resolved = candidate.resolve(strict=True)
        self._assert_within_roots(resolved, self.local_ingest_read_roots(source_root=Path(source_root)))
        self._assert_no_symlink_traversal(resolved, require_leaf=True)
        return resolved

    def require_object_lifecycle_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        decision = self.evaluate_object_lifecycle_transition(current_state, target_state)
        if not decision.allowed:
            raise ValueError(illegal_transition_message("object_lifecycle_state", current_state, target_state))
        return decision

    def evaluate_object_lifecycle_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        return self._decision_for_transition(
            evaluate_transition("object_lifecycle_state", current_state, target_state)
        )

    def require_revision_review_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        decision = self.evaluate_revision_review_transition(current_state, target_state)
        if not decision.allowed:
            raise ValueError(illegal_transition_message("revision_review_state", current_state, target_state))
        return decision

    def evaluate_revision_review_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        return self._decision_for_transition(
            evaluate_transition("revision_review_state", current_state, target_state)
        )

    def require_draft_progress_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        decision = self.evaluate_draft_progress_transition(current_state, target_state)
        if not decision.allowed:
            raise ValueError(illegal_transition_message("draft_progress_state", current_state, target_state))
        return decision

    def evaluate_draft_progress_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        return self._decision_for_transition(
            evaluate_transition("draft_progress_state", current_state, target_state)
        )

    def require_ingestion_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        decision = self.evaluate_ingestion_transition(current_state, target_state)
        if not decision.allowed:
            raise ValueError(illegal_transition_message("ingestion_state", current_state, target_state))
        return decision

    def evaluate_ingestion_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        return self._decision_for_transition(
            evaluate_transition("ingestion_state", current_state, target_state)
        )

    def require_source_sync_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        decision = self.evaluate_source_sync_transition(current_state, target_state)
        if not decision.allowed:
            raise ValueError(illegal_transition_message("source_sync_state", current_state, target_state))
        return decision

    def evaluate_source_sync_transition(
        self,
        current_state: str,
        target_state: str,
    ) -> PolicyDecision:
        return self._decision_for_transition(
            evaluate_transition("source_sync_state", current_state, target_state)
        )

    def assert_acknowledgements(
        self,
        decision: PolicyDecision,
        acknowledgements: list[str] | tuple[str, ...] | set[str] | None,
    ) -> None:
        provided = {str(item) for item in acknowledgements or []}
        missing = [item for item in decision.required_acknowledgements if item not in provided]
        if missing:
            raise ValueError("missing required acknowledgements: " + ", ".join(missing))

    def _decision_for_transition(self, transition: TransitionDescriptor) -> PolicyDecision:
        if transition.semantics == TransitionSemantics.ILLEGAL:
            return PolicyDecision(
                allowed=False,
                required_acknowledgements=(),
                source_of_truth="canonical_markdown",
                transition=transition,
                invalidated_assumptions=(),
                operator_message=illegal_transition_message(
                    transition.machine,
                    transition.from_state,
                    transition.to_state,
                ),
            )
        source_of_truth = "canonical_markdown"
        required_acknowledgements: tuple[str, ...] = ()
        invalidated_assumptions: tuple[str, ...] = ()
        if transition.semantics == TransitionSemantics.NO_OP:
            operator_message = (
                f"{transition.machine} remains {transition.to_state}. "
                "The requested action is idempotent and does not produce a new transition."
            )
        else:
            operator_message = (
                f"{transition.machine} will change from {transition.from_state} to {transition.to_state}. "
                "Canonical source remains the source of truth."
            )
        if transition.machine == "source_sync_state":
            source_of_truth = (
                "runtime_projection_pending_sync"
                if transition.to_state == SourceSyncState.PENDING.value
                else "canonical_markdown"
            )
            if transition.to_state == SourceSyncState.APPLIED.value and transition.changes_state:
                required_acknowledgements = ("canonical_source_will_change",)
                invalidated_assumptions = ("previous_runtime_preview_matches_live_source",)
            elif transition.to_state == SourceSyncState.RESTORED.value and transition.changes_state:
                required_acknowledgements = ("restore_can_remove_current_canonical_text",)
                invalidated_assumptions = ("current_canonical_text_remains_authoritative",)
            if transition.semantics == TransitionSemantics.NO_OP:
                operator_message = (
                    f"Source sync state remains {transition.to_state}. "
                    "Canonical Markdown remains authoritative, and the action is a no-op."
                )
            else:
                operator_message = (
                    f"Source sync state will change from {transition.from_state} to {transition.to_state}. "
                    "Canonical Markdown will win after this action, and previously observed source text may no longer be valid."
                )
        elif (
            transition.machine == "object_lifecycle_state"
            and transition.to_state == ObjectLifecycleState.ARCHIVED.value
            and transition.changes_state
        ):
            required_acknowledgements = ("canonical_path_will_move_to_archive",)
            invalidated_assumptions = ("current_knowledge_path_remains_live",)
            operator_message = (
                "Object lifecycle will move to archived. Canonical source will move under archive/knowledge/, "
                "and operators must stop assuming the current knowledge path remains active guidance."
            )
        elif (
            transition.machine == "revision_review_state"
            and transition.to_state == RevisionReviewState.APPROVED.value
            and transition.changes_state
        ):
            required_acknowledgements = ("approval_makes_revision_authoritative",)
            invalidated_assumptions = ("draft_revision_is_non_authoritative",)
            operator_message = (
                "Revision review state will move to approved. The approved revision becomes authoritative for runtime use, "
                "subject to source sync state and trust posture."
            )
        elif (
            transition.machine == "revision_review_state"
            and transition.to_state == RevisionReviewState.SUPERSEDED.value
            and transition.changes_state
        ):
            required_acknowledgements = ("previous_revision_will_stop_being_current",)
            invalidated_assumptions = ("current_revision_remains_primary",)
            operator_message = (
                "Revision review state will move to superseded. Operators must stop assuming the current revision remains the primary governed version."
            )
        return PolicyDecision(
            allowed=True,
            required_acknowledgements=required_acknowledgements,
            source_of_truth=source_of_truth,
            transition=transition,
            invalidated_assumptions=invalidated_assumptions,
            operator_message=operator_message,
        )

    def _resolve_policy_path(self, source_root: Path, raw_path: str | Path) -> Path:
        configured = Path(str(raw_path))
        if configured.is_absolute():
            return configured
        return Path(source_root) / configured

    def _assert_within_roots(self, candidate: Path, roots: tuple[Path, ...]) -> None:
        resolved_candidate = candidate.resolve(strict=False)
        for root in roots:
            try:
                resolved_candidate.relative_to(root)
                return
            except ValueError:
                continue
        raise ValueError("Path is outside the approved policy roots.")

    def _assert_no_symlink_traversal(self, candidate: Path, *, require_leaf: bool) -> None:
        absolute_candidate = candidate.absolute()
        parts = absolute_candidate.parts
        current = Path(parts[0])
        for index, part in enumerate(parts[1:], start=1):
            current = current / part
            if index == len(parts) - 1 and not require_leaf and not current.exists():
                break
            if current.exists() and current.is_symlink():
                raise ValueError(f"Symlink traversal is not allowed for governed paths: {current}")
