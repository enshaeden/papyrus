from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from papyrus.application.action_contracts import (
    ActionDescriptor,
    action_descriptor_payload,
    action_from_gate,
    action_from_policy,
)
from papyrus.application.policy_authority import PolicyAuthority
from papyrus.application.runtime_projection import RuntimeStateSnapshot
from papyrus.domain.lifecycle import (
    DraftProgressState,
    ObjectLifecycleState,
    RevisionReviewState,
)


@dataclass(frozen=True)
class UseGuidanceProjection:
    code: str
    summary: str
    detail: str
    next_action: str
    safe_to_use: bool


@dataclass(frozen=True)
class UiProjection:
    state: RuntimeStateSnapshot
    use_guidance: UseGuidanceProjection
    reasons: tuple[str, ...]
    actions: tuple[ActionDescriptor, ...]


def use_guidance_payload(projection: UseGuidanceProjection) -> dict[str, Any]:
    return {
        "code": projection.code,
        "summary": projection.summary,
        "detail": projection.detail,
        "next_action": projection.next_action,
        "safe_to_use": projection.safe_to_use,
    }


def ui_projection_payload(projection: UiProjection) -> dict[str, Any]:
    return {
        "state": {
            "object_lifecycle_state": projection.state.object_lifecycle_state,
            "revision_review_state": projection.state.revision_review_state,
            "draft_progress_state": projection.state.draft_progress_state,
            "source_sync_state": projection.state.source_sync_state,
            "trust_state": projection.state.trust_state,
            "approval_state": projection.state.approval_state,
        },
        "use_guidance": use_guidance_payload(projection.use_guidance),
        "reasons": list(projection.reasons),
        "actions": [action_descriptor_payload(action) for action in projection.actions],
    }


def build_use_guidance(
    *,
    state: RuntimeStateSnapshot,
    posture: dict[str, Any],
) -> UseGuidanceProjection:
    approval_state = str(state.approval_state or "")
    trust_state = str(state.trust_state or "")
    if approval_state == "approved" and trust_state == "trusted":
        return UseGuidanceProjection(
            code="safe_to_use",
            summary="Safe to use now",
            detail="The current revision is approved and the runtime trust posture is trusted.",
            next_action=str(posture.get("approval", {}).get("action") or "Use the current guidance."),
            safe_to_use=True,
        )
    if approval_state == "in_review":
        return UseGuidanceProjection(
            code="review_pending",
            summary="Review decision pending",
            detail="The current revision is in review and should not be treated as canonical guidance yet.",
            next_action=str(posture.get("approval", {}).get("action") or "Use the last approved guidance or route the revision through review."),
            safe_to_use=False,
        )
    if approval_state in {"draft", "rejected"}:
        return UseGuidanceProjection(
            code="not_ready",
            summary="Not ready for operational use",
            detail="The current revision is draft or rejected and is not approved guidance.",
            next_action=str(posture.get("approval", {}).get("action") or "Complete authoring work and submit the revision for review."),
            safe_to_use=False,
        )
    if trust_state == "weak_evidence":
        return UseGuidanceProjection(
            code="verify_evidence",
            summary="Verify evidence before use",
            detail="Approval is not enough here because the current evidence posture is weak or unverified.",
            next_action=str(posture.get("approval", {}).get("action") or "Review citations and capture stronger evidence before relying on this guidance."),
            safe_to_use=False,
        )
    if trust_state == "stale":
        return UseGuidanceProjection(
            code="revalidate_freshness",
            summary="Revalidate freshness before use",
            detail="The review cadence is overdue, so the guidance may no longer reflect the current environment.",
            next_action=str(posture.get("approval", {}).get("action") or "Refresh the content and validate it before relying on it."),
            safe_to_use=False,
        )
    if trust_state == "suspect":
        return UseGuidanceProjection(
            code="suspect",
            summary="Do not rely on this yet",
            detail=str(posture.get("trust_detail") or "Papyrus marked this guidance suspect and it needs explicit review."),
            next_action=str(posture.get("approval", {}).get("action") or "Inspect the audit trail and related dependencies before use."),
            safe_to_use=False,
        )
    return UseGuidanceProjection(
        code="inspect_posture",
        summary="Inspect lifecycle posture before use",
        detail=str(posture.get("trust_detail") or "Papyrus cannot confirm the current governance posture."),
        next_action=str(posture.get("approval", {}).get("action") or "Inspect the detail and audit views before acting."),
        safe_to_use=False,
    )


def build_object_actions(
    *,
    authority: PolicyAuthority,
    state: RuntimeStateSnapshot,
    current_revision_id: str | None,
    assignment: dict[str, Any] | None = None,
    evidence_status: dict[str, Any] | None = None,
) -> tuple[ActionDescriptor, ...]:
    actions: list[ActionDescriptor] = []
    revision_state = str(state.revision_review_state or "")
    draft_state = str(state.draft_progress_state or DraftProgressState.READY_FOR_REVIEW.value)

    if current_revision_id is not None:
        if draft_state != DraftProgressState.READY_FOR_REVIEW.value:
            actions.append(
                action_from_gate(
                    action_id="submit_for_review",
                    label="Submit for review",
                    available=False,
                    detail="The current revision still has draft blockers or incomplete required sections.",
                )
            )
        else:
            actions.append(
                action_from_policy(
                    action_id="submit_for_review",
                    label="Submit for review",
                    decision=authority.evaluate_revision_review_transition(
                        revision_state,
                        RevisionReviewState.IN_REVIEW.value,
                    ),
                )
            )
    else:
        actions.append(
            action_from_gate(
                action_id="submit_for_review",
                label="Submit for review",
                available=False,
                detail="Create a revision before routing this object into review.",
            )
        )

    actions.append(
        action_from_gate(
            action_id="assign_reviewer",
            label="Assign reviewer",
            available=revision_state == RevisionReviewState.IN_REVIEW.value,
            detail=(
                "Assign a reviewer to move the in-review revision toward a decision."
                if revision_state == RevisionReviewState.IN_REVIEW.value
                else "A reviewer can only be assigned after the revision is in review."
            ),
        )
    )
    actions.append(
        action_from_gate(
            action_id="review_decision",
            label="Review decision",
            available=revision_state == RevisionReviewState.IN_REVIEW.value and assignment is not None,
            detail=(
                "A reviewer assignment exists and the revision is ready for an approval or rejection decision."
                if revision_state == RevisionReviewState.IN_REVIEW.value and assignment is not None
                else "Assign a reviewer before recording an approval or rejection decision."
            ),
        )
    )
    actions.append(
        action_from_gate(
            action_id="mark_suspect",
            label="Mark suspect",
            available=True,
            noop=str(state.trust_state or "") == "suspect",
            detail=(
                "This object is already in suspect posture."
                if str(state.trust_state or "") == "suspect"
                else "Mark the object suspect when an upstream change may have invalidated the guidance."
            ),
        )
    )
    actions.append(
        action_from_policy(
            action_id="supersede_object",
            label="Supersede object",
            decision=authority.evaluate_object_lifecycle_transition(
                state.object_lifecycle_state,
                ObjectLifecycleState.DEPRECATED.value,
            ),
        )
    )
    if current_revision_id is None:
        actions.append(
            action_from_gate(
                action_id="archive_object",
                label="Archive object",
                available=False,
                detail="Archive requires a current revision so the canonical content can move coherently.",
            )
        )
    else:
        actions.append(
            action_from_policy(
                action_id="archive_object",
                label="Archive object",
                decision=authority.evaluate_object_lifecycle_transition(
                    state.object_lifecycle_state,
                    ObjectLifecycleState.ARCHIVED.value,
                ),
            )
        )
    citation_count = int((evidence_status or {}).get("total_citations") or 0)
    actions.append(
        action_from_gate(
            action_id="request_evidence_revalidation",
            label="Request evidence revalidation",
            available=citation_count > 0,
            detail=(
                "Request explicit evidence follow-up for the current citations."
                if citation_count > 0
                else "No citations are attached to the current revision, so there is nothing to revalidate."
            ),
        )
    )
    return tuple(actions)


def build_review_actions(
    *,
    authority: PolicyAuthority,
    state: RuntimeStateSnapshot,
    assignments: list[dict[str, Any]],
) -> tuple[ActionDescriptor, ...]:
    revision_state = str(state.revision_review_state or "")
    assigned = bool(assignments)
    gate_detail = (
        "The revision is in review and has assignment context for a reviewer decision."
        if revision_state == RevisionReviewState.IN_REVIEW.value and assigned
        else "A revision can only be approved or rejected after it is in review and has reviewer assignment context."
    )
    base_available = revision_state == RevisionReviewState.IN_REVIEW.value and assigned
    if revision_state == RevisionReviewState.APPROVED.value:
        approve_action = action_from_policy(
            action_id="approve_revision",
            label="Approve revision",
            decision=authority.evaluate_revision_review_transition(
                revision_state,
                RevisionReviewState.APPROVED.value,
            ),
        )
    elif base_available:
        approve_action = action_from_policy(
            action_id="approve_revision",
            label="Approve revision",
            decision=authority.evaluate_revision_review_transition(
                revision_state,
                RevisionReviewState.APPROVED.value,
            ),
            detail=gate_detail,
        )
    else:
        approve_action = action_from_gate(
            action_id="approve_revision",
            label="Approve revision",
            available=False,
            detail=gate_detail,
        )

    if revision_state == RevisionReviewState.REJECTED.value:
        reject_action = action_from_policy(
            action_id="reject_revision",
            label="Reject revision",
            decision=authority.evaluate_revision_review_transition(
                revision_state,
                RevisionReviewState.REJECTED.value,
            ),
        )
    elif base_available:
        reject_action = action_from_policy(
            action_id="reject_revision",
            label="Reject revision",
            decision=authority.evaluate_revision_review_transition(
                revision_state,
                RevisionReviewState.REJECTED.value,
            ),
            detail=gate_detail,
        )
    else:
        reject_action = action_from_gate(
            action_id="reject_revision",
            label="Reject revision",
            available=False,
            detail=gate_detail,
        )
    return (
        action_from_gate(
            action_id="assign_reviewer",
            label="Assign reviewer",
            available=revision_state == RevisionReviewState.IN_REVIEW.value,
            detail=(
                "Assign or update reviewer routing while the revision is in review."
                if revision_state == RevisionReviewState.IN_REVIEW.value
                else "Reviewer assignment is only available for in-review revisions."
            ),
        ),
        approve_action,
        reject_action,
    )


def build_ui_projection(
    *,
    state: RuntimeStateSnapshot,
    posture: dict[str, Any],
    reasons: list[str] | tuple[str, ...] | None,
    actions: tuple[ActionDescriptor, ...],
) -> UiProjection:
    return UiProjection(
        state=state,
        use_guidance=build_use_guidance(state=state, posture=posture),
        reasons=tuple(str(item) for item in reasons or []),
        actions=actions,
    )
