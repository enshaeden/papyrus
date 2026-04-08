"""Review workflow surface reserved for later phases."""

from __future__ import annotations

from papyrus.domain.entities import AuditEvent, ReviewAssignment


class ReviewWorkflow:
    """Phase 5 placeholder for deterministic review and approval flows."""

    def submit_for_review(self, assignment: ReviewAssignment) -> AuditEvent:
        raise NotImplementedError("Review workflows are introduced in a later phase.")

