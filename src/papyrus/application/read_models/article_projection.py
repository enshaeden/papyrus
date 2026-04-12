from __future__ import annotations

from typing import Any

from papyrus.domain.actor import resolve_actor


def _clean_text(value: object) -> str:
    return str(value or "").strip()


def _clean_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _paragraph_block(text: object, *, title: str = "") -> dict[str, Any] | None:
    normalized = _clean_text(text)
    if not normalized:
        return None
    return {"kind": "paragraph", "title": title, "text": normalized}


def _list_block(items: object, *, title: str = "") -> dict[str, Any] | None:
    normalized = _clean_list(items)
    if not normalized:
        return None
    return {"kind": "list", "title": title, "items": normalized}


def _facts_block(rows: list[tuple[str, object]], *, title: str = "") -> dict[str, Any] | None:
    normalized_rows = [(label, _clean_text(value)) for label, value in rows if _clean_text(value)]
    if not normalized_rows:
        return None
    return {"kind": "facts", "title": title, "rows": normalized_rows}


def _service_context(related_services: list[dict[str, Any]], item: dict[str, Any]) -> dict[str, Any]:
    return {
        "section_id": "service_context",
        "title": "Linked service context",
        "eyebrow": "Context",
        "blocks": [
            _list_block(
                [
                    f"{service['service_name']} ({service['service_criticality']} · {service['status']})"
                    for service in related_services
                ]
            ),
            _facts_block(
                [
                    ("Systems", ", ".join(str(entry) for entry in item.get("systems") or [])),
                    ("Tags", ", ".join(str(entry) for entry in item.get("tags") or [])),
                ]
            ),
        ],
        "empty": "No linked service context is recorded.",
    }


def _governance_context(item: dict[str, Any], ui_projection: dict[str, Any], evidence_status: dict[str, Any]) -> dict[str, Any]:
    use_guidance = dict(ui_projection.get("use_guidance") or {})
    state = dict(ui_projection.get("state") or {})
    return {
        "section_id": "governance",
        "title": "Governance and readiness",
        "eyebrow": "Governance",
        "blocks": [
            _paragraph_block(use_guidance.get("summary"), title="Use now"),
            _paragraph_block(use_guidance.get("detail"), title="Guardrail"),
            _facts_block(
                [
                    ("Trust", state.get("trust_state") or item.get("trust_state")),
                    ("Review", state.get("revision_review_state") or item.get("revision_review_state")),
                    ("Lifecycle", state.get("object_lifecycle_state") or item.get("object_lifecycle_state")),
                    ("Owner", item.get("owner")),
                    ("Team", item.get("team")),
                    ("Last reviewed", item.get("last_reviewed")),
                    ("Review cadence", item.get("review_cadence")),
                    ("Evidence posture", evidence_status.get("summary")),
                ]
            ),
        ],
    }


def _evidence_context(citations: list[dict[str, Any]], evidence_status: dict[str, Any]) -> dict[str, Any]:
    return {
        "section_id": "evidence",
        "title": "Evidence",
        "eyebrow": "Evidence",
        "blocks": [
            _facts_block(
                [
                    ("Citations", evidence_status.get("total_citations")),
                    ("Snapshots", evidence_status.get("snapshot_count")),
                    ("Needs revalidation", evidence_status.get("revalidation_count")),
                    ("Stale or broken", evidence_status.get("stale_count")),
                ]
            ),
            _list_block(
                [
                    f"{citation['source_title']} ({citation['validity_status']})"
                    for citation in citations
                    if citation.get("source_title")
                ],
                title="Sources",
            ),
        ],
    }


def _change_context(revision: dict[str, Any] | None, audit_events: list[dict[str, Any]]) -> dict[str, Any]:
    latest_audit = audit_events[0] if audit_events else None
    latest_audit_text = ""
    if latest_audit is not None:
        latest_audit_text = (
            f"{latest_audit['event_type']} at {latest_audit['occurred_at']} by {latest_audit['actor']}"
        )
    return {
        "section_id": "audit",
        "title": "Change and audit context",
        "eyebrow": "Change",
        "blocks": [
            _paragraph_block((revision or {}).get("change_summary"), title="Revision change"),
            _paragraph_block(latest_audit_text, title="Latest audit"),
        ],
    }


def _source_context(revision: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "section_id": "source",
        "title": "Revision source",
        "eyebrow": "Source",
        "blocks": [
            _facts_block(
                [
                    ("Revision", f"#{revision['revision_number']}" if revision is not None else ""),
                    ("Review state", (revision or {}).get("revision_review_state")),
                    ("Imported", (revision or {}).get("imported_at")),
                ]
            ),
        ],
        "raw_markdown": _clean_text((revision or {}).get("body_markdown")),
    }


def _section(section_id: str, title: str, *, eyebrow: str, blocks: list[dict[str, Any] | None], empty: str) -> dict[str, Any]:
    return {
        "section_id": section_id,
        "title": title,
        "eyebrow": eyebrow,
        "blocks": [block for block in blocks if block is not None],
        "empty": empty,
    }


def _runbook_sections(section_content: dict[str, dict[str, Any]], metadata: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    purpose = section_content.get("purpose", {})
    boundaries = section_content.get("boundaries", {})
    return [
        _section(
            "when_to_use",
            "When to use",
            eyebrow="Read",
            blocks=[_paragraph_block(purpose.get("use_when") or metadata.get("use_when"))],
            empty="No trigger guidance is recorded.",
        ),
        _section(
            "scope",
            "Prerequisites and scope",
            eyebrow="Scope",
            blocks=[
                _list_block(section_content.get("prerequisites", {}).get("prerequisites") or metadata.get("prerequisites")),
                _facts_block(
                    [
                        ("Audience", metadata.get("audience")),
                        ("Owner", item.get("owner")),
                    ]
                ),
            ],
            empty="No prerequisites or scope notes are recorded.",
        ),
        _section(
            "guidance",
            "Steps and guidance",
            eyebrow="Guide",
            blocks=[_list_block(section_content.get("procedure", {}).get("steps") or metadata.get("steps"), title="Steps")],
            empty="No guided steps are recorded.",
        ),
        _section(
            "verification",
            "Verification",
            eyebrow="Verify",
            blocks=[_list_block(section_content.get("verification", {}).get("verification") or metadata.get("verification"))],
            empty="No verification checks are recorded.",
        ),
        _section(
            "rollback",
            "Rollback and recovery",
            eyebrow="Recover",
            blocks=[_list_block(section_content.get("rollback", {}).get("rollback") or metadata.get("rollback"))],
            empty="No rollback or recovery steps are recorded.",
        ),
        _section(
            "escalation",
            "Escalation and boundaries",
            eyebrow="Escalate",
            blocks=[
                _paragraph_block(boundaries.get("boundaries_and_escalation") or metadata.get("boundaries_and_escalation")),
                _paragraph_block(boundaries.get("related_knowledge_notes"), title="Related knowledge"),
            ],
            empty="No escalation boundary is recorded.",
        ),
    ]


def _known_error_sections(section_content: dict[str, dict[str, Any]], metadata: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    diagnosis = section_content.get("diagnosis", {})
    escalation = section_content.get("escalation", {})
    return [
        _section(
            "when_to_use",
            "When to use",
            eyebrow="Read",
            blocks=[
                _list_block(diagnosis.get("symptoms") or metadata.get("symptoms"), title="Symptoms"),
                _paragraph_block(diagnosis.get("scope") or metadata.get("scope"), title="Scope"),
            ],
            empty="No trigger pattern is recorded.",
        ),
        _section(
            "scope",
            "Prerequisites and scope",
            eyebrow="Scope",
            blocks=[
                _paragraph_block(diagnosis.get("cause") or metadata.get("cause"), title="Cause"),
                _facts_block([("Owner", item.get("owner")), ("Audience", metadata.get("audience"))]),
            ],
            empty="No scope notes are recorded.",
        ),
        _section(
            "guidance",
            "Steps and guidance",
            eyebrow="Guide",
            blocks=[
                _list_block(
                    section_content.get("diagnostic_checks", {}).get("diagnostic_checks") or metadata.get("diagnostic_checks"),
                    title="Diagnostic checks",
                ),
                _list_block(section_content.get("mitigations", {}).get("mitigations") or metadata.get("mitigations"), title="Mitigations"),
            ],
            empty="No diagnostic or mitigation guidance is recorded.",
        ),
        _section(
            "verification",
            "Verification",
            eyebrow="Verify",
            blocks=[_paragraph_block(escalation.get("detection_notes"), title="Detection notes")],
            empty="No verification notes are recorded.",
        ),
        _section(
            "rollback",
            "Rollback and recovery",
            eyebrow="Recover",
            blocks=[_paragraph_block(section_content.get("mitigations", {}).get("permanent_fix_status") or metadata.get("permanent_fix_status"), title="Permanent fix status")],
            empty="No recovery guidance is recorded.",
        ),
        _section(
            "escalation",
            "Escalation and boundaries",
            eyebrow="Escalate",
            blocks=[
                _paragraph_block(escalation.get("escalation_threshold"), title="Escalation threshold"),
                _paragraph_block(escalation.get("evidence_notes"), title="Evidence notes"),
            ],
            empty="No escalation guidance is recorded.",
        ),
    ]


def _service_record_sections(section_content: dict[str, dict[str, Any]], metadata: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    profile = section_content.get("service_profile", {})
    operations = section_content.get("operations", {})
    return [
        _section(
            "when_to_use",
            "When to use",
            eyebrow="Read",
            blocks=[_paragraph_block(profile.get("scope_notes"), title="Scope")],
            empty="No scope notes are recorded.",
        ),
        _section(
            "scope",
            "Prerequisites and scope",
            eyebrow="Scope",
            blocks=[
                _facts_block(
                    [
                        ("Service name", profile.get("service_name") or metadata.get("service_name") or item.get("title")),
                        ("Criticality", profile.get("service_criticality") or metadata.get("service_criticality")),
                        ("Owner", item.get("owner")),
                    ]
                ),
            ],
            empty="No service scope is recorded.",
        ),
        _section(
            "guidance",
            "Steps and guidance",
            eyebrow="Guide",
            blocks=[
                _list_block(section_content.get("support_entrypoints", {}).get("support_entrypoints") or metadata.get("support_entrypoints"), title="Support entrypoints"),
                _list_block(section_content.get("dependencies", {}).get("dependencies") or metadata.get("dependencies"), title="Dependencies"),
                _list_block(section_content.get("failure_modes", {}).get("common_failure_modes") or metadata.get("common_failure_modes"), title="Failure modes"),
                _paragraph_block(operations.get("operational_notes"), title="Operational notes"),
            ],
            empty="No operational guidance is recorded.",
        ),
        _section(
            "verification",
            "Verification",
            eyebrow="Verify",
            blocks=[_paragraph_block(operations.get("evidence_notes"), title="Evidence notes")],
            empty="No verification notes are recorded.",
        ),
        _section(
            "rollback",
            "Rollback and recovery",
            eyebrow="Recover",
            blocks=[_list_block(operations.get("related_runbooks"), title="Related runbooks")],
            empty="No recovery path is recorded.",
        ),
        _section(
            "escalation",
            "Escalation and boundaries",
            eyebrow="Escalate",
            blocks=[_list_block(operations.get("related_known_errors"), title="Related known errors")],
            empty="No escalation path is recorded.",
        ),
    ]


def _policy_sections(section_content: dict[str, dict[str, Any]], metadata: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _section(
            "when_to_use",
            "When to use",
            eyebrow="Read",
            blocks=[_paragraph_block(section_content.get("policy_scope", {}).get("policy_scope") or metadata.get("policy_scope"))],
            empty="No policy scope is recorded.",
        ),
        _section(
            "scope",
            "Prerequisites and scope",
            eyebrow="Scope",
            blocks=[_facts_block([("Owner", item.get("owner")), ("Review cadence", item.get("review_cadence"))])],
            empty="No scope details are recorded.",
        ),
        _section(
            "guidance",
            "Steps and guidance",
            eyebrow="Guide",
            blocks=[_list_block(section_content.get("controls", {}).get("controls") or metadata.get("controls"), title="Controls")],
            empty="No controls are recorded.",
        ),
        _section(
            "verification",
            "Verification",
            eyebrow="Verify",
            blocks=[_paragraph_block("Confirm operators can point to the specific control they applied.")],
            empty="No verification notes are recorded.",
        ),
        _section(
            "rollback",
            "Rollback and recovery",
            eyebrow="Recover",
            blocks=[],
            empty="This policy does not define rollback actions.",
        ),
        _section(
            "escalation",
            "Escalation and boundaries",
            eyebrow="Escalate",
            blocks=[_paragraph_block(section_content.get("exceptions", {}).get("exceptions") or metadata.get("exceptions"), title="Exceptions")],
            empty="No exception handling is recorded.",
        ),
    ]


def _system_design_sections(section_content: dict[str, dict[str, Any]], metadata: dict[str, Any], item: dict[str, Any]) -> list[dict[str, Any]]:
    operations = section_content.get("operations", {})
    return [
        _section(
            "when_to_use",
            "When to use",
            eyebrow="Read",
            blocks=[_paragraph_block(section_content.get("architecture", {}).get("architecture") or metadata.get("architecture"), title="Architecture")],
            empty="No architecture overview is recorded.",
        ),
        _section(
            "scope",
            "Prerequisites and scope",
            eyebrow="Scope",
            blocks=[
                _list_block(section_content.get("dependencies", {}).get("dependencies") or metadata.get("dependencies"), title="Dependencies"),
                _list_block(section_content.get("interfaces", {}).get("interfaces") or metadata.get("interfaces"), title="Interfaces"),
            ],
            empty="No dependency or interface scope is recorded.",
        ),
        _section(
            "guidance",
            "Steps and guidance",
            eyebrow="Guide",
            blocks=[_paragraph_block(operations.get("operational_notes"), title="Operational notes")],
            empty="No operational guidance is recorded.",
        ),
        _section(
            "verification",
            "Verification",
            eyebrow="Verify",
            blocks=[_list_block(section_content.get("failure_modes", {}).get("common_failure_modes") or metadata.get("common_failure_modes"), title="Failure modes")],
            empty="No failure-mode verification notes are recorded.",
        ),
        _section(
            "rollback",
            "Rollback and recovery",
            eyebrow="Recover",
            blocks=[_list_block(operations.get("support_entrypoints") or metadata.get("support_entrypoints"), title="Support entrypoints")],
            empty="No recovery routing is recorded.",
        ),
        _section(
            "escalation",
            "Escalation and boundaries",
            eyebrow="Escalate",
            blocks=[],
            empty="No explicit escalation boundary is recorded.",
        ),
    ]


def _article_sections(
    blueprint_id: str,
    *,
    section_content: dict[str, dict[str, Any]],
    metadata: dict[str, Any],
    item: dict[str, Any],
) -> list[dict[str, Any]]:
    if blueprint_id == "runbook":
        return _runbook_sections(section_content, metadata, item)
    if blueprint_id == "known_error":
        return _known_error_sections(section_content, metadata, item)
    if blueprint_id == "service_record":
        return _service_record_sections(section_content, metadata, item)
    if blueprint_id == "policy":
        return _policy_sections(section_content, metadata, item)
    return _system_design_sections(section_content, metadata, item)


def build_article_projection(
    *,
    item: dict[str, Any],
    revision: dict[str, Any] | None,
    metadata: dict[str, Any],
    section_content: dict[str, dict[str, Any]],
    related_services: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    evidence_status: dict[str, Any],
    audit_events: list[dict[str, Any]],
    ui_projection: dict[str, Any],
    actor_id: str,
) -> dict[str, Any]:
    actor = resolve_actor(actor_id)
    article_behavior = actor.page_behavior("object-detail")
    blueprint_id = _clean_text((revision or {}).get("blueprint_id")) or _clean_text(item.get("object_type")) or "runbook"
    primary_sections = _article_sections(
        blueprint_id,
        section_content=section_content,
        metadata=metadata,
        item=item,
    )
    primary_sections.append(_service_context(related_services, item))
    all_secondary = [
        _governance_context(item, ui_projection, evidence_status),
        _evidence_context(citations, evidence_status),
        _change_context(revision, audit_events),
        _source_context(revision),
    ]
    allowed_secondary = set(article_behavior.secondary_sections if article_behavior is not None else ())
    secondary_sections = [
        section
        for section in all_secondary
        if not allowed_secondary or section["section_id"] in allowed_secondary
    ]
    return {
        "variant": actor.actor_id,
        "hero": {
            "title": item["title"],
            "summary": item["summary"],
            "eyebrow": f"{str(item['object_type']).replace('_', ' ')} · {item['object_id']}",
            "use_now": _clean_text((ui_projection.get("use_guidance") or {}).get("summary")),
        },
        "sections": primary_sections,
        "secondary_sections": secondary_sections,
        "show_context_rail": bool(article_behavior.show_context_rail) if article_behavior is not None else False,
    }
