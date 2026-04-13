from __future__ import annotations

import hashlib
from pathlib import Path

from papyrus.application.commands import (
    approve_revision_command,
    assign_reviewer_command,
    attach_evidence_snapshot_command,
    build_projection_command,
    create_object_command,
    create_revision_command,
    ingest_event_command,
    mark_evidence_stale_command,
    mark_object_suspect_due_to_change_command,
    record_validation_run_command,
    request_evidence_revalidation_command,
    submit_for_review_command,
)
from papyrus.application.queries import (
    impact_view_for_service,
    knowledge_object_detail,
    oversight_dashboard,
    review_queue,
)
from papyrus.infrastructure.paths import DB_PATH, ROOT

DEMO_SOURCE_ROOT = ROOT / "build" / "demo-source"
OPERATOR_SCENARIOS = (
    "service_degradation",
    "stale_knowledge",
    "conflicting_evidence",
    "review_backlog",
)


def _citation(*, title: str, ref: str, note: str, validity_status: str) -> dict[str, str | None]:
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
    citations: list[dict[str, str | None]],
    last_reviewed: str = "2026-04-07",
    review_cadence: str = "quarterly",
) -> dict[str, object]:
    return {
        "id": object_id,
        "title": title,
        "canonical_path": canonical_path,
        "summary": f"Operational guidance for {title.lower()}",
        "knowledge_object_type": object_type,
        "legacy_article_type": None,
        "object_lifecycle_state": "active",
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
        "references": [
            {"title": item["source_title"], "path": item["source_ref"], "note": item["note"]}
            for item in citations
        ],
        "change_log": [
            {
                "date": "2026-04-07",
                "summary": "Initial reviewed baseline.",
                "author": "local.operator",
            }
        ],
    }


def _runbook_payload(
    *,
    object_id: str,
    title: str,
    canonical_path: str,
    owner: str,
    services: list[str],
    citations: list[dict[str, str | None]],
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
        tags=["operator-ready"],
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
    citations: list[dict[str, str | None]],
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
        tags=["known-error"],
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
            "mitigations": [
                "Force a fresh sign-in and route high-impact users to fallback support."
            ],
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
    citations: list[dict[str, str | None]],
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
        tags=["service"],
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


def _approve_revision(
    database_path: Path,
    *,
    object_id: str,
    payload: dict[str, object],
    change_summary: str,
    actor: str,
    reviewer: str,
    source_root: Path = ROOT,
) -> str:
    revision = create_revision_command(
        database_path=database_path,
        source_root=source_root,
        object_id=object_id,
        normalized_payload=payload,
        body_markdown=f"## Revision Narrative\n\n{change_summary}",
        actor=actor,
        legacy_metadata=payload,
        change_summary=change_summary,
    )
    submit_for_review_command(
        database_path=database_path,
        source_root=source_root,
        object_id=object_id,
        revision_id=revision.revision_id,
        actor=actor,
        notes=change_summary,
    )
    assign_reviewer_command(
        database_path=database_path,
        source_root=source_root,
        object_id=object_id,
        revision_id=revision.revision_id,
        reviewer=reviewer,
        actor=actor,
        notes="Assign the initial reviewer for the baseline guidance.",
    )
    approve_revision_command(
        database_path=database_path,
        source_root=source_root,
        object_id=object_id,
        revision_id=revision.revision_id,
        reviewer=reviewer,
        actor=reviewer,
        notes="Approved for the initial local operator runtime.",
    )
    return revision.revision_id


def _citation_id_for_object(database_path: Path, object_id: str) -> str:
    detail = knowledge_object_detail(object_id, database_path=database_path)
    if not detail["citations"]:
        raise ValueError(f"seeded object has no current citations: {object_id}")
    return str(detail["citations"][0]["citation_id"])


def _queue_counts(database_path: Path) -> dict[str, int]:
    queue = review_queue(database_path=database_path)
    return {
        "review_required": len(queue["review_required"]),
        "stale_items": len(queue["stale_items"]),
        "weak_evidence_items": len(queue["weak_evidence_items"]),
        "ownership_items": len(queue["ownership_items"]),
    }


def _scenario_summary(
    *,
    scenario: str,
    database_path: Path,
    source_root: Path,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    dashboard = oversight_dashboard(database_path=database_path)
    summary = {
        "scenario": scenario,
        "database_path": str(database_path),
        "source_root": str(source_root),
        "trust_counts": dashboard["trust_counts"],
        "review_counts": dashboard["review_counts"],
        "queue_counts": _queue_counts(database_path),
    }
    if extra:
        summary.update(extra)
    return summary


def build_operator_demo_runtime(
    database_path: Path = DB_PATH, *, source_root: Path = DEMO_SOURCE_ROOT
) -> dict[str, object]:
    result = build_projection_command(database_path=database_path)
    actor = "local.operator"

    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-remote-access-service-record",
        object_type="service_record",
        title="Remote Access Service Record",
        summary="Operator-ready service record for remote access.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/services/remote-access-service-record.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-remote-access-vpn-recovery",
        object_type="runbook",
        title="Remote Access VPN Recovery",
        summary="Trusted runbook for VPN recovery.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/runbooks/remote-access-vpn-recovery.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-identity-service-record",
        object_type="service_record",
        title="Identity Service Record",
        summary="Service record for identity workflows with open risk.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/services/identity-service-record.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-identity-fallback-sign-in",
        object_type="runbook",
        title="Identity Fallback Sign-In Runbook",
        summary="Stale runbook for identity fallback access.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/runbooks/identity-fallback-sign-in.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-identity-token-refresh-failure",
        object_type="known_error",
        title="Identity Token Refresh Failure",
        summary="Change-triggered suspect known error for identity token failures.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/known-errors/identity-token-refresh-failure.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-password-reset-escalation",
        object_type="runbook",
        title="Password Reset Escalation Runbook",
        summary="In-review runbook waiting for governance approval.",
        owner="identity_ops",
        team="IT Operations",
        canonical_path="knowledge/runbooks/password-reset-escalation.md",
        actor=actor,
    )
    create_object_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-legacy-vpn-split-tunnel-failure",
        object_type="known_error",
        title="Legacy VPN Split-Tunnel Failure",
        summary="Weak-evidence known error retained for follow-up.",
        owner="remote_access_ops",
        team="IT Operations",
        canonical_path="knowledge/known-errors/legacy-vpn-split-tunnel-failure.md",
        actor=actor,
    )

    _approve_revision(
        database_path,
        object_id="kb-remote-access-service-record",
        payload=_service_record_payload(
            object_id="kb-remote-access-service-record",
            title="Remote Access Service Record",
            canonical_path="knowledge/services/remote-access-service-record.md",
            owner="remote_access_ops",
            service_name="Remote Access",
            citations=[
                _citation(
                    title="Remote Access ownership matrix",
                    ref="docs/reference/system-model.md",
                    note="Verified ownership reference.",
                    validity_status="verified",
                )
            ],
            related_runbooks=["kb-remote-access-vpn-recovery"],
            related_known_errors=[
                "kb-troubleshooting-vpn-connectivity",
                "kb-legacy-vpn-split-tunnel-failure",
            ],
        ),
        change_summary="Initial healthy remote-access service record.",
        actor=actor,
        reviewer="manager.remote-access",
        source_root=source_root,
    )
    _approve_revision(
        database_path,
        object_id="kb-remote-access-vpn-recovery",
        payload=_runbook_payload(
            object_id="kb-remote-access-vpn-recovery",
            title="Remote Access VPN Recovery",
            canonical_path="knowledge/runbooks/remote-access-vpn-recovery.md",
            owner="remote_access_ops",
            services=["Remote Access"],
            citations=[
                _citation(
                    title="VPN recovery validation",
                    ref="docs/playbooks/read.md",
                    note="Verified recovery reference.",
                    validity_status="verified",
                )
            ],
            related_object_ids=[
                "kb-remote-access-service-record",
                "kb-troubleshooting-vpn-connectivity",
            ],
        ),
        change_summary="Initial approved remote-access recovery runbook.",
        actor=actor,
        reviewer="manager.remote-access",
        source_root=source_root,
    )
    _approve_revision(
        database_path,
        object_id="kb-identity-service-record",
        payload=_service_record_payload(
            object_id="kb-identity-service-record",
            title="Identity Service Record",
            canonical_path="knowledge/services/identity-service-record.md",
            owner="identity_ops",
            service_name="Identity",
            citations=[
                _citation(
                    title="Identity support model",
                    ref="docs/playbooks/manage.md",
                    note="Verified support reference.",
                    validity_status="verified",
                )
            ],
            related_runbooks=["kb-identity-fallback-sign-in", "kb-password-reset-escalation"],
            related_known_errors=["kb-identity-token-refresh-failure"],
        ),
        change_summary="Initial identity service record.",
        actor=actor,
        reviewer="manager.identity",
        source_root=source_root,
    )
    _approve_revision(
        database_path,
        object_id="kb-identity-fallback-sign-in",
        payload=_runbook_payload(
            object_id="kb-identity-fallback-sign-in",
            title="Identity Fallback Sign-In Runbook",
            canonical_path="knowledge/runbooks/identity-fallback-sign-in.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[
                _citation(
                    title="Fallback access SOP",
                    ref="docs/playbooks/write.md",
                    note="Verified fallback reference.",
                    validity_status="verified",
                )
            ],
            related_object_ids=["kb-identity-service-record", "kb-identity-token-refresh-failure"],
            last_reviewed="2024-01-15",
            review_cadence="quarterly",
        ),
        change_summary="Initial identity fallback runbook now intentionally stale.",
        actor=actor,
        reviewer="manager.identity",
        source_root=source_root,
    )
    _approve_revision(
        database_path,
        object_id="kb-identity-token-refresh-failure",
        payload=_known_error_payload(
            object_id="kb-identity-token-refresh-failure",
            title="Identity Token Refresh Failure",
            canonical_path="knowledge/known-errors/identity-token-refresh-failure.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[
                _citation(
                    title="Identity change record",
                    ref="docs/reference/operator-web-ui.md",
                    note="Verified change reference.",
                    validity_status="verified",
                )
            ],
            related_object_ids=["kb-identity-service-record", "kb-identity-fallback-sign-in"],
        ),
        change_summary="Approved known error before dependency drift.",
        actor=actor,
        reviewer="manager.identity",
        source_root=source_root,
    )
    mark_object_suspect_due_to_change_command(
        database_path=database_path,
        object_id="kb-identity-token-refresh-failure",
        actor=actor,
        reason="Upstream identity policy changed and token behavior must be revalidated.",
        changed_entity_type="service",
        changed_entity_id="Identity",
    )
    _approve_revision(
        database_path,
        object_id="kb-legacy-vpn-split-tunnel-failure",
        payload=_known_error_payload(
            object_id="kb-legacy-vpn-split-tunnel-failure",
            title="Legacy VPN Split-Tunnel Failure",
            canonical_path="knowledge/known-errors/legacy-vpn-split-tunnel-failure.md",
            owner="remote_access_ops",
            services=["Remote Access"],
            citations=[
                _citation(
                    title="Legacy split-tunnel notes",
                    ref="docs/reference/operator-web-ui.md",
                    note="Imported note not yet re-verified.",
                    validity_status="unverified",
                )
            ],
            related_object_ids=["kb-remote-access-service-record", "kb-remote-access-vpn-recovery"],
        ),
        change_summary="Known error preserved with weak evidence for follow-up.",
        actor=actor,
        reviewer="manager.remote-access",
        source_root=source_root,
    )

    pending_revision = create_revision_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-password-reset-escalation",
        normalized_payload=_runbook_payload(
            object_id="kb-password-reset-escalation",
            title="Password Reset Escalation Runbook",
            canonical_path="knowledge/runbooks/password-reset-escalation.md",
            owner="identity_ops",
            services=["Identity"],
            citations=[
                _citation(
                    title="Password reset checklist",
                    ref="knowledge/access/password-reset-account-lockout.md",
                    note="Ready for review.",
                    validity_status="verified",
                )
            ],
            related_object_ids=[
                "kb-identity-service-record",
                "kb-access-password-reset-account-lockout",
            ],
        ),
        body_markdown="## Revision Narrative\n\nPending review because the escalation threshold changed.",
        actor=actor,
        legacy_metadata={},
        change_summary="Submit password reset escalation changes for review.",
    )
    submit_for_review_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-password-reset-escalation",
        revision_id=pending_revision.revision_id,
        actor=actor,
        notes="Queue for approval after the escalation threshold change.",
    )
    assign_reviewer_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-password-reset-escalation",
        revision_id=pending_revision.revision_id,
        reviewer="manager.identity",
        actor=actor,
        notes="Route the revision into the live review queue.",
    )

    record_validation_run_command(
        database_path=database_path,
        run_id="operator-readiness-check-20260407",
        run_type="manual_operator_check",
        status="warning",
        finding_count=3,
        details={
            "scenario": "operator_readiness_runtime",
            "summary": "The local runtime contains one stale runbook, one weak-evidence known error, and one in-review runbook.",
        },
        actor=actor,
    )
    attach_evidence_snapshot_command(
        database_path=database_path,
        citation_id=_citation_id_for_object(database_path, "kb-remote-access-service-record"),
        snapshot_source_path=source_root
        / "knowledge"
        / "services"
        / "remote-access-service-record.md",
        actor=actor,
        expires_at="2026-07-01T00:00:00+00:00",
        root_path=source_root,
    )
    stale_evidence = mark_evidence_stale_command(
        database_path=database_path,
        object_id="kb-legacy-vpn-split-tunnel-failure",
        actor=actor,
        reason="Imported note lacks a current evidence snapshot and needs revalidation.",
    )
    revalidation = request_evidence_revalidation_command(
        database_path=database_path,
        object_id="kb-identity-fallback-sign-in",
        actor=actor,
        notes="Quarterly review found stale identity fallback guidance.",
    )
    change_event = ingest_event_command(
        database_path=database_path,
        event_type="validation_failure",
        source="local",
        entity_type="knowledge_object",
        entity_id="kb-legacy-vpn-split-tunnel-failure",
        payload={
            "summary": "Legacy VPN split-tunnel validation no longer matches the imported note.",
            "object_ids": ["kb-legacy-vpn-split-tunnel-failure"],
        },
        actor=actor,
    )

    return {
        "database_path": str(result.database_path),
        "source_root": str(source_root),
        "document_count": result.document_count,
        "demo_objects": [
            "kb-remote-access-service-record",
            "kb-remote-access-vpn-recovery",
            "kb-identity-service-record",
            "kb-identity-fallback-sign-in",
            "kb-identity-token-refresh-failure",
            "kb-password-reset-escalation",
            "kb-legacy-vpn-split-tunnel-failure",
        ],
        "demo_actions": {
            "stale_citation_ids": stale_evidence.citation_ids,
            "revalidation_object_id": revalidation.object_id,
            "change_event_id": change_event.event_id,
        },
    }


def run_operator_scenario(
    *,
    scenario: str,
    database_path: Path = DB_PATH,
    source_root: Path = DEMO_SOURCE_ROOT,
    actor: str = "local.operator",
) -> dict[str, object]:
    normalized = scenario.strip().lower().replace("-", "_")
    if normalized not in OPERATOR_SCENARIOS:
        raise ValueError(f"unsupported scenario: {scenario}")

    base_runtime = build_operator_demo_runtime(database_path=database_path, source_root=source_root)

    if normalized == "service_degradation":
        event = ingest_event_command(
            database_path=database_path,
            event_type="service_change",
            source="local",
            entity_type="service",
            entity_id="Remote Access",
            payload={
                "summary": "Remote Access failover behavior changed after a network maintenance window."
            },
            actor=actor,
        )
        impact = impact_view_for_service("Remote Access", database_path=database_path)
        return _scenario_summary(
            scenario=normalized,
            database_path=database_path,
            source_root=source_root,
            extra={
                "demo_objects": base_runtime["demo_objects"],
                "event_id": event.event_id,
                "impacted_objects": impact["impacted_objects"],
            },
        )

    if normalized == "stale_knowledge":
        queue = review_queue(database_path=database_path)
        return _scenario_summary(
            scenario=normalized,
            database_path=database_path,
            source_root=source_root,
            extra={
                "demo_objects": base_runtime["demo_objects"],
                "stale_items": [
                    {
                        "object_id": item["object_id"],
                        "title": item["title"],
                        "trust_state": item["trust_state"],
                    }
                    for item in queue["stale_items"]
                ],
            },
        )

    if normalized == "conflicting_evidence":
        event = ingest_event_command(
            database_path=database_path,
            event_type="evidence_conflict",
            source="local",
            entity_type="evidence",
            entity_id="docs/reference/system-model.md",
            payload={
                "summary": "Conflicting operator notes were recorded against the remote-access service evidence.",
                "trust_state": "weak_evidence",
            },
            actor=actor,
        )
        detail = knowledge_object_detail(
            "kb-remote-access-service-record", database_path=database_path
        )
        return _scenario_summary(
            scenario=normalized,
            database_path=database_path,
            source_root=source_root,
            extra={
                "demo_objects": base_runtime["demo_objects"],
                "event_id": event.event_id,
                "object_id": detail["object"]["object_id"],
                "trust_state": detail["object"]["trust_state"],
                "evidence_status": detail["evidence_status"],
            },
        )

    detail = knowledge_object_detail("kb-remote-access-vpn-recovery", database_path=database_path)
    payload = dict(detail["metadata"])
    payload["updated"] = "2026-04-08"
    payload["last_reviewed"] = "2026-04-08"
    payload["change_log"] = [
        *(payload.get("change_log") if isinstance(payload.get("change_log"), list) else []),
        {"date": "2026-04-08", "summary": "Review backlog scenario follow-up.", "author": actor},
    ]
    revision = create_revision_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-remote-access-vpn-recovery",
        normalized_payload=payload,
        body_markdown="## Revision Narrative\n\nScenario backlog revision waiting for review.",
        actor=actor,
        legacy_metadata=detail["metadata"],
        change_summary="Queue another recovery update for review.",
    )
    submit_for_review_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-remote-access-vpn-recovery",
        revision_id=revision.revision_id,
        actor=actor,
        notes="Queue another review item to simulate backlog pressure.",
    )
    assign_reviewer_command(
        database_path=database_path,
        source_root=source_root,
        object_id="kb-remote-access-vpn-recovery",
        revision_id=revision.revision_id,
        reviewer="manager.remote-access",
        actor=actor,
        notes="Backlog scenario assignment.",
    )
    queue = review_queue(database_path=database_path)
    return _scenario_summary(
        scenario=normalized,
        database_path=database_path,
        source_root=source_root,
        extra={
            "demo_objects": base_runtime["demo_objects"],
            "revision_id": revision.revision_id,
            "review_required": [
                {
                    "object_id": item["object_id"],
                    "revision_id": item["revision_id"],
                    "title": item["title"],
                }
                for item in queue["review_required"]
            ],
        },
    )
