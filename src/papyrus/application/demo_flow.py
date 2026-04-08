from __future__ import annotations

import hashlib
from pathlib import Path

from papyrus.application.commands import (
    assign_reviewer_command,
    approve_revision_command,
    build_projection_command,
    create_object_command,
    create_revision_command,
    mark_object_suspect_due_to_change_command,
    record_validation_run_command,
    submit_for_review_command,
)
from papyrus.infrastructure.paths import DB_PATH


def _citation(*, title: str, ref: str, note: str, validity_status: str) -> dict[str, str]:
    return {
        "source_title": title,
        "source_type": "document",
        "source_ref": ref,
        "note": note,
        "claim_anchor": "operator-claim",
        "excerpt": None,
        "captured_at": "2026-04-07T09:00:00+00:00",
        "validity_status": validity_status,
        "integrity_hash": hashlib.sha256(ref.encode("utf-8")).hexdigest()[:16],
    }


def _common_payload(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    object_type: str,
    owner: str,
    services: list[str],
    systems: list[str],
    tags: list[str],
    citations: list[dict[str, str]],
    last_reviewed: str = "2026-04-07",
    review_cadence: str = "quarterly",
) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Demo scenario object for {title.lower()}",
        "knowledge_object_type": object_type,
        "legacy_article_type": None,
        "status": "active",
        "owner": owner,
        "source_type": "native",
        "source_system": "repository",
        "source_title": title,
        "team": "IT Operations",
        "systems": systems,
        "tags": tags,
        "created": "2026-04-07",
        "updated": "2026-04-07",
        "last_reviewed": last_reviewed,
        "review_cadence": review_cadence,
        "audience": "service_desk",
        "citations": citations,
        "related_object_ids": [],
        "superseded_by": None,
        "retirement_reason": None,
        "services": services,
        "related_articles": [],
        "references": [{"title": item["source_title"], "path": item["source_ref"], "note": item["note"]} for item in citations],
        "change_log": [{"date": "2026-04-07", "summary": "Scenario seed revision.", "author": "papyrus-demo"}],
    }


def _runbook_payload(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    services: list[str],
    citations: list[dict[str, str]],
    related_object_ids: list[str],
    last_reviewed: str = "2026-04-07",
    review_cadence: str = "quarterly",
) -> dict[str, object]:
    payload = _common_payload(
        object_id=object_id,
        title=title,
        canonical_path=canonical_path,
        object_type="runbook",
        owner=owner,
        services=services,
        systems=["<VPN_SERVICE>"] if "Remote Access" in services else ["<IDENTITY_PROVIDER>"],
        tags=["demo", "operator-ready"],
        citations=citations,
        last_reviewed=last_reviewed,
        review_cadence=review_cadence,
    )
    payload.update(
        {
            "related_services": services,
            "related_object_ids": related_object_ids,
            "related_articles": related_object_ids,
            "prerequisites": ["Ticket is opened and scoped."],
            "steps": ["Execute the documented operator action."],
            "verification": ["Confirm the user-impact check passes."],
            "rollback": ["Back out the last change and escalate."],
        }
    )
    return payload


def _known_error_payload(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    services: list[str],
    citations: list[dict[str, str]],
    related_object_ids: list[str],
) -> dict[str, object]:
    payload = _common_payload(
        object_id=object_id,
        title=title,
        canonical_path=canonical_path,
        object_type="known_error",
        owner=owner,
        services=services,
        systems=["<IDENTITY_PROVIDER>"],
        tags=["demo", "known-error"],
        citations=citations,
    )
    payload.update(
        {
            "related_services": services,
            "related_object_ids": related_object_ids,
            "related_articles": related_object_ids,
            "symptoms": ["Users cannot refresh tokens after the upstream change."],
            "scope": "Identity workflows backed by cached refresh tokens.",
            "cause": "Upstream identity policy changed before downstream runbooks were reviewed.",
            "diagnostic_checks": ["Confirm the identity policy revision applied."],
            "mitigations": ["Force a fresh sign-in and route high-impact users to fallback support."],
            "permanent_fix_status": "planned",
        }
    )
    return payload


def _service_record_payload(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    service_name: str,
    citations: list[dict[str, str]],
    related_runbooks: list[str],
    related_known_errors: list[str],
) -> dict[str, object]:
    payload = _common_payload(
        object_id=object_id,
        title=title,
        canonical_path=canonical_path,
        object_type="service_record",
        owner=owner,
        services=[service_name],
        systems=["<VPN_SERVICE>"] if service_name == "Remote Access" else ["<IDENTITY_PROVIDER>"],
        tags=["demo", "service"],
        citations=citations,
    )
    payload.update(
        {
            "service_name": service_name,
            "service_criticality": "high",
            "dependencies": ["Identity"] if service_name == "Remote Access" else ["Remote Access"],
            "support_entrypoints": ["Primary helpdesk", "Escalation manager"],
            "common_failure_modes": ["Authentication drift", "License saturation"],
            "related_runbooks": related_runbooks,
            "related_known_errors": related_known_errors,
        }
    )
    return payload


def _approve_revision(database_path: Path, *, object_id: str, payload: dict[str, object], change_summary: str, actor: str, reviewer: str) -> str:
    revision = create_revision_command(
        database_path=database_path,
        object_id=object_id,
        normalized_payload=payload,
        body_markdown=f"## Demo Narrative\n\n{change_summary}",
        actor=actor,
        legacy_metadata=payload,
        change_summary=change_summary,
    )
    submit_for_review_command(database_path=database_path, object_id=object_id, revision_id=revision.revision_id, actor=actor, notes=change_summary)
    assign_reviewer_command(
        database_path=database_path,
        object_id=object_id,
        revision_id=revision.revision_id,
        reviewer=reviewer,
        actor=actor,
        notes="Demo review assignment.",
    )
    approve_revision_command(
        database_path=database_path,
        object_id=object_id,
        revision_id=revision.revision_id,
        reviewer=reviewer,
        actor=actor,
        notes="Approved for the operator-readiness demo.",
    )
    return revision.revision_id


def build_operator_demo_runtime(database_path: Path = DB_PATH) -> dict[str, object]:
    result = build_projection_command(database_path=database_path)
    actor = "papyrus-demo"

    create_object_command(
        database_path=database_path,
        object_id="kb-demo-remote-access-service-record",
        object_type="service_record",
        title="Remote Access Service Record",
        summary="Operator-ready demo service record for remote access.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/remote-access-service-record.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-vpn-recovery-runbook",
        object_type="runbook",
        title="Remote Access VPN Recovery",
        summary="Trusted demo runbook for VPN recovery.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/remote-access-vpn-recovery.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-identity-service-record",
        object_type="service_record",
        title="Identity Service Record",
        summary="Degraded demo service record for identity workflows.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/identity-service-record.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-identity-fallback-runbook",
        object_type="runbook",
        title="Identity Fallback Sign-In Runbook",
        summary="Stale demo runbook for identity fallback access.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/identity-fallback-sign-in.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-identity-token-known-error",
        object_type="known_error",
        title="Identity Token Refresh Failure",
        summary="Change-triggered suspect known error for identity token failures.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/identity-token-refresh-failure.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-password-reset-runbook",
        object_type="runbook",
        title="Password Reset Escalation Runbook",
        summary="In-review runbook waiting for governance approval.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/password-reset-escalation.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        object_id="kb-demo-evidence-gap-known-error",
        object_type="known_error",
        title="Legacy VPN Split-Tunnel Failure",
        summary="Weak-evidence known error preserved for demo tension.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/demo/legacy-vpn-split-tunnel-failure.md",
        actor=actor,
    )

    _approve_revision(
        database_path,
        object_id="kb-demo-remote-access-service-record",
        payload=_service_record_payload(
            object_id="kb-demo-remote-access-service-record",
            title="Remote Access Service Record",
            canonical_path="knowledge/demo/remote-access-service-record.md",
            owner="remote_access_ops",
            service_name="Remote Access",
            citations=[_citation(title="Remote Access ownership matrix", ref="docs/reference/system-model.md", note="Demo evidence.", validity_status="verified")],
            related_runbooks=["kb-demo-vpn-recovery-runbook"],
            related_known_errors=["kb-troubleshooting-vpn-connectivity", "kb-demo-evidence-gap-known-error"],
        ),
        change_summary="Initial healthy remote-access service record.",
        actor=actor,
        reviewer="manager.remote-access",
    )
    _approve_revision(
        database_path,
        object_id="kb-demo-vpn-recovery-runbook",
        payload=_runbook_payload(
            object_id="kb-demo-vpn-recovery-runbook",
            title="Remote Access VPN Recovery",
            canonical_path="knowledge/demo/remote-access-vpn-recovery.md",
            owner="remote_access_ops",
            services=["Remote Access"],
            citations=[_citation(title="VPN recovery validation", ref="docs/playbooks/read.md", note="Demo verified evidence.", validity_status="verified")],
            related_object_ids=["kb-demo-remote-access-service-record", "kb-troubleshooting-vpn-connectivity"],
        ),
        change_summary="Initial approved remote-access recovery runbook.",
        actor=actor,
        reviewer="manager.remote-access",
    )
    _approve_revision(
        database_path,
        object_id="kb-demo-identity-service-record",
        payload=_service_record_payload(
            object_id="kb-demo-identity-service-record",
            title="Identity Service Record",
            canonical_path="knowledge/demo/identity-service-record.md",
            owner="identity_ops",
            service_name="Identity",
            citations=[_citation(title="Identity support model", ref="docs/playbooks/manage.md", note="Demo evidence.", validity_status="verified")],
            related_runbooks=["kb-demo-identity-fallback-runbook", "kb-demo-password-reset-runbook"],
            related_known_errors=["kb-demo-identity-token-known-error"],
        ),
        change_summary="Initial identity service record.",
        actor=actor,
        reviewer="manager.identity",
    )
    _approve_revision(
        database_path,
        object_id="kb-demo-identity-fallback-runbook",
        payload=_runbook_payload(
            object_id="kb-demo-identity-fallback-runbook",
            title="Identity Fallback Sign-In Runbook",
            canonical_path="knowledge/demo/identity-fallback-sign-in.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[_citation(title="Fallback access SOP", ref="docs/playbooks/write.md", note="Demo evidence.", validity_status="verified")],
            related_object_ids=["kb-demo-identity-service-record", "kb-demo-identity-token-known-error"],
            last_reviewed="2024-01-15",
            review_cadence="quarterly",
        ),
        change_summary="Initial identity fallback runbook now intentionally stale.",
        actor=actor,
        reviewer="manager.identity",
    )
    _approve_revision(
        database_path,
        object_id="kb-demo-identity-token-known-error",
        payload=_known_error_payload(
            object_id="kb-demo-identity-token-known-error",
            title="Identity Token Refresh Failure",
            canonical_path="knowledge/demo/identity-token-refresh-failure.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[_citation(title="Identity change record", ref="docs/reference/operator-web-ui.md", note="Demo evidence.", validity_status="verified")],
            related_object_ids=["kb-demo-identity-service-record", "kb-demo-identity-fallback-runbook"],
        ),
        change_summary="Approved known error before dependency drift.",
        actor=actor,
        reviewer="manager.identity",
    )
    mark_object_suspect_due_to_change_command(
        database_path=database_path,
        object_id="kb-demo-identity-token-known-error",
        actor=actor,
        reason="Upstream identity policy changed and token behavior must be revalidated.",
        changed_entity_type="service",
        changed_entity_id="Identity",
    )
    _approve_revision(
        database_path,
        object_id="kb-demo-evidence-gap-known-error",
        payload=_known_error_payload(
            object_id="kb-demo-evidence-gap-known-error",
            title="Legacy VPN Split-Tunnel Failure",
            canonical_path="knowledge/demo/legacy-vpn-split-tunnel-failure.md",
            owner="remote_access_ops",
            services=["Remote Access"],
            citations=[_citation(title="Legacy split-tunnel notes", ref="docs/reference/operator-web-ui.md", note="Imported note not yet re-verified.", validity_status="unverified")],
            related_object_ids=["kb-demo-remote-access-service-record", "kb-demo-vpn-recovery-runbook"],
        ),
        change_summary="Known error preserved with weak evidence for demo.",
        actor=actor,
        reviewer="manager.remote-access",
    )

    pending_revision = create_revision_command(
        database_path=database_path,
        object_id="kb-demo-password-reset-runbook",
        normalized_payload=_runbook_payload(
            object_id="kb-demo-password-reset-runbook",
            title="Password Reset Escalation Runbook",
            canonical_path="knowledge/demo/password-reset-escalation.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[_citation(title="Password reset checklist", ref="knowledge/access/password-reset-account-lockout.md", note="Ready for review.", validity_status="verified")],
            related_object_ids=["kb-demo-identity-service-record", "kb-access-password-reset-account-lockout"],
        ),
        body_markdown="## Demo Narrative\n\nPending review because the escalation threshold changed.",
        actor=actor,
        legacy_metadata={},
        change_summary="Submit password reset escalation changes for review.",
    )
    submit_for_review_command(
        database_path=database_path,
        object_id="kb-demo-password-reset-runbook",
        revision_id=pending_revision.revision_id,
        actor=actor,
        notes="Queue for manager approval during the demo.",
    )
    assign_reviewer_command(
        database_path=database_path,
        object_id="kb-demo-password-reset-runbook",
        revision_id=pending_revision.revision_id,
        reviewer="manager.identity",
        actor=actor,
        notes="Review queue scenario for operator demo.",
    )

    record_validation_run_command(
        database_path=database_path,
        run_id="demo-operator-check-20260407",
        run_type="manual_operator_check",
        status="warning",
        finding_count=3,
        details={
            "scenario": "operator_ready_demo",
            "summary": "Demo runtime contains one stale runbook, one weak-evidence known error, and one in-review runbook.",
        },
        actor=actor,
    )

    return {
        "database_path": str(result.database_path),
        "document_count": result.document_count,
        "demo_objects": [
            "kb-demo-remote-access-service-record",
            "kb-demo-vpn-recovery-runbook",
            "kb-demo-identity-service-record",
            "kb-demo-identity-fallback-runbook",
            "kb-demo-identity-token-known-error",
            "kb-demo-password-reset-runbook",
            "kb-demo-evidence-gap-known-error",
        ],
    }
