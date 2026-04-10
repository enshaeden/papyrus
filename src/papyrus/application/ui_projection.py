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
from papyrus.domain.blueprints import Blueprint
from papyrus.domain.ingestion import IngestionStatus, has_mapping_result
from papyrus.domain.lifecycle import (
    DraftProgressState,
    ObjectLifecycleState,
    RevisionReviewState,
    SourceSyncState,
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


@dataclass(frozen=True)
class ProjectionRow:
    label: str
    value: str


@dataclass(frozen=True)
class WorkflowProjection:
    code: str
    summary: str
    detail: str
    operator_message: str
    source_of_truth: str
    tone: str
    rows: tuple[ProjectionRow, ...]
    warnings: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()
    actions: tuple[ActionDescriptor | dict[str, Any], ...] = ()


@dataclass(frozen=True)
class ReferenceCandidateProjection:
    eligible: bool
    summary: str
    detail: str


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
        },
        "use_guidance": use_guidance_payload(projection.use_guidance),
        "reasons": list(projection.reasons),
        "actions": [action_descriptor_payload(action) for action in projection.actions],
    }


def workflow_projection_payload(projection: WorkflowProjection) -> dict[str, Any]:
    return {
        "code": projection.code,
        "summary": projection.summary,
        "detail": projection.detail,
        "operator_message": projection.operator_message,
        "source_of_truth": projection.source_of_truth,
        "tone": projection.tone,
        "rows": [{"label": row.label, "value": row.value} for row in projection.rows],
        "warnings": list(projection.warnings),
        "reasons": list(projection.reasons),
        "actions": [
            action_descriptor_payload(action) if isinstance(action, ActionDescriptor) else dict(action)
            for action in projection.actions
        ],
    }


def reference_candidate_payload(projection: ReferenceCandidateProjection) -> dict[str, Any]:
    return {
        "eligible": projection.eligible,
        "summary": projection.summary,
        "detail": projection.detail,
    }


def build_use_guidance(
    *,
    state: RuntimeStateSnapshot,
    posture: dict[str, Any],
) -> UseGuidanceProjection:
    revision_review_state = str(state.revision_review_state or "")
    trust_state = str(state.trust_state or "")
    source_sync_state = str(state.source_sync_state or "")
    if source_sync_state == SourceSyncState.CONFLICTED.value:
        return UseGuidanceProjection(
            code="source_sync_conflicted",
            summary="Canonical source conflict requires review",
            detail="Papyrus detected a source-sync conflict, so runtime guidance may no longer match canonical Markdown.",
            next_action="Inspect the writeback conflict and resolve canonical source divergence before relying on this guidance.",
            safe_to_use=False,
        )
    if source_sync_state == SourceSyncState.RESTORED.value:
        return UseGuidanceProjection(
            code="source_sync_restored",
            summary="Canonical source was restored",
            detail="Papyrus restored the canonical source, so operators must verify that runtime guidance still matches the restored Markdown.",
            next_action="Review the restore audit trail and re-apply or revise the governed revision before treating it as current.",
            safe_to_use=False,
        )
    if source_sync_state == SourceSyncState.PENDING.value:
        safe_to_use = revision_review_state == RevisionReviewState.APPROVED.value and trust_state == "trusted"
        return UseGuidanceProjection(
            code="source_sync_pending",
            summary="Runtime is ahead of canonical Markdown",
            detail="Papyrus is treating the runtime projection as current while canonical source sync is still pending.",
            next_action=(
                "Complete source writeback before relying on canonical Markdown as synchronized."
                if safe_to_use
                else str(
                    posture.get("approval", {}).get("action")
                    or "Resolve the review or trust posture first, then complete source sync."
                )
            ),
            safe_to_use=safe_to_use,
        )
    if revision_review_state == RevisionReviewState.APPROVED.value and trust_state == "trusted":
        return UseGuidanceProjection(
            code="safe_to_use",
            summary="Safe to use now",
            detail="The current revision is approved and the runtime trust posture is trusted.",
            next_action=str(posture.get("approval", {}).get("action") or "Use the current guidance."),
            safe_to_use=True,
        )
    if revision_review_state == RevisionReviewState.IN_REVIEW.value:
        return UseGuidanceProjection(
            code="review_pending",
            summary="Review decision pending",
            detail="The current revision is in review and should not be treated as canonical guidance yet.",
            next_action=str(posture.get("approval", {}).get("action") or "Use the last approved guidance or route the revision through review."),
            safe_to_use=False,
        )
    if revision_review_state in {RevisionReviewState.DRAFT.value, RevisionReviewState.REJECTED.value, ""}:
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
            detail="A completed review state is not enough here because the current evidence posture is weak or unverified.",
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


def build_draft_readiness_projection(
    *,
    blueprint: Blueprint,
    completion: dict[str, Any],
    submit_action: ActionDescriptor | dict[str, Any] | None,
) -> WorkflowProjection:
    draft_state = str(completion.get("draft_progress_state") or DraftProgressState.IN_PROGRESS.value)
    next_section_id = str(completion.get("next_section_id") or "").strip()
    next_section_label = (
        blueprint.section(next_section_id).display_name
        if next_section_id and next_section_id in set(blueprint.ordering)
        else "Review readiness"
    )
    evidence_posture = dict(completion.get("evidence_posture") or {})
    blockers = tuple(str(item) for item in completion.get("blockers", []) if str(item).strip())
    warnings = tuple(str(item) for item in completion.get("warnings", []) if str(item).strip())
    action_detail = ""
    if isinstance(submit_action, ActionDescriptor):
        action_detail = submit_action.detail
    elif isinstance(submit_action, dict):
        action_detail = str(submit_action.get("detail") or "")
    summary = "Draft is in progress"
    detail = "Required sections are partially complete, and Papyrus has identified the next section to continue."
    tone = "context"
    if draft_state == DraftProgressState.BLOCKED.value:
        summary = "Draft has blocking gaps"
        detail = "Required sections or fields are still incomplete, so the revision cannot move into review yet."
        tone = "warning"
    elif draft_state == DraftProgressState.READY_FOR_REVIEW.value:
        summary = "Draft is ready for review"
        detail = "Required sections are complete and the revision can move into the governed review flow."
        tone = "approved"
    return WorkflowProjection(
        code=f"draft_{draft_state}",
        summary=summary,
        detail=detail,
        operator_message=action_detail or detail,
        source_of_truth="draft_progress_validation",
        tone=tone,
        rows=(
            ProjectionRow("Draft progress", draft_state),
            ProjectionRow(
                "Completed required sections",
                f"{int(completion.get('completed_required_sections') or 0)} / {int(completion.get('required_section_count') or 0)}",
            ),
            ProjectionRow("Next section", next_section_label),
            ProjectionRow(
                "Evidence posture",
                str(evidence_posture.get("summary") or "No evidence references recorded yet."),
            ),
        ),
        warnings=warnings,
        reasons=blockers,
        actions=((submit_action,) if submit_action is not None else ()),
    )


def build_ingestion_actions(*, detail: dict[str, Any]) -> tuple[ActionDescriptor, ...]:
    ingestion_state = str(detail.get("ingestion_state") or IngestionStatus.UPLOADED.value)
    mapping_result = dict(detail.get("mapping_result") or {})
    mapped = has_mapping_result(mapping_result) or ingestion_state in {
        IngestionStatus.MAPPED.value,
        IngestionStatus.CONVERTED.value,
    }
    converted = bool(detail.get("converted_revision_id")) or ingestion_state == IngestionStatus.CONVERTED.value
    actions: list[ActionDescriptor] = [
        action_from_gate(
            action_id="review_ingestion_mapping",
            label="Review mapping" if mapped else "Generate mapping review",
            available=not converted,
            noop=False,
            detail=(
                "Open mapping review to inspect section matches, conflicts, and conversion gaps."
                if not converted
                else "This ingestion has already been converted into a governed draft."
            ),
        )
    ]
    actions.append(
        action_from_gate(
            action_id="convert_ingestion_to_draft",
            label="Create draft",
            available=mapped and not converted,
            detail=(
                "Create a draft from the reviewed mapping."
                if mapped and not converted
                else "Generate and review the mapping before creating a draft."
                if not mapped
                else "This ingestion has already been turned into a draft."
            ),
            noop=converted,
        )
    )
    if converted:
        actions.append(
            action_from_gate(
                action_id="open_converted_draft",
                label="Open converted draft",
                available=True,
                detail="Open the governed draft created from this ingestion.",
            )
        )
    return tuple(actions)


def build_ingestion_projection(*, detail: dict[str, Any]) -> WorkflowProjection:
    ingestion_state = str(detail.get("ingestion_state") or IngestionStatus.UPLOADED.value)
    mapping_result = dict(detail.get("mapping_result") or {})
    normalized = dict(detail.get("normalized_content") or {})
    classification = dict(detail.get("classification") or {})
    extraction_quality = dict(normalized.get("extraction_quality") or {})
    mapped = has_mapping_result(mapping_result) or ingestion_state in {
        IngestionStatus.MAPPED.value,
        IngestionStatus.CONVERTED.value,
    }
    converted = bool(detail.get("converted_revision_id")) or ingestion_state == IngestionStatus.CONVERTED.value
    missing_count = len(mapping_result.get("missing_sections", [])) if mapped else 0
    low_confidence_count = len(mapping_result.get("low_confidence", [])) if mapped else 0
    conflict_count = len(mapping_result.get("conflicts", [])) if mapped else 0
    warning_items = tuple(
        str(item)
        for item in [
            *normalized.get("parser_warnings", []),
            *normalized.get("degradation_notes", []),
        ]
        if str(item).strip()
    )
    summary = "Generate mapping review"
    detail_text = "Papyrus has parsed and classified the source, but section mapping has not been generated yet."
    operator_message = "Generate the mapping first, then inspect gaps before converting anything into a governed draft."
    tone = "context"
    if converted:
        summary = "Converted to governed draft"
        detail_text = "This ingestion has already been converted into a governed draft revision."
        operator_message = "Open the converted draft when you need to continue structured authoring or review."
        tone = "approved"
    elif mapped and (missing_count or low_confidence_count or conflict_count):
        summary = "Mapping review required"
        detail_text = "Papyrus generated a mapping, but it still has gaps or conflicts that require operator review."
        operator_message = "Review mapping conflicts and missing sections before deciding whether to convert."
        tone = "warning"
    elif mapped:
        summary = "Ready to convert to draft"
        detail_text = "Papyrus generated a mapping and no missing or conflicted sections are currently flagged."
        operator_message = "Review the mapping and convert it into a governed draft when you are satisfied with the current import result."
        tone = "approved"
    return WorkflowProjection(
        code=f"ingestion_{ingestion_state}",
        summary=summary,
        detail=detail_text,
        operator_message=operator_message,
        source_of_truth="ingestion_artifacts",
        tone=tone,
        rows=(
            ProjectionRow("Ingestion state", ingestion_state),
            ProjectionRow(
                "Suggested blueprint",
                str(detail.get("blueprint_id") or classification.get("blueprint_id") or "unknown"),
            ),
            ProjectionRow("Parser quality", str(extraction_quality.get("state") or "unknown")),
            ProjectionRow("Missing required sections", str(missing_count)),
            ProjectionRow("Low-confidence mappings", str(low_confidence_count)),
            ProjectionRow("Mapping conflicts", str(conflict_count)),
        ),
        warnings=warning_items,
        reasons=tuple(str(item) for item in classification.get("reasons", []) if str(item).strip()),
        actions=build_ingestion_actions(detail=detail),
    )


def build_reference_candidate_projection(
    *,
    current_revision: dict[str, Any] | None,
    citations: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
) -> ReferenceCandidateProjection:
    if current_revision is None:
        return ReferenceCandidateProjection(
            eligible=False,
            summary="No current revision",
            detail="Papyrus cannot cite or relate a knowledge object that has no current revision.",
        )
    body_markdown = str(current_revision.get("body_markdown") or "").strip()
    revision_state = str(
        current_revision.get("revision_review_state")
        or current_revision.get("revision_state")
        or ""
    ).strip()
    citation_count = len(citations or [])
    if revision_state == RevisionReviewState.DRAFT.value and not body_markdown and citation_count == 0:
        return ReferenceCandidateProjection(
            eligible=False,
            summary="Draft shell is empty",
            detail="Papyrus excludes empty draft shells from citation and relationship pickers until they contain content or evidence.",
        )
    return ReferenceCandidateProjection(
        eligible=True,
        summary="Current revision can be referenced",
        detail="Papyrus can use this current revision as a reference candidate in authoring flows.",
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
